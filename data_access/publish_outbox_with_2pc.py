from pydantic import UUID4
from typing import Optional, List
from seedworks.logger import Logger
from orchestrator_sdk.data_access.message_broker_publisher_interface import MessageBrokerPublisherInterface
from orchestrator_sdk.contracts.types.process_structure import ProcessStructure
from orchestrator_sdk.contracts.requests.commands.concurrent_command_request import ConcurrentCommandRequest
from orchestrator_sdk.contracts.requests.commands.queue_command_request import QueueCommandRequest
from orchestrator_sdk.contracts.requests.events.publish_event_request import PublishEventRequest
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.callback_context import CallbackContext


import requests
import json

logger = Logger.get_instance()

class PublishOutboxWith2PC(MessageBrokerPublisherInterface):
    
    async def publish(self, publish_instruction:PublishEnvelope, transaction_reference:Optional[UUID4] = None):
        try:                   
                       
            if transaction_reference == None and not CallbackContext.is_available():
                raise Exception(f"To use OutboxWith2PC you have to have an interaction reference. This can be populated dynamically from a callback or must be done manually in the UnitOfWork imlimentation and passed through as a parameter.")

            transaction_number:UUID4 = transaction_reference if transaction_reference is not None else CallbackContext.callback_reference.get()     

            # Save to local SQLLite database with status Pending with the [transaction_number] above
            
            pass            
        except Exception as ex:
            
            logger.error(ex)            
            raise

    async def completed(self, transaction_reference:Optional[UUID4] = None):
        
        transaction_number:UUID4 = transaction_reference if transaction_reference is not None else CallbackContext.callback_reference.get()
        
        # Update all the pending messages with the above transaction number and set their status to [Ready]
        
        '''
        CheckForUnsubmittedMessages (Start() and completed())
        |_ ProcessUnsubmittedMessages (Background Process - Can only be one - Runs until there are no messages with status Ready - Ignore Elegibility)
          |_ ProcessNextBatch (Get a list of Ready and Eligible message and process them)
        
        '''
        
        # If [CheckForLocalUnsubmittedMessages] background process is not running, start it   
        
        pass
