from abc import ABC, abstractmethod
from pydantic import BaseModel
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope

class MessageBrokerPublisherInterface(ABC, BaseModel):

    @abstractmethod
    async def submit(self, publish_instruction:PublishEnvelope):
        pass
