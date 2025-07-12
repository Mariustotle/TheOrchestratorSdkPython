from loguru import logger
from pathlib import Path

import os
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.seedworks.contracts.logging import Logging

def _get_log_level(level:str):
    
    if (level.lower() == 'trace'):
        return "TRACE"

    if (level.lower() == 'debug'):
        return "DEBUG"
    
    if (level.lower() == 'info'):
        return "INFO"
    
    if (level.lower() == 'warn'):
        return "WARNING"
    
    if (level.lower() == 'error'):
        return "ERROR"
    
    if (level.lower() == 'critical'):
        return "CRITICAL"
    
    raise ValueError('Unknown log level specified in configuration')

class Logger:
    _logger_instance = None

    @staticmethod
    def get_instance():
        if Logger._logger_instance is None:
            Logger._logger_instance = Logger._setup_logger()
        return Logger._logger_instance

    @staticmethod
    def _setup_logger():
        try:
            logger_settings = ConfigReader().section("logging", Logging)

            log_dir  = Path(logger_settings.path)
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / logger_settings.file_name 

            logger.add(
                log_file,
                level=_get_log_level(logger_settings.level),
                rotation=f"{logger_settings.max_file_size_in_mb} MB",
                retention=logger_settings.max_number_of_files,
                enqueue=True,
                backtrace=True,
                compression="zip",
                format=(logger_settings.log_format or
                        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                        "{level:<8} | {module}.{function}:{line} - {message}")
            )

            # logger.info(f'Logger Initialized')

            return logger        

        except Exception as ex:
            print(f"Oops! {ex.__class__} occurred. Unable to initialize the logger. Details: {ex}")
            raise