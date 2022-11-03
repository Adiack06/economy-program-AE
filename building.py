from constants import *
from typing import Union
import datetime

class Building:
    def __init__(self, btype: int, date: datetime.date, size: int=None):
        self.btype = btype
        self.size = size
        self.date = date
        
        if self.btype == AIRPORT or self.btype == HOUSE:
            assert self.size != None, "For airports and houses, the size must not be None"
    
    def cost(self) -> float:
        if self.btype == AIRPORT:
            return ROI * self.income()
        elif self.btype == HOUSE:
            return {1: 1500, 2: 3000, 4: 6000, 6: 9000}[self.size]
        else:
            return BUILDING_INFO[self.btype].cost
    
    def wage(self) -> float:
        return BUILDING_INFO[self.btype].wage
    
    def employees(self) -> int:
        #annoying hack to make airports bought before some date
        if self.btype == AIRPORT:
            if self.date < datetime.date(2022, 10, 20):
                return 6            
            return self.size / 20
        return BUILDING_INFO[self.btype].employees
    
    def name(self) -> str:
        if self.btype == AIRPORT:
            return str(self.size) + " block long airport"
        if self.btype == HOUSE:
            return str(self.size) + " person house"
        return BUILDING_INFO[self.btype].name
        
    def income(self) -> float:
        return self.wage() * self.employees() * 8 # 8 hours per day
        
    def serialise(self) -> Union[list[int, int], int]:
        # if need to store size, return [type, size]
        if self.size != None:
            return [self.btype, self.size]
        else: # else just a single int
            return self.btype
            
    def deserialise(obj: Union[list[int, int], int], date: datetime.date):
        # serialised buildings are either a list of [type, size]
        if type(obj) == type([]):
            return Building(obj[0], date, obj[1])
        else: # or just a single int, being type
            return Building(obj, date)
            
    def __hash__(self):
        return hash((self.btype, self.size))
        
    def __eq__(self, other):
        return type(self) == type(other) and self.btype == other.btype and self.size == other.size
        

