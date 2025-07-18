# 🔥 Fire-Related Twitter Search Targets (USA Only)

# Expanded US states
US_STATES = [
    "Arizona", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Idaho", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Michigan", "Minnesota", "Mississippi", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "South Carolina", "Tennessee", "Texas", "US Virgin Islands", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming", "DC"
]

# Fire/structure keywords and perils
FIRE_KEYWORDS = [
    "house fire", "apartment complex", "store fire", "commercial fire", "restaurant fire", "warehouse fire", "business fire", "pipe burst"
]
PERILS = [
    "hurricanes", "wildfires", "smoke", "explosion","tornado", "fire"
]

# Twitter accounts to monitor for US fire/peril news
FIRE_ACCOUNTS = [
    "@DFWscanner", "@DallasTexasTV", "@NWSSanAntonio", "@FriscoFFD", "@RedCrossTXGC", "@whatsupTucson", "@WacoTXFire", "@SouthMetroPIO", "@NWSBoulder", "@SeattleFire", "@CityofMiamiFire", "@PeterNewcomb41", "@ffxfirerescue", "@ScannerRadioDFW", "@sfgafirerescue", "@THEJFRD", "@ChicagoMWeather", "@ToledoFire", "@AustinFireInfo"
]

# States with the most fire incidents (example list, can be expanded)
HIGH_FIRE_INCIDENT_STATES = [
    "California", "Texas", "Arizona", "Colorado", "Florida", "Oregon", "Washington", "Nevada", "New Mexico", "Utah", "Idaho", "Montana", "Wyoming"
]

# Hashtags for only high-fire-incident states, format: '#Fire{State}'
FIRE_HASHTAGS = [
    f"#{state.replace(' ', '')}Fire" for state in HIGH_FIRE_INCIDENT_STATES
]

LOCATION_FIRE_HASHTAGS = FIRE_HASHTAGS

# Regex pattern to match US fire-related hashtags (case-insensitive)
import re
FIRE_HASHTAG_REGEX = re.compile(r"#(fire|wildfire|housefire|apartmentfire|storefire|commercialfire|restaurantfire|warehousefire|businessfire|pipeburst|hurricane|wildfires|smoke|explosion|volcaniceruption|lightning|hail|hailstorm|landslides|earthquake|flood|freezing|storm|tornado)", re.IGNORECASE)

import itertools

# Generate all combinations: [state] [fire keyword]
FIRE_SEARCH_COMBINATIONS = [
    f"{state} {fire}"
    for state in US_STATES
    for fire in FIRE_KEYWORDS
]

def get_all_fire_hashtags():
    return FIRE_HASHTAGS + LOCATION_FIRE_HASHTAGS + FIRE_KEYWORDS + PERILS

def get_all_fire_accounts():
    return [acc.lstrip('@') for acc in FIRE_ACCOUNTS]

def get_all_fire_search_combinations():
    return FIRE_SEARCH_COMBINATIONS 