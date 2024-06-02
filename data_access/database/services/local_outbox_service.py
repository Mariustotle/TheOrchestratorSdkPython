import asyncio
import json

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from orchestrator_sdk.data_access.database.repositories.message_outbox_repository import MessageOutboxRepository, ReadyForSubmissionBatch
from orchestrator_sdk.data_access.database.message_database import MessageDatabase
from orchestrator_sdk.data_access.database.entities.message_outbox_entity import MessageOutboxEntity
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.data_access.message_broker.methods.api_submission import ApiSubmission
from orchestrator_sdk.data_access.database.outbox_status import OutboxStatus
from orchestrator_sdk.data_access.database.tools.pooling_utility import PoolingUtility
from requests.exceptions import ConnectionError as RequestsConnectionError

from orchestrator_sdk.seedworks.logger import Logger

logger = Logger.get_instance()

class LocalOutboxService:
    
    lock = asyncio.Lock()
    is_busy:bool = False
    message_database:MessageDatabase = None    
    remaining_count:Optional[int] = None    
    min_cleanup_interval_in_hours:int = 1
    pending_message_counts:dict = None    
    pooling_utility:PoolingUtility = None
    
    BATCH_SIZE:int = 80
    BATCH_WAIT_TIME_IN_SECONDS:int = 60
    SLACK_MARKER:int = 20
    SLACK_WAIT_TIME_IN_SECONDS:int = 1
    CONCURENT_LIMIT:int = 10
    MESSAGE_DELAY_ON_FAILURE_IN_MINUTES:int = 5
    
    def __init__(self, message_database:MessageDatabase): 
        self.is_busy = False
        self.message_database = message_database
        self.pooling_utility = PoolingUtility(logger, self.message_database.db_engine)
        
    def update_message_counter_on_success(self, message_name):
        
        if (self.pending_message_counts != None and message_name in self.pending_message_counts):
            counter = self.pending_message_counts[message_name]
            self.pending_message_counts[message_name] = counter - 1
            
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
        return  converted_string       
        
        
    async def update_remaining_message_counters(self, repo:MessageOutboxRepository):
        pending_counters = repo.get_pending_message_counts()        
        self.pending_message_counts = pending_counters      
        
    async def check_for_messages_that_are_ready(self):         
        
        async with LocalOutboxService.lock:            
            if LocalOutboxService.is_busy:
                return
            LocalOutboxService.is_busy = True           

        try:           
            self.remaining_count = None
            
            await asyncio.sleep(5)
            await asyncio.create_task(self.process_next_batch())
                        
        except Exception as ex:
            logger.error("Failed to process next batch of outbox items", ex)
        
        async with LocalOutboxService.lock: 
            LocalOutboxService.is_busy = False
            
    async def process_item(self, submitter:ApiSubmission, message:MessageOutboxEntity, content:str) -> bool: 
        try:
            
            items_at_source:Optional[int] = None
            if (self.pending_message_counts != None and message.message_name in self.pending_message_counts):
                items_at_source = self.pending_message_counts[message.message_name] - 1           
            
            payload = self.update_message_process_fields(message.priority, items_at_source, content)
        
            message.process_count += 1                            
            envelope = PublishEnvelope.Create(
                    endpoint=message.endpoint,
                    publish_request=payload,
                    handler_name=message.handler_name,
                    source_trace_message_id=message.source_trace_message_id,
                    priority=message.priority, message_name=message.message_name,
                    de_duplication_enabled=message.de_duplication_enabled,
                    de_duplication_delay_in_seconds=message.de_duplication_delay_in_seconds,
                    unique_header_hash=message.unique_header_hash)
                
            await submitter.submit(envelope)
        
            message.status = OutboxStatus.Published.name
            message.is_completed = True
            message.published_date = datetime.utcnow()
                        
            self.update_message_counter_on_success(message_name=message.message_name)           

            return True
        
        except RequestsConnectionError:
            logger.warn(f'Unable to connect to orchestrator server to publish the messages waiting to be sent. Will delay retry.')
            logger.info(f'MESSAGE DB POOL STATUS: [{self.message_database.db_engine.pool.status()}]')           

            return False
            
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            logger.info(f'MESSAGE DB POOL STATUS: [{self.message_database.db_engine.pool.status()}]')
            
            delay_period = timedelta(minutes=self.MESSAGE_DELAY_ON_FAILURE_IN_MINUTES)
            eligible_after = datetime.utcnow() + delay_period            
            message.eligible_after = eligible_after            
        
            return False
   
    async def process_concurrent_batch(self, messages, api_submission:ApiSubmission) -> int:

        # Create a list of coroutine objects by calling the process function on each item
        tasks = [self.process_item(api_submission, message, message.publish_request_object) for message in messages]

        # Wait for all tasks to complete and gather their results
        results = await asyncio.gather(*tasks)
        
        successes = sum(results)        
        return successes   

   
    async def process_next_batch(self):
        
        delay_next_request = False
        another_batch = True
        error_occured = False
        
        try:
            
            previous_batch_remaining = self.remaining_count        
            remaining:int = None
            ready:int = None
            api_submission = ApiSubmission()
            success_count = 0
            slack_count = 0
            error_occurred = False       
            batch_size_at_start = 0     
            
            session = self.message_database.db_session_maker()
             
            outbox_repo = MessageOutboxRepository(session, None)
            do_cleanup:bool = True if self.message_database.last_cleanup_timestamp is None or (datetime.utcnow() - self.message_database.last_cleanup_timestamp) > timedelta(hours=self.min_cleanup_interval_in_hours) else False
           
            try:                       
                if do_cleanup:
                    await asyncio.wait_for(self.cleanup(outbox_repo), timeout=120)
                    
                await asyncio.wait_for(outbox_repo.remove_duplicates_pending_submission(), timeout=30)  
                await asyncio.wait_for(self.update_remaining_message_counters(outbox_repo), timeout=30)             
                session.commit()
                
            except asyncio.TimeoutError:
                self.pending_message_counts = None
                logger.warn(f'Timeout while cleaning up outbox (Cleanup | Remove Duplicates)] - Not stopping, continuing with outbox processing.')                
                
            await self.pooling_utility.throttle_database_connections()
                
            batch_result:ReadyForSubmissionBatch = await asyncio.wait_for(outbox_repo.get_next_messages(batch_size=self.BATCH_SIZE), timeout=60) 
            
            if (batch_result == None or batch_result.messages_not_completed <= 0):
                another_batch = False
                
            else:
                logger.info(f'OUTBOX Queue Summary >>>> Remaining [{len(batch_result.messages)}/{batch_result.messages_not_completed}] Ready [{batch_result.messages_ready}] Intervention [{batch_result.messages_needing_intervention}] <<<<')
                
                self.remaining_count = batch_result.messages_not_completed
                remaining = self.remaining_count
                ready = batch_result.messages_ready                
                
                batch_size_at_start = len(batch_result.messages)                                
                
                while (len(batch_result.messages) > 0):
                    
                    await self.pooling_utility.throttle_database_connections()
                    
                    batch_size = min(self.CONCURENT_LIMIT, len(batch_result.messages))
                    concurrent_subset = [batch_result.messages.pop() for _ in range(batch_size)]
                    successes = await self.process_concurrent_batch(concurrent_subset, api_submission)
                    
                    session.commit()
                    
                    success_count += successes        
                    slack_count += successes
                
                    if slack_count >= self.SLACK_MARKER:
                        await asyncio.sleep(self.SLACK_WAIT_TIME_IN_SECONDS)
                        slack_count = 0

                    if (batch_size > 0 and successes < batch_size):
                        error_occurred = True
                        break              

                if (remaining != None and (remaining - success_count) <= 0):                
                    another_batch = False                
                
                error_occured = remaining == None or ready == None or error_occurred == True
                something_went_wrong_previously = previous_batch_remaining != None and remaining == previous_batch_remaining                
                no_remaining_items_are_ready = True if remaining != None and ready != None and ready == 0 else False
                
                delay_next_request = error_occured or something_went_wrong_previously or no_remaining_items_are_ready
       
        except Exception as ex:     
                logger.error(f"Oops! {ex.__class__} process_next_batch: {ex}")
                logger.info(f'MESSAGE DB POOL STATUS: [{self.message_database.db_engine.pool.status()}]')
                delay_next_request, error_occured = True
                
        finally:
            
            session.close()
            
            if (success_count > batch_size_at_start):
                logger.warn(f"More mesages submitted [{success_count}] than there where messages in the batch [{batch_size_at_start}]. This could indicate duplicate submissions.")
            
            
            if (delay_next_request):
                if (error_occured):
                    logger.warn(f'Error occured trying to submit a batch of messages to server. Delaying next batch submission with [{self.BATCH_WAIT_TIME_IN_SECONDS}]s.')
                
                await asyncio.sleep(self.BATCH_WAIT_TIME_IN_SECONDS)
            
            else:
                 asyncio.sleep(1)                      
           
            if (another_batch):
                await asyncio.create_task(self.process_next_batch())            

            
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