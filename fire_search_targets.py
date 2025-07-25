# Fire search targets for tweet_fire_search.py
# US_STATES = [
#     "California"
# ]
US_STATES = [
    "Arizona", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Idaho", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Michigan", "Minnesota", "Mississippi", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "South Carolina", "Tennessee", "Texas", "US Virgin Islands", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming", "DC"
]
FIRE_KEYWORDS = [
    "house fire", "apartment complex", "store fire", "commercial fire", "restaurant fire", "warehouse fire", "business fire", "pipe burst"
]
FIRE_ACCOUNTS = [
    "@DFWscanner", "@DallasTexasTV", "@NWSSanAntonio", "@FriscoFFD", "@RedCrossTXGC", "@whatsupTucson", "@WacoTXFire", "@SouthMetroPIO", "@NWSBoulder", "@SeattleFire", "@CityofMiamiFire", "@PeterNewcomb41", "@ffxfirerescue", "@ScannerRadioDFW", "@sfgafirerescue", "@THEJFRD", "@ChicagoMWeather", "@ToledoFire", "@AustinFireInfo"
]
FIRE_SEARCH_COMBINATIONS = [
    f"{state} {fire}" for state in US_STATES for fire in FIRE_KEYWORDS
]
def get_all_fire_accounts():
    return [acc.lstrip('@') for acc in FIRE_ACCOUNTS]
def get_all_fire_search_combinations():
    return FIRE_SEARCH_COMBINATIONS 