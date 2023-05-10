from constants import *
from typing import Union
import datetime

class Building:
    def __init__(self, btype: int, date: datetime.date, lorentz: int, size: int=None):
        self.btype = btype
        self.size = size
        self.date = date
        self.lorentz = lorentz
        
        if btype == HOUSE or btype == AIRPORT or btype == MILITARY_AIRSTRIP or btype == MILITARY_AIRBASE :
            assert self.size != None, "For airports and houses, the size must not be None"

    def get_lorentz(eco) -> float:
        return (((eco / 1000) + 0.2)**0.425)/3 + 0.34

    def cost(self, l=None) -> float:
        if l is None:
            lorentz = self.lorentz
        else:
            lorentz = l

        if self.btype == AIRPORT:
            return ROI * self.income() * lorentz
        elif self.btype == MILITARY_AIRSTRIP:
            return ROI * self.income() * lorentz
        elif self.btype == MILITARY_AIRBASE:
            return ROI * self.income() * lorentz
        elif self.btype == HOUSE:
            return {1: 1500, 2: 3000, 4: 6000, 6: 9000}[self.size] * lorentz
        elif self.btype != MILLS:
            return BUILDING_INFO[self.btype].cost * lorentz
        else:
            return BUILDING_INFO[self.btype].cost # mils are exempt from relativistic pricing
    
    def wage(self) -> float:
        return BUILDING_INFO[self.btype].wage
    
    def employees(self) -> int:
        #annoying hack to make airports bought before some date
        if self.btype == AIRPORT:
            if self.date < datetime.date(2022, 10, 20):
                return 6            
            return self.size / 20
        elif self.btype == MILITARY_AIRSTRIP:
            return self.size / 40
        elif self.btype == MILITARY_AIRBASE:
            return self.size / 20
        return BUILDING_INFO[self.btype].employees
    
    def name(self, airports_together=False) -> str:
        if self.btype == AIRPORT:
            if airports_together:
                return "Airport"
            return str(self.size) + " block long airport"
        if self.btype == MILITARY_AIRSTRIP:
            if airports_together:
                return "Military Airstrip"
            return str(self.size) + " block long Military Airstrip"
        if self.btype == MILITARY_AIRBASE:
            if airports_together:
                return "Military Airbase"
            return str(self.size) + " block long Military Airbase"
        if self.btype == HOUSE:
            return {1: "One", 2: "Two", 4: "Four", 6: "Six"}[self.size] + " person house"
        
        return BUILDING_INFO[self.btype].name
        
    def income(self) -> float:
        return self.wage() * self.employees() * 8 # 8 hours per day
        
    def serialise(self):
        return [self.btype, self.size, self.lorentz]
            
    def deserialise(obj, date: datetime.date, lorentz: float=None):
        if lorentz is None:
            lorentz = 1
        # old serialised buildings are either a list of [type, size]
        # or just a single int type. New serialised buildings are always
        # a list of [type, size, lorentz] to avoid ambiguity.
        if type(obj) == list:
            if len(obj) == 2: # old building, type and size
                return Building(obj[0], date, lorentz, obj[1])
            elif len(obj) == 3: # new building, type size and lorentz
                return Building(obj[0], date, obj[2], obj[1])
        else: # old building, just type
            return Building(obj, date, lorentz)
            
    def __eq__(self, other):
        return type(self) == type(other) and self.btype == other.btype and self.size == other.size and self.lorentz == other.lorentz

    def is_roughly(self, other):
        return type(self) == type(other) and self.btype == other.btype and self.size == other.size

