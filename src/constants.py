from building_info import BuildingInfo
# IDs
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
BARRACKS              = 24
MUNITION_FACTORY      = 25
STORAGE_BUNKER        = 26
POTION_BREWERY        = 27
CHEMICAL_WEAPONS_FAC  = 28
MILITARY_AIRSTRIP     = 29
MILITARY_AIRBASE      = 30
MILITARY_DOCKYARDS    = 31
DRY_DOCKS             = 32

TRANSACTION_MANUAL = 1
TRANSACTION_BUY    = 2
TRANSACTION_SELL   = 3
TRANSACTION_INCOME = 4

ROI = 13
MONEY_PREFIX = "UN$"
UN_LOAN_INTEREST = 0.20
OVERDRAFT_INTEREST = 0.30

BUILDING_INFO = {
    RAILWAY_STATION       : BuildingInfo(13.5,  2,     2808,     "Railway Station"),
    MARKET_STALL          : BuildingInfo(11,    1,     1144.00,  "Market Stall"),
    POLICE_STATION        : BuildingInfo(19.6,  3,     6115.20,  "Police Station"),
    POST_OFFICE           : BuildingInfo(12.5,  2,     2600.00,  "Post Office"),
    SMALL_STORE           : BuildingInfo(11.5,  2,     2392.00,  "Small Store/Fuel Station"),
    HOSPITAL              : BuildingInfo(26,    3,     8112.00,  "Hospital"),
    FIRE_STATION          : BuildingInfo(19,    2,     3952.00,  "Fire station"),
    SUPER_STORE           : BuildingInfo(12.2,  4,     5075.20,  "Super Store"),
    PIER                  : BuildingInfo(14,    1,     1456.00,  "Pier"),
    DOCK                  : BuildingInfo(15.8,  2,     3286.40,  "Dock per 15 blocks"),
    QUARRY                : BuildingInfo(11.2,  2,     2329.60,  "Quarries Per Chunk"),
    SMALL_FACTORY         : BuildingInfo(14.5,  6,     9048.00,  "Small Factory"),
    LARGE_FACTORY         : BuildingInfo(15.5,  12,    19344.00, "Large Factory"),
    FARMING               : BuildingInfo(18.5,  1/324, 11.9,     "Farming per block"),
    NAVAL_DOCKYARD        : BuildingInfo(15.5,  1,     1612.00,  "Naval dockyard per 7 blocks"), #depricated 
    MILLS                 : BuildingInfo(0,     12,    25500.00, "MiLLs"), #depricated 
    AIRBASE               : BuildingInfo(17.5,  4,     7280.00,  "Airbase"), #depricated 
    SUPPLY_HUB            : BuildingInfo(10.5,  1,     1092.00,  "Supply hub"),
    REACTOR               : BuildingInfo(20.5,  6,     6396.00,  "Nuclear/biogas reactor"),
    ELECTRICAL_GENERATION : BuildingInfo(12.5,  2,     2600.00,  "Electrical generation/storage"),
    AIRPORT               : BuildingInfo(18,    0,     69,       "Airport"),
    HOUSE                 : BuildingInfo(0,     0,     69420,    "House"),
    OFFICE                : BuildingInfo(18,    1,     1872.00,  "Office"),
    METRO_STATION         : BuildingInfo(12.9,  1,     1341.60,  "Metro Station"),
    BARRACKS              : BuildingInfo(13,    3,     4056,     "Barracks"),
    MUNITION_FACTORY      : BuildingInfo(14.5,  6,     9048,     "Munition Factory"),
    STORAGE_BUNKER        : BuildingInfo(10,    5,     5200,     "Storage Bunker"),
    POTION_BREWERY        : BuildingInfo(13.5,  3,     4212,     "Potion Brewery"),
    CHEMICAL_WEAPONS_FAC  : BuildingInfo(15,    6,     9360,     "Chemical Weapons Fac."),
    MILITARY_AIRSTRIP     : BuildingInfo(15.5,  0,     806,      "Military Airstrip"),
    MILITARY_AIRBASE      : BuildingInfo(16.5,  0,     1716,     "Military Airbase"),
    MILITARY_DOCKYARDS    : BuildingInfo(14.5,  1,     1508,     "Military Dockyards per 7 blocks"),
    DRY_DOCKS             : BuildingInfo(15,    2,     3120,     "Dry Docks per 7 blocks")
}

