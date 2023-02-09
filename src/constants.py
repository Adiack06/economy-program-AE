from building_info import BuildingInfo
from enum import IntEnum, unique
# IDs
@unique
class BType(IntEnum):
    RAILWAY_STATION       = 0
    MARKET_STALL          = 1
    POLICE_STATION        = 2
    POST_OFFICE           = 3
    SMALL_STORE           = 4
    HOSPITAL              = 5
    FIRE_STATION          = 6
    SUPER_STORE           = 7
    PIER                  = 8
    DOCK                  = 9
    QUARRY                = 10
    SMALL_FACTORY         = 11
    LARGE_FACTORY         = 12
    FARMING               = 13
    NAVAL_DOCKYARD        = 14
    MILLS                 = 15
    AIRBASE               = 16
    SUPPLY_HUB            = 17
    REACTOR               = 18
    ELECTRICAL_GENERATION = 19
    AIRPORT               = 20
    HOUSE                 = 21
    OFFICE                = 22
    METRO_STATION         = 23

ROI = 13
MONEY_PREFIX = "UN$"
UN_LOAN_INTEREST = 0.20
OVERDRAFT_INTEREST = 0.30

BUILDING_INFO = {
    BType.RAILWAY_STATION       : BuildingInfo(13.5,  2,     2808,     "Railway Station"),
    BType.MARKET_STALL          : BuildingInfo(11,    1,     1144.00,  "Market Stall"),
    BType.POLICE_STATION        : BuildingInfo(19.6,  3,     6115.20,  "Police Station"),
    BType.POST_OFFICE           : BuildingInfo(12.5,  2,     2600.00,  "Post Office"),
    BType.SMALL_STORE           : BuildingInfo(11.5,  2,     2392.00,  "Small Store/Fuel Station"),
    BType.HOSPITAL              : BuildingInfo(26,    3,     8112.00,  "Hospital"),
    BType.FIRE_STATION          : BuildingInfo(19,    2,     3952.00,  "Fire station"),
    BType.SUPER_STORE           : BuildingInfo(12.2,  4,     5075.20,  "Super Store"),
    BType.PIER                  : BuildingInfo(14,    1,     1456.00,  "Pier"),
    BType.DOCK                  : BuildingInfo(15.8,  2,     3286.40,  "Dock per 10 blocks"),
    BType.QUARRY                : BuildingInfo(11.2,  2,     2329.60,  "Quarries Per Chunk"),
    BType.SMALL_FACTORY         : BuildingInfo(14.5,  6,     9048.00,  "Small Factory"),
    BType.LARGE_FACTORY         : BuildingInfo(15.5,  12,    19344.00, "Large Factory"),
    BType.FARMING               : BuildingInfo(18.5,  1/162, 11.9,     "Farming per block"),
    BType.NAVAL_DOCKYARD        : BuildingInfo(15.5,  1,     1612.00,  "Naval dockyard per 7 blocks"),
    BType.MILLS                 : BuildingInfo(0,     12,    25500.00, "MiLLs"),
    BType.AIRBASE               : BuildingInfo(17.5,  4,     7280.00,  "Airbase"),
    BType.SUPPLY_HUB            : BuildingInfo(10.5,  1,     1092.00,  "Supply hub"),
    BType.REACTOR               : BuildingInfo(20.5,  3,     6396.00,  "Nuclear/biogas reactor"),
    BType.ELECTRICAL_GENERATION : BuildingInfo(12.5,  2,     2600.00,  "Electrical generation/storage"),
    BType.AIRPORT               : BuildingInfo(18,    0,     69,       "Airport"),
    BType.HOUSE                 : BuildingInfo(0,     0,     69420,    "House"),
    BType.OFFICE                : BuildingInfo(18,    1,     1872.00,  "Office"),
    BType.METRO_STATION         : BuildingInfo(12.9,  1,     1341.60,  "Metro Station")
}