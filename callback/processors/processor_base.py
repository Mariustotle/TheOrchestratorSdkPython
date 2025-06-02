from abc import ABC, abstractmethod ## abstract module
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork
from orchestrator_sdk.services.idempotence_service import IdempotenceService
from orchestrator_sdk.seedworks.json_worker import JsonWorker
from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.callback.header_properties import HeaderProperties
from orchestrator_sdk.callback.processing_context import ProcessingContext

import json

logger = Logger.get_instance()

class ProcessorBase(ABC):	
	application_name:str = None
	idempotence_service: IdempotenceService = None
	json_worker:JsonWorker = None

	@abstractmethod
	def get_header_properties(self, headers:HeaderProperties) -> object: pass

	@abstractmethod
	def get_processing_context(self, headers) -> ProcessingContext: pass

	@abstractmethod
	async def process_specific(self, json_content, callback, headers, processing_context, unit_of_work:UnitOfWork) -> object: pass


	def load_json_payload(self, json_string) -> object:
		json_object = None

		try:
			json_object = json.loads(json_string)

		except json.JSONDecodeError:
			raise Exception(f'Unable to process callback message as the the body is not JSON format [{json_string}]')	

		return json_object
	
	async def process(self, callback_event, all_headers:HeaderProperties, unit_of_work:UnitOfWork):
		specific_headers = self.get_header_properties(all_headers)
		processing_context = self.get_processing_context(specific_headers)

		json_content = self.load_json_payload(callback_event.JsonPayload)		

		if unit_of_work is not None:           
			already_processed:bool = await self.idempotence_service.has_message_been_processed(message_id=all_headers.message_id, unit_of_work=unit_of_work)
			if already_processed:
				logger.warning(f'Idempotence check: Message [{all_headers.message_id}] have already been processed, skipping this request.')
				return # Our work here is done
        
		response = await self.process_specific(json_content=json_content, callback=callback_event, 
			headers=specific_headers, processing_context=processing_context, unit_of_work=unit_of_work)
		
		if unit_of_work is not None: 
			await unit_of_work.message_history_repository.add_message(all_headers.message_id)
			unit_of_work.message_session.commit()

		return response		
		

	def __init__(self, application_name:str):
		self.application_name = application_name
		self.idempotence_service = IdempotenceService()
		self.json_worker = JsonWorker()

