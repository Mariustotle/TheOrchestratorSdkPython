from sdk.logging.logger import Logger
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.contracts.requests.application.sync_webhooks_request import SyncWebhooksRequest
from orchestrator_sdk.contracts.requests.webhooks.webhook_request import WebhookRequest
from orchestrator_sdk.contracts.endpoints import Endpoints
from orchestrator_sdk.contracts.requests.application.application_sync_request import ApplicationSyncRequest
from orchestrator_sdk.contracts.requests.events.event_publisher_registration import EventPublisherRegistration
from orchestrator_sdk.contracts.requests.events.event_subscriber_registration import EventSubscriberRegistration
from orchestrator_sdk.contracts.requests.commands.command_processor_registration import CommandProcessorRegistration
from orchestrator_sdk.contracts.requests.commands.command_raiser_registration import CommandRaiserRegistration
from orchestrator_sdk.message_processors.events.event_subscriber_base import EventSubscriberBase
from orchestrator_sdk.message_processors.events.event_publisher_base import EventPublisherBase
from orchestrator_sdk.message_processors.commands.command_processor_base import CommandProcessorBase
from orchestrator_sdk.message_processors.commands.command_raiser_base import CommandRaiserBase
from orchestrator_sdk.data_access.database.repositories.message_outbox_repository import MessageOutboxRepository

from orchestrator_sdk.data_access.database.message_database import message_database
from sqlalchemy.orm import Session
from typing import Optional, List

import requests
import json

logger = Logger.get_instance()

class SyncService():
    
    def _post(self, request, endpoint):
    
        headers = {'Content-Type': 'application/json'}      
               
        json_data = json.dumps(json.loads(request.json()))
        
        response = requests.post(endpoint, data=json_data, headers=headers, verify=False)
        
        if response.status_code != 200:
            raise Exception(f'Request failed with status code [{response.status_code}] for [{request}]. Details [{response.text}]') 
        
        return response
   

    def init(self, settings:OrchestratorConfig, endpoints:Endpoints, 
             event_subscribers:List[EventSubscriberBase] = None, event_publishers:List[EventPublisherBase] = None,
             command_raisers:List[CommandProcessorBase] = None, command_processors:List[CommandProcessorBase] = None) -> bool:

        session:Session = message_database.db_session_maker()
        is_successfull:bool = False
        
        try:
            
            repo = MessageOutboxRepository(session, None)            
            pending_message_counts = repo.get_pending_message_counts()
            
            update_webhook_endpoint = endpoints.get_sync_default_webhook_endpoint()             
            self.sync_default_webhook(update_webhook_endpoint,
                    settings.default_callback_webhook.name, 
                    settings.application_name, 
                    settings.default_callback_webhook.url, 
                    settings.default_callback_webhook.api_token)           
                 
            event_subscriptions_reg = self.build_event_subscriptions(event_subscribers) if event_subscribers != None else None
            event_publishers_reg = self.build_event_publishers(event_publishers, pending_message_counts) if event_publishers != None else None
            command_raisers_reg = self.build_command_raisers(command_raisers, pending_message_counts) if command_raisers != None else None
            command_processors_reg = self.build_command_processors(command_processors) if command_processors != None else None
            
            sync_application_message_processors_endpoint = endpoints.get_sync_application_message_processors()
            self.sync_applicaton_message_processors(
                    endpoint = sync_application_message_processors_endpoint,
                    application_name = settings.application_name,
                    event_subscribers = event_subscriptions_reg,
                    event_publishers = event_publishers_reg,
                    command_raisers = command_raisers_reg,
                    command_processors = command_processors_reg)     
            
            self.SuccessfullyInitiatlized = True
            
            is_successfull = True
            
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
        
        finally:
            session.close()
        
        return is_successfull
          
  
    
    def sync_default_webhook(self, endpoint:str, webhook_name:str, application_name:str, webhook_url:str, webhook_token:str) -> bool:
        
       	try:            
            application_webhook = WebhookRequest.Create(name=webhook_name, webhook_url=webhook_url, api_token=webhook_token)
            
            webhooks = []         
            webhooks.append(application_webhook)
            
            request = SyncWebhooksRequest.Create(application_name=application_name, webhooks=webhooks)            
           
            self._post(request, endpoint)
            
            logger.info('Default webhook details syncronized')
            return True       
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            return False
 

    def sync_applicaton_message_processors(self, endpoint:str, application_name:str, event_publishers:List[EventPublisherRegistration] = None,
                                           event_subscribers:List[EventSubscriberRegistration] = None, command_raisers:List[CommandRaiserRegistration] = None,
                                           command_processors:List[CommandRaiserRegistration] = None) -> bool:
                
       	try:            
            application_sync = ApplicationSyncRequest.Create(
                application_name=application_name, event_publishers=event_publishers, event_subscribers=event_subscribers,
                command_raisers=command_raisers, command_processors=command_processors)      
           
            response = self._post(application_sync, endpoint)
            
            event_publisher_count = len(event_publishers) if event_publishers != None else 0
            event_subscriber_count = len(event_subscribers) if event_subscribers != None else 0
            command_raiser_count = len(command_raisers) if command_raisers != None else 0
            command_processor_count = len(command_processors) if command_processors != None else 0
            
            logger.info(f'Message Proceessors Syncronized. Event Publishers [{event_publisher_count}], Event Subscribers [{event_subscriber_count}], Command Raisers [{command_raiser_count}], Command Processors [{command_processor_count}]')
            
            if response.status_code != 200:
                raise Exception(f'Request failed with status code [{response.status_code}] for [{application_name}]. Details [{response.text}]') 
            
            return True       
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            return False
    
    def build_event_publishers(self, event_publishers:List[EventPublisherBase], pending_message_counts:dict):
        publishers = []
        
        try:
            if (event_publishers == None):
                return publishers            
            
            for handler in event_publishers:
                
                items_at_source = None
                if (pending_message_counts != None and handler.event_name in pending_message_counts):
                    items_at_source = pending_message_counts[handler.event_name]
                
                publisher = EventPublisherRegistration.Create(
                    event_name = handler.event_name, 
                    latest_version = handler.latest_version,
                    processing_type=handler.processing_type,
                    json_schema = None, # Do this dynamically from the DTO
                    de_duplication_enabled = handler.de_duplication_enabled,
                    de_duplication_delay_in_minutes = handler.de_duplication_delay_in_minutes,
                    items_remaining_at_source = items_at_source,
                    max_concurrency=handler.max_concurrency_limit,
                    allow_publishing_without_subscribers = handler.allow_publishing_without_subscribers)
                
                publishers.append(publisher)                
                
            return publishers       
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            return []
    
  
    def build_event_subscriptions(self, event_subscribers:List[EventSubscriberBase]):
        subscriptions = []
        
        try:            
            if (event_subscribers == None):
                return subscriptions
              
            for handler in event_subscribers:
                subscription = EventSubscriberRegistration.Create(
                    dispatcher = handler.processor_name, 
                    event_name = handler.event_name, 
                    webhook_name = handler.process_webhook_name,
                    event_version = handler.event_version)
                
                subscriptions.append(subscription)     
                           
            return subscriptions       
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            return []


    def build_command_raisers(self, command_raisers:List[CommandRaiserBase], pending_message_counts:dict):
        raisers = []
        
        items_remaining:Optional[int] = None # Do a lookup to the outbox on the message name
        
        try:            
            if (command_raisers == None):
                return raisers            
                  
            for handler in command_raisers:
                
                items_at_source = None
                if (pending_message_counts != None and handler.command_name in pending_message_counts):
                    items_at_source = pending_message_counts[handler.command_name]
                    
                subscription = CommandRaiserRegistration.Create(
                    command_name = handler.command_name,
                    command_version = handler.command_version,
                    items_remaining_at_source=items_at_source)
                
                raisers.append(subscription)     
                           
            return raisers       
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            return []

    def build_command_processors(self, command_processors:List[CommandProcessorBase]):
        processors = []
        
        try:
            
            if command_processors == None:
                return processors
                        
            for handler in command_processors:
                subscription = CommandProcessorRegistration.Create(
                    command_name = handler.command_name,
                    webhook_name = handler.process_webhook_name,
                    procesing_type = handler.processing_type,
                    dispatcher = handler.processor_name,
                    de_duplication_enabled = handler.de_duplication_enabled,
                    de_duplication_delay_in_minutes = handler.de_duplication_delay_in_minutes,
                    json_schema = None, # Do this dynamically from the DTO
                    latest_version = handler.latest_version,
                    max_concurrency = handler.max_concurrency_limit,
                    requires_command_raiser_approval = handler.requires_command_raiser_approval)
                
                processors.append(subscription)     
                           
            return processors       
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            return []