import asyncio

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from orchestrator_sdk.data_access.database.repositories.message_outbox_repository import MessageOutboxRepository, ReadyForSubmissionBatch
from orchestrator_sdk.data_access.database.message_database import MessageDatabase
from orchestrator_sdk.data_access.database.entities.message_outbox_entity import MessageOutboxEntity
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.data_access.message_broker.methods.api_submission import ApiSubmission
from orchestrator_sdk.data_access.database.outbox_status import OutboxStatus
from requests.exceptions import ConnectionError as RequestsConnectionError

from orchestrator_sdk.seedworks.logger import Logger
logger = Logger.get_instance()

class LocalOutboxService:
    
    lock = asyncio.Lock()
    is_busy:bool = False
    message_database:MessageDatabase = None    
    remaining_count:Optional[int] = None
    
    BATCH_SIZE:int = 80
    BATCH_WAIT_TIME_IN_SECONDS:int = 30
    SLACK_MARKER:int = 20
    SLACK_WAIT_TIME_IN_SECONDS:int = 0.5
    CONCURENT_LIMIT:int = 10
    
    RETENTION_TIME_IN_DAYS:int = 3
    
    def __init__(self, message_database:MessageDatabase): 
        self.is_busy = False
        self.message_database = message_database
        
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
            
    async def process_item(self, session:Session, submitter:ApiSubmission, message:MessageOutboxEntity, content:str) -> bool: 
        try:
                message.process_count += 1                            
                envelope = PublishEnvelope.Create(
                        endpoint=message.endpoint,
                        publish_request=content,
                        handler_name=message.handler_name,
                        source_trace_message_id=message.source_trace_message_id,
                        priority=message.priority, message_name=message.message_name,
                        de_duplication_enabled=message.de_duplication_enabled,
                        unique_header_hash=message.unique_header_hash)
                    
                await submitter.submit(envelope)
            
                message.status = OutboxStatus.Published.name
                message.is_completed = True
                message.published_date = datetime.utcnow()
                session.commit()                                   

                return True
        
        except RequestsConnectionError:
                logger.warn(f'Unable to connect to orchestrator server to publish the messages waiting to be sent. Will delay retry.')
                logger.info(f'MESSAGE DB POOL STATUS: [{self.message_database.db_engine.pool.status()}]')
                session.rollback()
                return False
            
        except Exception as ex:
                logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
                logger.info(f'MESSAGE DB POOL STATUS: [{self.message_database.db_engine.pool.status()}]')
                session.rollback()
                raise   
   
    async def process_all(self, messages, session:Session, api_submission:ApiSubmission) -> int:

        # Create a list of coroutine objects by calling the process function on each item
        tasks = [self.process_item(session, api_submission, message, message.publish_request_object) for message in messages]

        # Wait for all tasks to complete and gather their results
        results = await asyncio.gather(*tasks)        
        successes = sum(results)
        
        return successes   
   
    async def process_next_batch(self):
                
        previous_batch_remaining = self.remaining_count
        
        remaining:int = None
        ready:int = None
        api_submission = ApiSubmission()
        add_extra_delay = True
        success_count = 0
        slack_count = 0
        error_occurred = False
        
        with self.message_database.db_session_maker() as session:
        
            try:           
                outbox_repo = MessageOutboxRepository(session, None)     
                
                await outbox_repo.remove_duplicates_pending_submission()      
                batch_result:ReadyForSubmissionBatch = await outbox_repo.get_next_messages(batch_size=self.BATCH_SIZE)               
                logger.info(f'OUTBOX Queue Summary >>>> Remaining [{len(batch_result.messages)}/{batch_result.messages_not_completed}] Ready [{batch_result.messages_ready}] Intervention [{batch_result.messages_needing_intervention}] <<<<')
                
                self.remaining_count = batch_result.messages_not_completed
                remaining = self.remaining_count
                ready = batch_result.messages_ready
                
                
                while (len(batch_result.messages) > 0):
                    concurrent_subset = [batch_result.messages.pop() for _ in range(min(self.CONCURENT_LIMIT, len(batch_result.messages)))]
                    successes = await self.process_all(concurrent_subset, session, api_submission)
                    
                    success_count += successes        
                    slack_count += successes
                
                    if slack_count >= self.SLACK_MARKER:
                        await asyncio.sleep(self.SLACK_WAIT_TIME_IN_SECONDS)
                        slack_count = 0

                    if (successes == 0):
                        error_occurred = True
                        break                                            
                    
            except Exception as ex:     
                logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
                logger.info(f'MESSAGE DB POOL STATUS: [{self.message_database.db_engine.pool.status()}]')
                session.rollback()
                
            finally:
                
                if (remaining != None and (remaining - success_count) <= 0):                
                    return
                
                error_occured = remaining == None or ready == None or error_occurred == True
                no_remaining_items_are_ready = True if remaining != None and ready != None and ready == 0 else False
                previous_batch_did_not_publish = previous_batch_remaining != None and remaining == previous_batch_remaining
                add_extra_delay = error_occured or no_remaining_items_are_ready or previous_batch_did_not_publish                
                
        delay:int = self.BATCH_WAIT_TIME_IN_SECONDS if add_extra_delay else 1
        await asyncio.sleep(delay)
        
        asyncio.create_task(self.process_next_batch())

            
    async def cleanup(self, session):  
        # Removed in its own context, non-blocking to original query
       
        repo = MessageOutboxRepository(session, None)
        await repo.delete_old_message_history(self.RETENTION_TIME_IN_DAYS)
        
        session.commit()

