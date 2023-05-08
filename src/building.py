from constants import *
from typing import Union
import datetime

class Building:
    def __init__(self, btype: int, date: datetime.date, lorentz: int, size: int=None, count: int=1):
        self.btype = btype
        self.size = size
        self.date = date
        self.lorentz = lorentz
        self.count = count
        
        if btype == BType.HOUSE or btype == BType.AIRPORT or btype == BType.MILITARY_AIRSTRIP or btype == BType.MILITARY_AIRBASE :
            assert self.size != None, "For airports and houses, the size must not be None"

    def get_lorentz(eco) -> float:
        return (((eco / 1000) + 0.2)**0.425)/3 + 0.34

    def cost(self, l=None) -> float:
        if l is None:
            lorentz = self.lorentz
        else:
            lorentz = l

        if self.btype == BType.AIRPORT or BType.MILITARY_AIRSTRIP or BType.MILITARY_AIRBASE:
            return ROI * self.income() * lorentz * self.count
        
        elif self.btype == BType.HOUSE:
            return {1: 1500, 2: 3000, 4: 6000, 6: 9000}[self.size] * lorentz * self.count
        elif self.btype != BType.MILLS:
            return BUILDING_INFO[self.btype].cost * lorentz * self.count
        else:
            return BUILDING_INFO[self.btype].cost * self.count # mils are exempt from relativistic pricing
    
    def wage(self) -> float:
        return BUILDING_INFO[self.btype].wage
    
    def employees(self) -> int:
        #annoying hack to make airports bought before some date employ 6 people
        if self.btype == BType.AIRPORT:
            if self.date < datetime.date(2022, 10, 20):
                return 6 * self.count
            return self.size / 20 * self.count
        return BUILDING_INFO[self.btype].employees * self.count
    
    def name(self, airports_together=False) -> str:
        if self.btype == BType.AIRPORT:
            if airports_together:
                return "Airport"
            return str(self.size) + " block long airport"
        if self.btype == BType.HOUSE:
            return {1: "One", 2: "Two", 4: "Four", 6: "Six"}[self.size] + " person house"
        if self.btype == BType.MILITARY_AIRSTRIP:
            if airports_together:
                return "Military Airstrip"
            return str(self.size) + " block long Military Airstrip"
        if self.btype == BType.MILITARY_AIRBASE:
            if airports_together:
                return "Military Airbase"
            return str(self.size) + " block long Military Airbase"
        
        return BUILDING_INFO[self.btype].name
        
    def income(self) -> float:
        return self.wage() * self.employees() * 8 # 8 hours per day
        
    def __eq__(self, other):
        return type(self) == type(other) and self.btype == other.btype and self.size == other.size and self.lorentz == other.lorentz and self.count == other.count

    def is_roughly(self, other):
        return type(self) == type(other) and self.btype == other.btype and self.size == other.size

