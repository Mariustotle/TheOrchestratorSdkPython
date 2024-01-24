from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.contracts.orchestrator_config import OrchestratorConfig
from orchestrator_sdk.contracts.requests.application.sync_webhooks_request import SyncWebhooksRequest
from orchestrator_sdk.contracts.requests.webhooks.webhook_request import WebhookRequest
from orchestrator_sdk.contracts.endpoints import Endpoints
from orchestrator_sdk.contracts.requests.events.publisher_request import PublisherRequest
from orchestrator_sdk.contracts.requests.events.subscriber_request import SubscriberRequest
from orchestrator_sdk.contracts.requests.application.sync_event_subscriptions import SyncEventSubscription
from orchestrator_sdk.contracts.requests.application.sync_event_publishers import SyncEventPublishers
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
            
            sync_event_subscriptions_endpoint = endpoints.get_sync_event_subscriptions()            
            self.sync_event_subscriptions(settings.application_name,
                    sync_event_subscriptions_endpoint,
                    event_subscribers)
            
            sync_event_publishers_endpoint = endpoints.get_sync_event_publishers()            
            self.sync_event_publishers(settings.application_name,
                    sync_event_publishers_endpoint,
                    event_publishers)            
            
            self.SuccessfullyInitiatlized = True
            
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")   
    
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
        
   
    def sync_event_subscriptions(self, application_name:str, endpoint:str, event_subscribers:List[EventSubscriberBase]):
        try:            
            subscriptions = []
            
            for handler in event_subscribers:
                subscription = SubscriberRequest().Create(
                    dispatcher=handler.processor_name, 
                    event_name=handler.event_name, 
                    webhook_name=handler.process_webhook_name,
                    event_version=handler.request_version)
                subscriptions.append(subscription)                
                
            sync_request = SyncEventSubscription().Create(application_name=application_name, subscriptions=subscriptions)
            
            self._post(sync_request, endpoint)
            
            logger.info('Event Subscriptions Syncronized')
            return True       
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            return False
        
    def sync_event_publishers(self, application_name:str, endpoint:str, event_publishers:List[EventPublisherBase]):
        try:            
            publishers = []
            
            for handler in event_publishers:
                publisher = PublisherRequest().Create(
                    event_name=handler.event_name, 
                    jason_schema=None, # Do this dynamically from the DTO
                    latest_version=handler.request_version)
                
                publishers.append(publisher)                
                
            sync_request = SyncEventPublishers().Create(application_name=application_name, publishers=publishers)
            
            self._post(sync_request, endpoint)
            
            logger.info('Event Publishers Syncronized')
            return True       
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")
            return False
