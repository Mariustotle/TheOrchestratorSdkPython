from orchestrator_sdk.message_processors.events.event_subscriber_base import EventSubscriberBase
from orchestrator_sdk.testing.unit_testing.process_context_builder import ProcessContextBuilder
from orchestrator_sdk.seedworks.logger import Logger

logger = Logger.get_instance()

class EventSubscriberTestHarness:

    subscriber: EventSubscriberBase
    process_context_builder: ProcessContextBuilder

    def __init__(self, subscriber:EventSubscriberBase):
        self.subscriber = subscriber
        self.process_context_builder = ProcessContextBuilder(message_name=self.subscriber.event_name)

    async def process(self, callback_message):

        try:
            if (type(callback_message) != self.subscriber.request_type):
                raise Exception(f'Canot intiate subscriber [{type(self.subscriber)}] with [{type(callback_message)}] expecting [{self.subscriber.request_type}]')

            process_context = self.process_context_builder.build()
            return await self.subscriber._process(
                request=callback_message, 
                context=process_context, 
                unit_of_work=None)
        
        except Exception as ex:
            logger.error(f"Oops! {ex.__class__} occurred. Details: {ex}")



    

