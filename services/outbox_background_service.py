import asyncio
from email.mime import message
import json

from dataclasses import dataclass
from pydantic import Field
from uuid import UUID, uuid4

from orchestrator_sdk.callback.processing_context import ProcessingContext
from orchestrator_sdk.contracts.requests.batch_context import BatchContext
from orchestrator_sdk.data_access.message_broker.methods.api_submission import ApiSubmission
from orchestrator_sdk.seedworks.in_flight_set import InFlightSet

from typing import Any, Optional, List
from datetime import datetime, timedelta

from orchestrator_sdk.data_access.database.repositories.message_outbox_repository import MessageOutboxRepository, ReadyForSubmissionBatch
from orchestrator_sdk.data_access.database.message_database import MessageDatabase
from orchestrator_sdk.data_access.database.entities.message_outbox_entity import MessageOutboxEntity
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.seedworks.recent_success_ttl_set import RecentSuccessTtlSet
from orchestrator_sdk.seedworks.timer import Timer, TimerStats
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.seedworks.dynamic_semaphor import DynamicSemaphore

from orchestrator_sdk.data_access.database.outbox_status import OutboxStatus
from orchestrator_sdk.data_access.database.tools.pooling_utility import PoolingUtility
from requests.exceptions import ConnectionError as RequestsConnectionError

from sqlalchemy.orm import Session
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
    successful_submission: bool = False
    recent_successes:RecentSuccessTtlSet = None
    in_flight:InFlightSet = None

    pooling_utility:PoolingUtility = None
    message_database:MessageDatabase = None 
    pending_message_counts:dict = None
    batch_message_counts:dict = None

    min_cleanup_interval_in_hours:int = 2

    batch_size: int = None         # Number of messages in one batch read
    max_parallel: int = None       # Concurrent number of submissions
    semaphore: DynamicSemaphore = None

    batch_error_count: int = 0
    batch_concurrent_error_count: int = 0
    stop_concurrent_submission:bool = False
    process_count: int = 0
    use_simulator: bool = False

    def __post_init__(self):
        config_reader = ConfigReader()
        orchestrator_settings:OrchestratorConfig = config_reader.section('orchestrator', OrchestratorConfig)
        environment:str = config_reader.section('environment', str)

        env = environment.lower()
        if orchestrator_settings.use_simulator and ('prod' in env or 'live' in env):
            raise Exception('Unable to publish outbox messages as the using the simulator in live or production is not allowed. Please review the configuration.')
        else:
            self.use_simulator = orchestrator_settings.use_simulator

        self.max_parallel = orchestrator_settings.outbox.concurrency if orchestrator_settings.outbox.concurrency != None else 10
        self.batch_size = orchestrator_settings.outbox.batch_size if orchestrator_settings.outbox.batch_size != None else 50
        self.item_delay = orchestrator_settings.outbox.item_delay if orchestrator_settings.outbox.item_delay != None else 0.02
        self.long_batch_delay = orchestrator_settings.outbox.long_batch_delay if orchestrator_settings.outbox.long_batch_delay != None else 10
        self.batch_delay = orchestrator_settings.outbox.batch_delay if orchestrator_settings.outbox.batch_delay != None else 10

        # Create a real semaphore instance
        self.semaphore = DynamicSemaphore(self.max_parallel)
        self.recent_successes = RecentSuccessTtlSet(capacity=1000, ttl=timedelta(minutes=5)) 

    async def update_remaining_message_counters(self, repo:MessageOutboxRepository):
        pending_counters = repo.get_pending_message_counts()        
        self.pending_message_counts = pending_counters

    async def cleanup(self, outbox_repo: MessageOutboxRepository):  
        isolated_session = None

        try:            
            await self.pooling_utility.throttle_database_connections()
            
            isolated_session = self.message_database.db_session_maker()       
            await outbox_repo.delete_old_message_history(isolated_session)
            
            isolated_session.commit()
            self.message_database.last_cleanup_timestamp = datetime.utcnow()

        except Exception as ex:
            logger.error(f'Failed to perform outbox local db cleanup. Details: {ex}')
            if isolated_session is not None:
                isolated_session.rollback()
        
        finally:            
            if isolated_session is not None:
                isolated_session.close()

    def calculate_exponential_backoff(self, process_count:int) -> datetime:        
        delay_minutes = 2 ** (process_count * 1)
        backoff_date = datetime.utcnow() + timedelta(minutes=delay_minutes)  
        
        return backoff_date
    
    def update_message_process_fields(self, priority:Optional[int], content:str, request_date:Optional[datetime], 
        outbox_reference_id:Optional[UUID], submission_batch: Optional[BatchContext] = None) -> str:        
        if content is None:
            return content
        
        data = json.loads(content)
        
        submission_batch_key = 'SubmissionBatch'
        priority_key = 'Priority'
        request_date_key = 'RequestDate'
        outbox_reference_id_key = 'OutboxReferenceId'
        
        if (data is not None and priority_key in data):
            data[priority_key] = priority

        if (data is not None and request_date_key in data):
            data[request_date_key] = request_date.isoformat() if request_date else None

        if (data is not None and outbox_reference_id_key in data):
            data[outbox_reference_id_key] = str(outbox_reference_id) if outbox_reference_id else None

        if submission_batch is not None:
            data[submission_batch_key] = submission_batch.model_dump(mode="json")

        converted_string = json.dumps(data)        
        return converted_string
    
    def update_message_counter_on_success(self, message_id:int, message_name:str):
       
        if (self.batch_message_counts is not None and message_name in self.batch_message_counts):
            counter = self.batch_message_counts[message_name]
            self.batch_message_counts[message_name] = counter - 1
        
        self.successful_submission = True
        self.recent_successes.try_add(message_id)


    async def publish_one(
        self,
        message_id: int,
        message_name: str,
        endpoint: str,
        handler_name: str,
        priority: int,
        created_date: datetime,
        transaction_reference: str,
        group_trace_key: str,
        source_map_message_id: str,
        de_duplication_enabled: bool,
        de_duplication_delay_in_seconds: int,
        unique_header_hash: str,
        content: str,
        api_caller: ApiSubmission,
        message_batch_id: UUID,
        total_items_in_batch: int,
        position_in_batch: int,
        total_remaining_excluding_batch: int,
        oldest_remaining_item: Optional[datetime] = None
    ):
        success = False
        local_session:Session = self.message_database.db_session_maker()

        try:
            batch_context = BatchContext.Create(
                total_items_in_batch=total_items_in_batch,
                position_in_batch=position_in_batch,
                total_remaining_excluding_batch=total_remaining_excluding_batch,
                batch_id=message_batch_id,
                oldest_remaining_item=oldest_remaining_item
            )

            payload = self.update_message_process_fields(
                priority, content, created_date, message_id, submission_batch=batch_context
            )

            process_context = ProcessingContext.Create(
                source_map_message_id=source_map_message_id,
                source_priority=None,
                message_name=message_name,
                reference=transaction_reference,
                group_trace_key=group_trace_key
            )

            envelope = PublishEnvelope.Create(
                endpoint=endpoint,
                processing_context=process_context,
                publish_request=payload,
                handler_name=handler_name,
                priority=priority,
                message_name=message_name,
                de_duplication_enabled=de_duplication_enabled,
                de_duplication_delay_in_seconds=de_duplication_delay_in_seconds,
                unique_header_hash=unique_header_hash
            )

            if self.use_simulator:
                await asyncio.sleep(0.02)
            else:
                await api_caller.submit(envelope)

            db_message = local_session.query(MessageOutboxEntity).filter(
                MessageOutboxEntity.id == message_id
            ).first()

            if db_message is not None:
                db_message.process_count += 1
                db_message.status = OutboxStatus.Published.name
                db_message.is_completed = True
                db_message.published_date = datetime.utcnow()
                local_session.commit()

            self.update_message_counter_on_success(message_id=message_id, message_name=message_name)
            success = True

        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")

            if local_session is None:
                local_session = self.message_database.db_session_maker()

            db_message = local_session.query(MessageOutboxEntity).filter(
                MessageOutboxEntity.id == message_id
            ).first()

            if db_message is not None:
                db_message.process_count += 1
                db_message.status = OutboxStatus.Retry.name
                db_message.is_completed = False
                db_message.eligible_after = self.calculate_exponential_backoff(db_message.process_count)
                local_session.commit()

        finally:
            self.in_flight.try_remove(message_id)

            if local_session is not None:
                local_session.close()

            self.semaphore.release()
        
        return success


    async def run(self, stop_event: asyncio.Event, message_database:MessageDatabase) -> None:        
        self.message_database = message_database
        self.pooling_utility = PoolingUtility(logger, self.message_database.create_db_engine())
        counter = 0
        session:Session = None

        while not stop_event.is_set():
            long_wait = False
            self.in_flight = InFlightSet(capacity=20000, ttl=timedelta(minutes=5))

            try:
                self.batch_error_count = 0
                self.batch_concurrent_error_count = 0
                self.process_count = 0
                self.successful_submission = False
                last_submission_count = 0                
                
                api_caller:ApiSubmission = None
                counter += 1
                perf_stats = TimerStats(f"Outbox - Next batch #[{counter}]")
                submitted_messages:dict = dict()                

                with Timer(f"Submit messages in outbox [{counter}]", perf_stats):                    

                    with Timer("Initialization"):
                        if (session is None):
                            session = self.message_database.db_session_maker()
                        
                        if (api_caller is None):
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

                    if (session):
                        session.commit()       

                    if len(self.pending_message_counts) > 0:                        
                        
                        self.batch_message_counts = {}

                        for key, value in self.pending_message_counts.items():
                            batch_backlog = []

                            messageByType:ReadyForSubmissionBatch = await asyncio.wait_for(outbox_repo.get_next_messages(batch_size=self.batch_size, message_name=key), timeout=60)
                            batch_backlog.extend(messageByType.messages)                                         

                            if (len(batch_backlog) < self.batch_size):
                                remaining_count = self.batch_size - len(batch_backlog)

                                fillerMessages:ReadyForSubmissionBatch = await asyncio.wait_for(outbox_repo.get_next_messages(batch_size=remaining_count), timeout=60)
                                batch_backlog.extend(fillerMessages.messages)

                            backlog = []
                            seen_ids = set()

                            # De-Duplicate Batch Backlog
                            for m in batch_backlog:
                                if m.id not in seen_ids:
                                    seen_ids.add(m.id)
                                    backlog.append(m)

                            if (len(backlog) <= 0):
                                break

                            backlog.sort(key=lambda m: (m.message_name, m.created_date))

                            batch_id = None
                            items_in_batch = None
                            items_remaining_outside_batch = None
                            message_position_in_batch = 0
                            current_message = None
                            oldest_remaining_item = None

                            tasks = []

                            for message in backlog:
                                await asyncio.sleep(self.item_delay)

                                if not self.in_flight.try_add(message.id):
                                    logger.warning(f'Unable to dispatch message [{message.id}] as it is already dispatched.')
                                    continue

                                if (self.recent_successes.contains(message.id) == True):
                                    logger.warning(f'Unable to dispatch message [{message.id}] as has already been sent.')

                                    if message is not None:
                                        message.status = OutboxStatus.Published.name
                                        message.is_completed = True
                                        message.published_date = datetime.utcnow()
                                        session.commit()

                                    continue

                                await self.semaphore.acquire()
                                last_submission_count += 1

                                if message.message_name != current_message:
                                    batch_id = uuid4()
                                    current_message = message.message_name
                                    items_in_batch = sum(1 for x in backlog if x.message_name == message.message_name)
                                    self.batch_message_counts[message.message_name] = items_in_batch

                                    all_pending_messages = self.pending_message_counts[message.message_name]
                                    if all_pending_messages is not None:
                                        items_remaining_outside_batch = max(0, all_pending_messages.remaining_count - items_in_batch)
                                        oldest_remaining_item = all_pending_messages.oldest_created_date
                                    else:
                                        items_remaining_outside_batch = 0

                                    message_position_in_batch = 1
                                else:
                                    message_position_in_batch += 1

                                task = asyncio.create_task(self.publish_one(
                                    message_id=message.id,
                                    message_name=message.message_name,
                                    endpoint=message.endpoint,
                                    handler_name=message.handler_name,
                                    priority=message.priority,
                                    created_date=message.created_date,
                                    transaction_reference=message.transaction_reference,
                                    group_trace_key=message.group_trace_key,
                                    source_map_message_id=message.source_map_message_id,
                                    de_duplication_enabled=message.de_duplication_enabled,
                                    de_duplication_delay_in_seconds=message.de_duplication_delay_in_seconds,
                                    unique_header_hash=message.unique_header_hash,
                                    content=message.publish_request_object,
                                    api_caller=api_caller,
                                    message_batch_id=batch_id,
                                    total_items_in_batch=items_in_batch,
                                    position_in_batch=message_position_in_batch,
                                    total_remaining_excluding_batch=items_remaining_outside_batch,
                                    oldest_remaining_item=oldest_remaining_item
                                ))
                                tasks.append(task)

                            await self.semaphore.wait_for_all_released()
                            await asyncio.gather(*tasks, return_exceptions=True)

                    if (self.successful_submission):
                        long_wait = False                        
                    else:
                        long_wait = True                        

            except Exception as ex:

                if session is not None:
                    session.rollback()

                long_wait = True
                logger.error(ex)
            
            finally:
                if session is not None:                    
                    session.close()
                    session = None

                if (self.in_flight is not None):                
                    self.in_flight.clear()
                    self.in_flight.dispose()

            with Timer(f"Batch wait time before next"):
                if (long_wait):
                    await asyncio.sleep(self.long_batch_delay)
                else:
                    await asyncio.sleep(self.batch_delay)                 

            if (last_submission_count > 0):
                message_totals = ", ".join(f"'{k}' @ [{v}]" for k, v in submitted_messages.items())
                logger.debug(perf_stats.display_summary(message_totals))


outbox_publisher = OutboxBackgroundService()