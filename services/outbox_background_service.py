import asyncio
import json

from dataclasses import dataclass
from pydantic import Field

from orchestrator_sdk.data_access.message_broker.methods.api_submission import ApiSubmission

from typing import Optional, List
from datetime import datetime, timedelta

from orchestrator_sdk.data_access.database.repositories.message_outbox_repository import MessageOutboxRepository, ReadyForSubmissionBatch
from orchestrator_sdk.data_access.database.message_database import MessageDatabase
from orchestrator_sdk.data_access.database.entities.message_outbox_entity import MessageOutboxEntity
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.seedworks.timer import Timer, TimerStats
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.seedworks.dynamic_semaphor import DynamicSemaphore

from orchestrator_sdk.data_access.database.outbox_status import OutboxStatus
from orchestrator_sdk.data_access.database.tools.pooling_utility import PoolingUtility
from requests.exceptions import ConnectionError as RequestsConnectionError

from orchestrator_sdk.seedworks.logger import Logger

logger = Logger.get_instance()

# ---------------------------------------------------------------------------
# Outbox publisher (runs forever in its own coroutine)
# ---------------------------------------------------------------------------
@dataclass(slots=True)
class OutboxBackgroundService:

    # Intervals in seconds    
    item_delay: float = None
    long_batch_delay: float = None
    batch_delay: float = None

    pooling_utility:PoolingUtility = None
    message_database:MessageDatabase = None 
    pending_message_counts:dict = None
    min_cleanup_interval_in_hours:int = 2

    batch_size: int = None         # Number of messages in one batch read
    max_parallel: int = None       # Concurrent number of submissions
    semaphore: DynamicSemaphore = None

    batch_error_count: int = 0
    batch_concurrent_error_count: int = 0
    stop_concurrent_submission:bool = False
    process_count: int = 0

    def __post_init__(self):
        config_reader = ConfigReader()
        orchestrator_settings:OrchestratorConfig = config_reader.section('orchestrator', OrchestratorConfig)

        self.max_parallel = orchestrator_settings.outbox.concurrency if orchestrator_settings.outbox.concurrency != None else 10
        self.batch_size = orchestrator_settings.outbox.batch_size if orchestrator_settings.outbox.batch_size != None else 50
        self.item_delay = orchestrator_settings.outbox.item_delay if orchestrator_settings.outbox.item_delay != None else 0.02
        self.long_batch_delay = orchestrator_settings.outbox.long_batch_delay if orchestrator_settings.outbox.long_batch_delay != None else 10
        self.batch_delay = orchestrator_settings.outbox.batch_delay if orchestrator_settings.outbox.batch_delay != None else 10

        # Create a real semaphore instance
        self.semaphore = DynamicSemaphore(self.max_parallel)     

            
    async def update_remaining_message_counters(self, repo:MessageOutboxRepository):
        pending_counters = repo.get_pending_message_counts()        
        self.pending_message_counts = pending_counters

    async def cleanup(self, outbox_repo: MessageOutboxRepository):  
        try:
            
            await self.pooling_utility.throttle_database_connections()
            
            isolated_session = self.message_database.db_session_maker()            
            await outbox_repo.delete_old_message_history(isolated_session)
            
            isolated_session.commit()
            self.message_database.last_cleanup_timestamp = datetime.utcnow()

        except Exception as ex:
            isolated_session.rollback()
            logger.error(f'Failed to perform outbox local db cleanup. Details: {ex}')
        
        finally:            
            isolated_session.close()

    def calculate_exponential_backoff(self, process_count:int) -> datetime:        
        delay_minutes = 2 ** (process_count * 1)
        backoff_date = datetime.utcnow() + timedelta(minutes=delay_minutes)  
        
        return backoff_date
    
    def update_message_process_fields(self, priority:Optional[int], items_at_source:Optional[int], content:str) -> str:
        
        if content == None:
            return content
        
        data = json.loads(content)
        
        priority_key = 'Priority'
        items_at_source_key = 'ItemsRemainingAtSource'
        
        if (data != None and priority_key in data):
            data[priority_key] = priority
            
        if (data != None and items_at_source_key in data):
            data[items_at_source_key] = items_at_source
            
        converted_string = json.dumps(data)        
        return converted_string
    
    def update_message_counter_on_success(self, message_name):
        
        if (self.pending_message_counts != None and message_name in self.pending_message_counts):
            counter = self.pending_message_counts[message_name]
            self.pending_message_counts[message_name] = counter - 1

    async def publish_one(self, message:MessageOutboxEntity, api_caller:ApiSubmission, content:str):
        try:
            
            items_at_source:Optional[int] = None
            if (self.pending_message_counts != None and message.message_name in self.pending_message_counts):
                items_at_source = self.pending_message_counts[message.message_name] - 1           
            
            payload = self.update_message_process_fields(message.priority, items_at_source, content)        
                                        
            envelope = PublishEnvelope.Create(
                    endpoint=message.endpoint,
                    publish_request=payload,
                    handler_name=message.handler_name,
                    source_trace_message_id=message.source_trace_message_id,
                    priority=message.priority, message_name=message.message_name,
                    de_duplication_enabled=message.de_duplication_enabled,
                    de_duplication_delay_in_seconds=message.de_duplication_delay_in_seconds,
                    unique_header_hash=message.unique_header_hash)
                
            await api_caller.submit(envelope)

            message.process_count += 1
            self.batch_concurrent_error_count = 0

            if (self.stop_concurrent_submission):
                self.stop_concurrent_submission = False
                self.semaphore.set_new_limit(self.max_parallel)
            
            message.status = OutboxStatus.Published.name
            message.is_completed = True
            message.published_date = datetime.utcnow()
                        
            self.update_message_counter_on_success(message_name=message.message_name)        

        except RequestsConnectionError:
            logger.warning(f'Unable to connect to orchestrator server to publish the messages waiting to be sent. Will delay retry.')
            logger.debug(f'MESSAGE DB POOL STATUS: [{self.message_database.db_engine.pool.status()}]')
            # Do not incriment or apply exponential backoff if a connection could not be established

            return False
            
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            logger.debug(f'MESSAGE DB POOL STATUS: [{self.message_database.db_engine.pool.status()}]')  
            
            self.batch_concurrent_error_count += 1
            self.batch_error_count += 1
            
            message.process_count += 1
            eligible_after = self.calculate_exponential_backoff(message.process_count)
            message.eligible_after = eligible_after
            
            if (self.batch_concurrent_error_count > 5 and self.stop_concurrent_submission == False):                
                self.stop_concurrent_submission = True      # Stop concurrent submission 
                self.semaphore.set_new_limit(1)
                
        finally:
            self.semaphore.release()


    async def run(self, stop_event: asyncio.Event, message_database:MessageDatabase) -> None:        
        self.message_database = message_database
        self.pooling_utility = PoolingUtility(logger, self.message_database.create_db_engine())
        counter = 0

        while not stop_event.is_set():
            session = None
            long_wait = False

            try:
                self.batch_error_count = 0
                self.batch_concurrent_error_count = 0
                self.process_count = 0
                last_submission_count = 0
                
                api_caller:ApiSubmission = None
                counter += 1
                perf_stats = TimerStats(f"Outbox - Next batch #[{counter}]")
                submitted_messages:dict = dict()

                with Timer(f"Submit messages in outbox [{counter}]", perf_stats):

                    with Timer("Initialization"):
                        if (session == None):
                            session = self.message_database.db_session_maker()
                        
                        if (api_caller == None):
                            api_caller = ApiSubmission()                 

                        outbox_repo = MessageOutboxRepository(session, None)
                        do_cleanup:bool = True if self.message_database.last_cleanup_timestamp is None or (datetime.utcnow() - self.message_database.last_cleanup_timestamp) > timedelta(hours=self.min_cleanup_interval_in_hours) else False

                    with Timer("Outbox Cleanup and De-Duplication"):
                        try:                       
                            if do_cleanup:                     
                                await asyncio.wait_for(self.cleanup(outbox_repo), timeout=120)                        

                            await asyncio.wait_for(outbox_repo.remove_duplicates_pending_submission(), timeout=30)  
                            await asyncio.wait_for(self.update_remaining_message_counters(outbox_repo), timeout=30)             
                            session.commit()
                            
                        except asyncio.TimeoutError:
                            self.pending_message_counts = None
                            logger.warning(f'Timeout while cleaning up outbox (Cleanup | Remove Duplicates)] - Not stopping, continuing with outbox processing.')                
                    
                    with Timer("Database connection throttling"):
                        await self.pooling_utility.throttle_database_connections()

                    with Timer("Get next messages from DB"):                        
                        batch_result:ReadyForSubmissionBatch = await asyncio.wait_for(outbox_repo.get_next_messages(batch_size=self.batch_size), timeout=60)

                    with Timer(f"Submit messages to Orchestrator [{len(batch_result.messages)}]"):                                            
                        # Launch publishing tasks with bounded concurrency.
                        for message in batch_result.messages:  
                            await asyncio.sleep(self.item_delay)

                            await self.semaphore.acquire()
                            last_submission_count += 1

                            asyncio.create_task(self.publish_one(message, api_caller, message.publish_request_object))

                            current_count = submitted_messages.get(message.message_name, 0)
                            submitted_messages[message.message_name] = current_count + 1                               
                        
                        try:
                            await asyncio.wait_for(self.semaphore.wait_for_all_released(), timeout=10)

                        except asyncio.TimeoutError:                            
                            logger.warning(f'Could not wait for all instances to be released.')                
                            self.semaphore = DynamicSemaphore(self.max_parallel)                        

                    if (batch_result != None and batch_result.messages_not_completed > 0 and last_submission_count > 0):
                        long_wait = False                        
                    else:
                        long_wait = True                        

                    with Timer("Save batch updates to DB"):
                        session.commit()

            except Exception as ex:
                long_wait = True
                logger.error(ex)
            
            finally:
                if session is not None:
                    session.close()  

            with Timer(f"Batch wait time before next"):
                if (long_wait):
                    await asyncio.sleep(self.long_batch_delay)
                else:
                    await asyncio.sleep(self.batch_delay)                 

            if (last_submission_count > 0):
                message_totals = ", ".join(f"'{k}' @ [{v}]" for k, v in submitted_messages.items())
                logger.debug(perf_stats.display_summary(message_totals))


outbox_publisher = OutboxBackgroundService()