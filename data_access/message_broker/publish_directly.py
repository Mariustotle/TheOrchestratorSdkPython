from typing import Optional

from orchestrator_sdk.data_access.message_broker.message_broker_publisher_interface import MessageBrokerPublisherInterface
from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork
from orchestrator_sdk.data_access.message_broker.methods.api_submission import ApiSubmission

class PublishDirectly(MessageBrokerPublisherInterface):

    async def publish(self, publish_request:PublishEnvelope, unit_of_work:Optional[UnitOfWork] = None):        
        method = ApiSubmission()
        method.submit(publish_request)



