from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional

from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork

class MessageBrokerPublisherInterface(ABC, BaseModel):

    @abstractmethod
    async def publish(self, publish_instruction:PublishEnvelope, unit_of_work:Optional[UnitOfWork] = None):
        pass
