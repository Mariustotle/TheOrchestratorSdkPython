import logging
from orchestrator_sdk.seedworks.config_reader import ConfigReader
from orchestrator_sdk.seedworks.contracts.logging import Logging

def _get_log_level(level:str):
    
    if (level.lower() == 'debug'):
        return logging.DEBUG
    
    if (level.lower() == 'info'):
        return logging.INFO
    
    if (level.lower() == 'warn'):
        return logging.WARN
    
    if (level.lower() == 'error'):
        return logging.ERROR
    
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
            config_reader = ConfigReader()

            logger_settings = config_reader.section('logging', Logging)
            log_level = _get_log_level(logger_settings.level)

            logger = logging.getLogger('app-logger')
            logger.setLevel(log_level)

            # Check if handlers already exist
            if logger.hasHandlers():
                logger.handlers.clear()

            file_handler = logging.FileHandler(logger_settings.path)
            file_handler.setLevel(log_level)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

            return logger

        except Exception as ex:
            print(f"Oops! {ex.__class__} occurred. Unable to initialize the logger. Details: {ex}")
            raise
    