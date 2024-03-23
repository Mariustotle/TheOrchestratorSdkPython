from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.contracts.requests.application.sync_webhooks_request import SyncWebhooksRequest
from orchestrator_sdk.contracts.requests.webhooks.webhook_request import WebhookRequest
from orchestrator_sdk.contracts.endpoints import Endpoints
from orchestrator_sdk.contracts.requests.application.application_sync_request import ApplicationSyncRequest
from orchestrator_sdk.contracts.requests.events.event_publisher_registration import EventPublisherRegistration
from orchestrator_sdk.contracts.requests.events.event_subscriber_registration import EventSubscriberRegistration
from orchestrator_sdk.handlers.event_handlers.event_subscriber_base import EventSubscriberBase
from orchestrator_sdk.handlers.event_handlers.event_publisher_base import EventPublisherBase
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
             event_subscribers:List[EventSubscriberBase], event_publishers:List[EventPublisherBase]) -> bool:
       
        try:            
            self.associate_application()
            
            update_webhook_endpoint = endpoints.get_sync_default_webhook_endpoint()             
            self.sync_default_webhook(update_webhook_endpoint,
                    settings.default_callback_webhook.name, 
                    settings.application_name, 
                    settings.default_callback_webhook.url, 
                    settings.default_callback_webhook.api_token)           
                 
            event_subscriptions = self.build_event_subscriptions(event_subscribers)        
            event_publishers = self.build_event_publishers(event_publishers)
            
            sync_application_message_processors_endpoint = endpoints.get_sync_application_message_processors()
            self.sync_applicaton_message_processors(
                    endpoint=sync_application_message_processors_endpoint,
                    application_name=settings.application_name,
                    event_subscribers=event_subscriptions,
                    event_publishers=event_publishers)     
            
            self.SuccessfullyInitiatlized = True
            
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            
            return False
    
    def associate_application(self):
        print('Application Registered')
    
    
    def sync_default_webhook(self, endpoint:str, webhook_name:str, application_name:str, webhook_url:str, webhook_token:str) -> bool:
        
       	try:            
            application_webhook = WebhookRequest().Create(name=webhook_name, webhook_url=webhook_url, api_token=webhook_token)
            
            webhooks = []         
            webhooks.append(application_webhook)
            
            request = SyncWebhooksRequest().Create(application_name=application_name, webhooks=webhooks)            
           
            self._post(request, endpoint)
            
            logger.info('Default webhook details syncronized')
            return True       
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            return False
 
        

    def sync_applicaton_message_processors(self, endpoint:str, application_name:str, event_publishers:List[EventPublisherRegistration],
                                           event_subscribers:List[EventSubscriberRegistration]) -> bool:
        
       	try:            
            application_sync = ApplicationSyncRequest.Create(
                application_name=application_name, event_publishers=event_publishers, event_subscribers=event_subscribers)      
           
            response = self._post(application_sync, endpoint)
            
            eventPublisherCount = len(event_publishers) if event_publishers != None else 0
            eventSubscriberCount = len(event_subscribers) if event_subscribers != None else 0
            
            logger.info(f'Message Proceessors Syncronized. Event Publishers [{eventPublisherCount}], Event Subscribers [{eventSubscriberCount}], Command Raisers [{0}], Command Processors [{0}]')
            
            if response.status_code != 200:
                raise Exception(f'Request failed with status code [{response.status_code}] for [{application_name}]. Details [{response.text}]') 
            
            return True       
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            return False
    
  
    def build_event_subscriptions(self, event_subscribers:List[EventSubscriberBase]):
        subscriptions = []
        
        try:            
                        
            for handler in event_subscribers:
                subscription = EventSubscriberRegistration.Create(
                    dispatcher=handler.processor_name, 
                    event_name=handler.event_name, 
                    webhook_name=handler.process_webhook_name,
                    event_version=handler.request_version)
                subscriptions.append(subscription)     
                           
            return subscriptions       
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            return []
        
    def build_event_publishers(self, event_publishers:List[EventPublisherBase]):
        publishers = []
        
        try:            
            
            for handler in event_publishers:
                publisher = EventPublisherRegistration.Create(
                    event_name=handler.event_name, 
                    processing_type=handler.processing_type,
                    jason_schema=None, # Do this dynamically from the DTO
                    latest_version=handler.request_version)
                
                publishers.append(publisher)                
                
            return publishers       
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            return []
