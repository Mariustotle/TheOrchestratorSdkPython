from fastapi import APIRouter, HTTPException, Request, Depends, Body
from fastapi.responses import JSONResponse
from typing import Union
from pydantic import Field
from typing import Literal, Annotated
from orchestrator_sdk.callback.header_properties import HeaderProperties

from orchestrator_sdk.contracts.exceptions.permanent_exception import PermanentException
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork
from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.testing.availability_simulator import AvailabilitySimulator
from orchestrator_sdk.seedworks.json_worker import JsonWorker
from orchestrator_sdk.callback.callback_types.command_callback import CommandCallback
from orchestrator_sdk.callback.callback_types.event_callback import EventCallback
from orchestrator_sdk.callback.callback_types.stream_event_callback import StreamEventCallback

from orchestrator_sdk.app.orchestration_app import orchestration_app
from src.database.application_database import application_database

message_router = APIRouter()
logger = Logger.get_instance()
availability_sim = AvailabilitySimulator.instance()
json_worker = JsonWorker()

EventUnion = Union[CommandCallback, EventCallback, StreamEventCallback]

async def get_unit_of_work(application_database = None) -> UnitOfWork:
    return UnitOfWork(application_database)

async def get_callback_context(request: Request) -> HeaderProperties:
    account_id = request.headers.get("AccountId")
    application_name = request.headers.get("ApplicationName")
    reference = request.query_params.get("Reference")
    message_id = request.query_params.get("SourceMessageId")
    trace_message_id = request.query_params.get("TraceMessageId")
    message_name = request.query_params.get("MessageName")
    message_type = request.query_params.get("MessageType")
    process_structure = request.query_params.get("ProcessStructure")
    group_trace_key = request.query_params.get("GroupTraceKey")
    dispatcher = request.query_params.get("Dispatcher")
    activity_type = request.query_params.get("ActivityType")
    priority = request.query_params.get("Priority")
    map_message_id = request.query_params.get("MapMessageId")

    return HeaderProperties(
        account_id=account_id,
        message_id=message_id,
        trace_message_id=trace_message_id,
        group_trace_key=group_trace_key,
        dispatcher=dispatcher,
        message_name=message_name,
        message_type=message_type,
        process_structure=process_structure,
        reference=reference,
        activity_type=activity_type,
        application_name=application_name,
        priority=priority,
        map_message_id=map_message_id
    )


@message_router.post('/callback')
async def callback(
    event: EventUnion = Body(...),
    headers: HeaderProperties = Depends(get_callback_context),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work)):  

    try:        
        response = None

        if (not availability_sim.is_available()):
            logger.error(f'Simulated unavailability for [{availability_sim.offline_duration}] minutes until [{availability_sim._available_after}]')
            availability_sim.simulate_unavailable()

        with unit_of_work as uow:      # async with unit_of_work as uow:   

            if isinstance(event, CommandCallback):
                response = await orchestration_app.command_processor.process(callback_event=event, all_headers=headers, unit_of_work=unit_of_work)
            elif isinstance(event, EventCallback):
                response = await orchestration_app.event_processor.process(callback_event=event, all_headers=headers, unit_of_work=unit_of_work)
            elif isinstance(event, StreamEventCallback):
                response = await orchestration_app.stream_processor.process(callback_event=event, all_headers=headers, unit_of_work=unit_of_work)
            else:
                raise HTTPException(status_code=400, detail="Unsupported event type")

        return_object = None

        if (response is not None):
                return_object = json_worker.read_as_json(response)

        return JSONResponse(return_object)            
            
    
    except PermanentException as ex:        
        logger.error(f"Oops! Permanant occurred. Details: {ex}")
        raise HTTPException(status_code=406, detail=str(ex))
    
    except Exception as ex:
        logger.error(f"Oops! Error occurred. Details: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))
