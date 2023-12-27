from orchestrator_sdk.contracts.exceptions.permanent_exception import PermanentException
from pydantic import BaseModel
from typing import Optional

import time
import asyncio
import random

class WorkloadSimulator(BaseModel):
    blocked_percentage_in_seconds: Optional[int] = None
    exception_percentage: Optional[int] = None
    permanent_exception_percentage: Optional[int] = None
    fastest_time: int = 0
    slowest_time: int = 0
        
    def set_execution_span(self, fastest_time_in_seconds: int, slowest_time_in_seconds: int) -> 'WorkloadSimulator':
        if (fastest_time_in_seconds > slowest_time_in_seconds):
            raise Exception(f'Please make sure your fastest time [{fastest_time_in_seconds}] is smaller than your slowest time [{slowest_time_in_seconds}]')  
        
        self.fastest_time = fastest_time_in_seconds
        self.slowest_time = slowest_time_in_seconds
        
        return self 
        
       
    def set_blocked_percentage_of_execution_time(self, blocked_percentage_in_seconds:int) -> 'WorkloadSimulator':
        self.blocked_percentage_in_seconds = blocked_percentage_in_seconds
        return self
    
    def set_exception_thresholds(self, exception_percentage:int, permanent_exception_percentage:Optional[int] = None) -> 'WorkloadSimulator':
        self.exception_percentage = exception_percentage
        self.permanent_exception_percentage = permanent_exception_percentage
        return self    

    async def run(self, percentage_faster:Optional[int] = None, percentage_slower:[int] = None) -> int:
        start_time = time.time()
        
        distance = self.slowest_time- self.fastest_time
        
        fastest = self.fastest_time
        slowest = self.slowest_time       
        
        if (percentage_faster != None and percentage_faster > 0):
            adjustment = round(distance * (percentage_faster/100))
            slowest = slowest - adjustment
            
        if (percentage_slower != None and percentage_slower > 0):
            adjustment = round(distance * (percentage_slower/100))
            fastest = fastest + adjustment               
        
        total_duration_in_seconds:int = random.randint(fastest, slowest)
        blocked_duration_in_seconds:Optional[float] = total_duration_in_seconds * (self.blocked_percentage_in_seconds/100) if self.blocked_percentage_in_seconds != None and self.blocked_percentage_in_seconds > 0 else None
        
        if blocked_duration_in_seconds != None and blocked_duration_in_seconds > 0:
            time.sleep(blocked_duration_in_seconds)
            
        non_blocking_duration:float = total_duration_in_seconds if blocked_duration_in_seconds == None else total_duration_in_seconds - blocked_duration_in_seconds        
        await asyncio.sleep(non_blocking_duration) 
        
        error_chance = random.randint(1, 100)
        
        if error_chance <= self.permanent_exception_percentage:
            raise PermanentException(f'Simulated Permanent Error @ [{error_chance}/{self.permanent_exception_percentage}%]')
        
        if error_chance <= self.exception_percentage:
            raise Exception(f'Simulated Error @ [{error_chance}/{self.exception_percentage}%]')  

        end_time = time.time()        
        duration_in_seconds = end_time - start_time
        
        return round(duration_in_seconds)