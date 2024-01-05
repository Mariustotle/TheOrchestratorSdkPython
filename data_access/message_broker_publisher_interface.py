from abc import ABC, abstractmethod
from pydantic import BaseModel, UUID4
from typing import Optional, List
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope

class MessageBrokerPublisherInterface(ABC, BaseModel):

    @abstractmethod
    async def publish(self, publish_instruction:PublishEnvelope, transaction_reference:Optional[UUID4] = None):
        pass
        
    @abstractmethod
    async def completed(self, transaction_reference:Optional[UUID4] = None):
        pass