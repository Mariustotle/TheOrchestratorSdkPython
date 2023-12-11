
class Endpoints():
    
    _base_url:str = None    

    def __init__(self, base_url:str) -> None:
        self._base_url = base_url
    
    def get_sync_default_webhook_endpoint(self) -> str:
        return f'{self._base_url}/Application/SyncApplicationWebhooks'
    
    def get_sync_event_subscriptions(self) -> str:
        return f'{self._base_url}/Application/SyncApplicationEventSubscriptions'
    
    def get_sync_event_publishers(self) -> str:
        return f'{self._base_url}/Application/SyncApplicationEventPublishers'