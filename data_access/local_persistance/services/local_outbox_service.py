from asyncio import Lock
import asyncio
from sqlalchemy.orm import Session
from typing import Optional

from orchestrator_sdk.data_access.local_persistance.repositories.message_outbox_repository import MessageOutboxRepository
from orchestrator_sdk.data_access.local_persistance.repositories.message_outbox_repository import ReadyForSubmissionBatch
from orchestrator_sdk.data_access.local_persistance.local_database import LocalDatabase
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.data_access.message_broker.methods.api_submission import ApiSubmission
from orchestrator_sdk.data_access.local_persistance.outbox_status import OutboxStatus

class LocalOutboxService:
    
    is_busy:bool = None
    session:Session = None
    local_database:LocalDatabase = None
    lock:object = None
    
    remaining_count:Optional[int] = None
    
    WAIT_TIME_IN_SECONDS:int = 30
    BATCH_SIZE:int = 20
    RETENTION_TIME_IN_DAYS:int = 30
    
    def __init__(self, local_database:LocalDatabase): 
        self.is_busy = False
        self.lock = Lock()
        self.local_database = local_database
        
    async def check_for_messages_that_are_ready(self):
        
        async with self.lock:
            if self.is_busy:
                return
            self.is_busy = True
        
        self.remaining_count = None
        self.session = self.local_database.db_session_maker()
        await asyncio.create_task(self.process_next_batch())
    
    async def process_next_batch(self):
        
        previous_batch_remaining = self.remaining_count
        
        remaining:int = None
        ready:int = None
        api_submission = ApiSubmission()
        
        try:           
           outbox_repo = MessageOutboxRepository(self.session, None)           
           batch_result:ReadyForSubmissionBatch = await outbox_repo.get_next_messages(batch_size=self.BATCH_SIZE)
           
           self.remaining_count = batch_result.messages_not_completed
           remaining = self.remaining_count
           ready = batch_result.messages_ready
           
           for message in batch_result.messages:
               publish_request = message.publish_request_object
               
               envelope = PublishEnvelope().Create(
                    endpoint=message.endpoint,
                    publish_request=publish_request,
                    handler_name=message.handler_name,
                    source_message_id=message.source_message_id,
                    group_trace_key=message.group_trace_key)
               
               try:                   
                   await api_submission.submit(envelope)
                   
                   message.status = OutboxStatus.Published.name
                   message.is_completed = True
                   self.session.commit()                         
                   
               except Exception as ex:            
                    print(f"Oops! {ex.__class__} occurred. Details: {ex}")  
                
        except Exception as ex:            
            print(f"Oops! {ex.__class__} occurred. Details: {ex}")  
            
        finally:
            
            if remaining == 0:                
                async with self.lock:
                    await self.cleanup()                
                    self.is_busy = False
                    return
            
            error_occured = remaining == None or ready == None
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
