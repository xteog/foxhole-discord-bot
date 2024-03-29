PATH = '.'
DB = {
	'mapName': PATH + '/data/mapName.json',
	'iconId': PATH + '/data/iconId.json',
	'mapData': PATH + '/data/MapData/{}.json',
	'mapImage': PATH + '/data/MapImage/{}.png',
	'iconImage': PATH + '/Icon/{}.png',
	'serverIcon': PATH + '/data/serverIcon.png',
	'dynamicData': 'https://war-service-live.foxholeservices.com/api/worldconquest/maps/{}/dynamic/public',
	'staticData': 'https://war-service-live.foxholeservices.com/api/worldconquest/maps/{}/static',
	'eventChannel': 1032345776300490882,
  'depotChannel': 856644848933011487,
  'dataBaseChannel': 1038431534606209134,
  'bollettinoChannel': 881662982160003113,
  'serverId': 844513454835499041,
  'errorChannel': 1032428103861026897,
	'mapReport': 'https://war-service-live.foxholeservices.com/api/worldconquest/warReport/{}',
	'warReport': 'https://war-service-live.foxholeservices.com/api/worldconquest/war',
	'Token': 'ODgxNjMyODI5NTQ3NjQyOTcy.GCb_U4.AcOcHxTXWm0jU2YVo4MziJ1PosDHj2LGxDUCmg',
	'startWar': 1664389802386,
  'iconFilter': [45, 46, 47, 56, 57, 58, 59, 60],
  'permission': [493028834640396289, 256556507460534273, 296350639611445248, 353826723550461972, 329637567693848580, 305342466545025025],
  'emojis': {
              'ColonialLogo': ['ColonialFaction', 1030064520418295818], 
              'WardenLogo': ['WardenFaction', 1030064521588506655],
              '33': ['StorageFacilityColonial', 1039239759266062457],
              '52': ['SeaportColonial', 1039239757533810749],
              '45': ['RelicBase', 1031540708978458674],
              '45C': ['RelicBaseColonial', 1030505659222986813],
              '45W': ['RelicBaseWarden', 1030505660317712459],
              '46C': ['RelicBaseColonial', 1030505659222986813],
              '46W': ['RelicBaseWarden', 1030505660317712459],
              '47C': ['RelicBaseColonial', 1030505659222986813],
              '47W': ['RelicBaseWarden', 1030505660317712459],
              '56': ['TownBase', 1031540584466350171],
              '56C': ['TownBase1Colonial', 1030505662008021122],
              '56W': ['TownBase1Warden', 1030505663203381289],
              '57C': ['TownBase2Colonial', 1030505665036296263],
              '57W': ['TownBase2Warden', 1030505666395258982],
              '58C': ['TownBase3Colonial', 1030505668555309107],
              '58W': ['TownBase3Warden', 1030505671231295588]
            }
}

ICON_ID = {
  8: 'ForwardBase1',
  11: 'Hospital',
  12: 'VehicleFactory',
  13: 'Armory',
  14: 'SupplyStation',
  15: 'Workshop',
  16: 'ManufacturingPlant',
  17: 'Refinery',
  18: 'Shipyard',
  19: 'TechCenter',
  20: 'SalvageField',
  21: 'ComponentField',
  22: 'FuelField',
  23: 'SulfurField',
  24: 'WorldMapTent',
  25: 'TravelTent',
  26: 'TrainingArea',
  27: 'Keep',
  28: 'ObservationTower',
  29: 'Fort',
  30: 'TroopShip',
  32: 'SulfurMine',
  33: 'StorageFacility',
  34: 'Factory',
  35: 'Safehouse',
  36: 'AmmoFactory',
  37: 'RocketSite',
  38: 'SalvageMine',
  39: 'ConstructionYard',
  40: 'ComponentMine',
  45: 'RelicBase1',
  46: 'RelicBase2',
  47: 'RelicBase3',
  51: 'MassProductionFactory',
  52: 'Seaport',
  53: 'CoastalGun',
  54: 'SoulFactory',
  56: 'TownBase1',
  57: 'TownBase2',
  58: 'TownBase3',
  59: 'StormCannon',
  60: 'IntelCenter',
  61: 'CoalField',
  62: 'OilField'
}

MAP_NAME = [
  "TheFingers",
  "GreatMarch",
  "TempestIsland",
  "MarbanHollow",
  "DeadLands",
  "Heartlands",
  "EndlessShore",
  "Westgate",
  "Oarbreaker",
  "Acrithia",
  "LochMor",
  "AllodsBight",
  "Kalokai",
  "RedRiver",
  "Origin",
  "ShackledChasm",
  "Terminus",
  "AshFields",
  "LinnMercy",
  "Godcrofts",
  "FishermansRow",
  "UmbralWildwood",
  "DrownedVale",
  "FarranacCoast",
  "BasinSionnach",
  "SpeakingWoods",
  "HowlCounty",
  "CallumsCape",
  "ReachingTrail",
  "ClansheadValley",
  "NevishLine",
  "MooringCounty",
  "ViperPit",
  "MorgensCrossing",
  "Stonecradle",
  "CallahansPassage",
  "WeatheredExpanse"
]

MAP_SIZE = (5632, 6216)

REGION_SIZE = (1024, 888)
D_RESIZE = 400

MAP_POSITION = {
  "TheFingers": (4608, 2220),
  "GreatMarch": (2304, 1776),
  "TempestIsland": (4608, 3108),
  "MarbanHollow": (3072, 3996),
  "DeadLands": (2304, 3552),
  "Heartlands": (1536, 2220),
  "EndlessShore": (3840, 3552),
  "Westgate": (768, 2664),
  "Oarbreaker": (0, 3996),
  "Acrithia": (3072, 1332),
  "LochMor": (1536, 3108),
  "AllodsBight": (3840, 2664),
  "Kalokai": (2304, 888),
  "RedRiver": (1536, 1332),
  "Origin": (0, 2220),
  "ShackledChasm": (3072, 2220),
  "Terminus": (3840, 1776),
  "AshFields": (768, 1776),
  "LinnMercy": (1536, 3996),
  "Godcrofts": (4608, 3996),
  "FishermansRow": (0, 3108),
  "UmbralWildwood": (2304, 2664),
  "DrownedVale": (3072, 3108),
  "FarranacCoast": (768, 3552),
  "BasinSionnach": (2304, 6216),
  "SpeakingWoods": (1536, 5772),
  "HowlCounty": (3072, 5772),
  "CallumsCape": (768, 5328),
  "ReachingTrail": (2304, 5328),
  "ClansheadValley": (3840, 5328),
  "NevishLine": (0, 4884),
  "MooringCounty": (1536, 4884),
  "ViperPit": (3072, 4884),
  "MorgensCrossing": (4608, 4884),
  "Stonecradle": (768, 4440),
  "CallahansPassage": (2304, 4440),
  "WeatheredExpanse": (3840, 4440)
}