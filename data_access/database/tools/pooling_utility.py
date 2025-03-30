from sqlalchemy import Engine
from sdk.logging.logger import Logger

import asyncio

class PoolingUtility:
    
    DB_SLEEP_IN_SECONDS:int = 5
    DB_POOL_OVERFLOW_THRESHOLD:int = 20
    
    logger:Logger = None
    db_engine:Engine = None
    
    def __init__(self, logger:Logger, db_engine: Engine) -> None:
        self.logger = logger
        self.db_engine = db_engine        

    async def throttle_database_connections(self):
    
        max_delays = 10
        check_pooling = True
        delay_counter = 0
        db_pool = self.db_engine.pool
        
        if (db_pool == None):
            return
        
        while (check_pooling and (delay_counter < max_delays)):               
            
            pool_limit = db_pool.size()
            pool_overflow = self.DB_POOL_OVERFLOW_THRESHOLD
            pool_in_use =  db_pool.checkedout()
            
            danger_zone = (pool_overflow-pool_limit) / 2
            
            if (pool_in_use > pool_limit):
                self.logger.info(f"There are more connections open [{pool_in_use}] than the limit [{pool_limit}] it will start to fail when it reaches [{pool_overflow}]")
            
            if pool_in_use < (pool_limit + danger_zone):
                check_pooling = False
                
            else:
                delay_counter += 1
                self.logger.warn(f"Overflow is reaching dangerous levels. Delaying batch submission [{delay_counter}/{max_delays}]. The Limit: [{pool_limit}], Total Connections: [{pool_in_use}] and Overflow Threshold: [{pool_overflow}]")
                await asyncio.sleep(self.DB_SLEEP_IN_SECONDS)
                            