# ---
# Variables used for search queries in tweet_fire_search.py:
#   - FIRE_HASHTAGS: Used for hashtag-based searches (e.g., #FireCalifornia)
#   - LOCATION_FIRE_HASHTAGS: Used for location-based hashtag searches (same as FIRE_HASHTAGS)
#   - FIRE_SEARCH_COMBINATIONS: Used for [state] [fire keyword] searches (e.g., 'Arizona house fire')
#   - FIRE_ACCOUNTS: Used for account-based searches (e.g., from:DFWscanner)
#
# Example usage for FIRE_SEARCH_COMBINATIONS:
#   from fire_search_targets import get_all_fire_search_combinations
#   combos = get_all_fire_search_combinations()
#   for combo in combos:
#       print(combo)  # e.g., 'Arizona house fire', 'Texas warehouse fire', ...
#
# The following are NOT currently used for search:
#   - PERILS: Not used in any search queries (commented out for now)
# ---

# 🔥 Fire-Related Twitter Search Targets (USA Only)

# Expanded US states
# US_STATES = [
#     "Arizona", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Idaho", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Michigan", "Minnesota", "Mississippi", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "South Carolina", "Tennessee", "Texas", "US Virgin Islands", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming", "DC"
# ]
US_STATES = [
       "California"
   ]
# Fire/structure keywords and perils
FIRE_KEYWORDS = [
    "house fire", "apartment complex", "store fire", "commercial fire", "restaurant fire", "warehouse fire", "business fire", "pipe burst"
]
# (PERILS is not used in search queries currently)
# PERILS = [
#     "hurricanes", "wildfires", "smoke", "explosion", "volcanic eruption", "lightning", "hail", "hailstorm", "landslides", "earthquake", "flood", "freezing", "storm", "tornado"
# ]

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
    f"#Fire{state.replace(' ', '')}" for state in HIGH_FIRE_INCIDENT_STATES
]

LOCATION_FIRE_HASHTAGS = FIRE_HASHTAGS

# Regex pattern to match US fire-related hashtags (case-insensitive)
import re
FIRE_HASHTAG_REGEX = re.compile(r"#(fire|wildfire|housefire|apartmentfire|storefire|commercialfire|restaurantfire|warehousefire|businessfire|pipeburst|hurricane|wildfires|smoke|explosion|volcaniceruption|lightning|hail|hailstorm|landslides|earthquake|flood|freezing|storm|tornado)", re.IGNORECASE)

import itertools

# Generate all combinations: [state] [fire keyword]
FIRE_SEARCH_COMBINATIONS = [
    f"{state} {fire}" for state in US_STATES for fire in FIRE_KEYWORDS
]

def get_all_fire_hashtags():
    return FIRE_HASHTAGS + LOCATION_FIRE_HASHTAGS

def get_all_fire_accounts():
    return [acc.lstrip('@') for acc in FIRE_ACCOUNTS]

def get_all_fire_search_combinations():
    return FIRE_SEARCH_COMBINATIONS 