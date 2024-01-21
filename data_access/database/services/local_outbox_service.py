from asyncio import Lock
import asyncio
from sqlalchemy.orm import Session
from typing import Optional

from orchestrator_sdk.data_access.database.repositories.message_outbox_repository import MessageOutboxRepository, ReadyForSubmissionBatch
from orchestrator_sdk.data_access.database.message_database import MessageDatabase
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.data_access.message_broker.methods.api_submission import ApiSubmission
from orchestrator_sdk.data_access.database.outbox_status import OutboxStatus
from requests.exceptions import ConnectionError as RequestsConnectionError


from orchestrator_sdk.seedworks.logger import Logger
logger = Logger.get_instance()

class LocalOutboxService:
    
    is_busy:bool = None
    session:Session = None
    message_database:MessageDatabase = None
    lock:object = None
    
    remaining_count:Optional[int] = None
    
    WAIT_TIME_IN_SECONDS:int = 30
    BATCH_SIZE:int = 20
    RETENTION_TIME_IN_DAYS:int = 30
    
    def __init__(self, message_database:MessageDatabase): 
        self.is_busy = False
        self.lock = Lock()
        self.message_database = message_database
        
    async def check_for_messages_that_are_ready(self):
        
        async with self.lock:
            if self.is_busy:
                return
            self.is_busy = True
        
        self.remaining_count = None
        self.session = self.message_database.db_session_maker()
        await asyncio.create_task(self.process_next_batch())
    
    async def process_next_batch(self):
        
        previous_batch_remaining = self.remaining_count
        
        remaining:int = None
        ready:int = None
        api_submission = ApiSubmission()
        error_occurred = False
        
        try:           
           outbox_repo = MessageOutboxRepository(self.session, None)           
           batch_result:ReadyForSubmissionBatch = await outbox_repo.get_next_messages(batch_size=self.BATCH_SIZE)
           
           if (batch_result.messages_not_completed > 0):
                logger.info(f'Batch Processing Summary >>>> Remaining [{len(batch_result.messages)}/{batch_result.messages_not_completed}] Ready [{batch_result.messages_ready}] Intervention [{batch_result.messages_needing_intervention}] <<<<')
           
           self.remaining_count = batch_result.messages_not_completed
           remaining = self.remaining_count
           ready = batch_result.messages_ready
           
           for message in batch_result.messages:
               publish_request = message.publish_request_object
               
               try:           
                   
                    envelope = PublishEnvelope().Create(
                            endpoint=message.endpoint,
                            publish_request=publish_request,
                            handler_name=message.handler_name,
                            source_message_id=message.source_message_id,
                            group_trace_key=message.group_trace_key,
                            priority=message.priority)
                           
                    await api_submission.submit(envelope)
                   
                    message.status = OutboxStatus.Published.name
                    message.is_completed = True
                    self.session.commit()
            
               except RequestsConnectionError:
                    error_occurred = True
                    logger.warn(f'Unable to connect to orchestrator server to publish the [{len(batch_result.messages)}] messages waiting to be sent. Will delay retry.')
                    break
                   
               except Exception as ex:
                    error_occurred = True        
                    logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")  
                
        except Exception as ex:            
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            error_occurred = True
            
        finally:
            
            if remaining == 0:                
                async with self.lock:
                    await self.cleanup()                
                    self.is_busy = False
                    return
            
            error_occured = remaining == None or ready == None or error_occurred == True
            no_remaining_items_are_ready = True if remaining != None and remaining > 0 and ready != None and ready == 0 else False
            previous_batch_did_not_publish = previous_batch_remaining != None and remaining == previous_batch_remaining
            add_extra_delay = error_occured or no_remaining_items_are_ready or previous_batch_did_not_publish
            
            delay:int = self.WAIT_TIME_IN_SECONDS if add_extra_delay else 1
            await asyncio.sleep(delay)
            
            asyncio.create_task(self.process_next_batch())

            
    async def cleanup(self):  
        # Removed in its own context, non-blocking to original query
       
        repo = MessageOutboxRepository(self.session, None)
        await repo.delete_old_message_history(self.RETENTION_TIME_IN_DAYS)
        
        self.session.commit()
        self.session.close()  
