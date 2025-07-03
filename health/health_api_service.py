from fastapi import HTTPException
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from src.database.application_database import application_database
from orchestrator_sdk.seedworks.logger import Logger
from orchestrator_sdk.data_access.database.unit_of_work import UnitOfWork
from orchestrator_sdk.services.health_service import HealthService
from fastapi.encoders import jsonable_encoder

health_router = APIRouter()
logger = Logger.get_instance()

@health_router.get('/ClientHealth')
async def ClientHealth():  

    try:       

        unit_of_work = UnitOfWork(application_database)       
        with unit_of_work as uow:
           
           service = HealthService(uow)
           response = await service.do_health_check()
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(response)
        )

    except Exception as ex:
        logger.error(f"Oops! {ex.__class__} occurred. Failed to do health checks. Details: {ex}")
        raise HTTPException(status_code=500, detail="An error occurred.")