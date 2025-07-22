import os
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fire_search_targets import get_all_fire_hashtags, get_all_fire_accounts, get_all_fire_search_combinations
from selenium.common.exceptions import WebDriverException
from urllib.parse import quote
import re
from datetime import datetime, timedelta
from ai_fire_verifier import verify_and_save_to_excel
import threading
import shutil
from contextlib import redirect_stdout

TWITTER_USERNAME = "TechWfm63921"
TWITTER_PASSWORD = "Pass@123"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "tweets.json")
OUTPUT_RAW_FILE = os.path.join(os.path.dirname(__file__), "tweets_raw.json")
OUTPUT_CLEANED_FILE = os.path.join(os.path.dirname(__file__), "tweets_cleaned.json")

LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
QUERIES_LOG = os.path.join(LOGS_DIR, "queries_searched.txt")
COMBOS_LOG = os.path.join(LOGS_DIR, "combination_keywords.txt")
ACCOUNTS_LOG = os.path.join(LOGS_DIR, "accounts_searched.txt")
SCRAPE_LOG = os.path.join(LOGS_DIR, "scrape.log")

# ---
# All search keywords, hashtags, perils, and state lists are now sourced from fire_search_targets.py
# Do not define or use any search-related variables here.
# ---

# (No unused search variables remain in this script)

# Setup WebDriver

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# Load Existing Tweets

def load_existing_tweets(raw=True):
    file_path = OUTPUT_RAW_FILE if raw else OUTPUT_CLEANED_FILE
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# Save Tweets to File

def save_tweet(tweet_data, raw=True):
    file_path = OUTPUT_RAW_FILE if raw else OUTPUT_CLEANED_FILE
    existing_tweets = load_existing_tweets(raw=raw)
    if tweet_data not in existing_tweets:
        existing_tweets.append(tweet_data)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(existing_tweets, file, indent=4, ensure_ascii=False)
        print(f"✅ Tweet saved: {tweet_data['content'][:50]}... ({'raw' if raw else 'cleaned'})")

# Twitter Login

def twitter_login(driver):
    driver.get("https://twitter.com/login")
    time.sleep(5)
    username_input = driver.find_element(By.NAME, "text")
    username_input.send_keys(TWITTER_USERNAME)
    username_input.send_keys(Keys.RETURN)
    time.sleep(3)
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(TWITTER_PASSWORD)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)

# Scrape recent tweets for a given search query

def scrape_recent_tweets_for_query(driver, query, max_tweets=10, scroll_times=4, mode="live", tab_index=0, log_f=None):
    encoded_query = quote(query)
    if mode == "live":
        search_url = f"https://twitter.com/search?q={encoded_query}&f=live"
    else:
        search_url = f"https://twitter.com/search?q={encoded_query}&f=top"
    # Switch to the correct tab
    driver.switch_to.window(driver.window_handles[tab_index])
    driver.get(search_url)
    time.sleep(7)  # Wait longer for page to load
    for _ in range(scroll_times):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(random.uniform(2, 4))
    tweet_elements = driver.find_elements(By.XPATH, "//article[@role='article']")
    msg = f"Found {len(tweet_elements)} tweets for query: {query}"
    if log_f:
        log_print(msg, log_f)
    else:
        print(msg)
    tweets_scraped = 0
    for tweet in tweet_elements:
        if tweets_scraped >= max_tweets:
            break
        try:
            username = tweet.find_element(By.XPATH, ".//div[@dir='ltr']/span").text
            content = tweet.find_element(By.XPATH, ".//div[@lang]").text
            timestamp = tweet.find_element(By.XPATH, ".//time").get_attribute("datetime")
            try:
                href = tweet.find_element(By.XPATH, ".//time/parent::a").get_attribute("href")
                tweet_url = href
            except:
                tweet_url = "URL Not Found"
            try:
                retweets = tweet.find_element(By.XPATH, ".//div[@data-testid='retweet']").get_attribute("textContent") or "0"
            except:
                retweets = "0"
            try:
                likes = tweet.find_element(By.XPATH, ".//div[@data-testid='like']").get_attribute("textContent") or "0"
            except:
                likes = "0"
            media = tweet.find_elements(By.XPATH, ".//img[contains(@src, 'twimg')]")
            media_urls = [img.get_attribute("src") for img in media]
            tweet_data = {
                "username": username,
                "content": content,
                "timestamp": timestamp,
                "tweet_url": tweet_url,
                "retweets": retweets,
                "likes": likes,
                "media": media_urls,
                "search_query": query,
                "source_account": username
            }
            msg = f"Extracted tweet: {content[:100]} | {timestamp} | {tweet_url}"
            if log_f:
                log_print(msg, log_f)
            else:
                print(msg)
            save_tweet(tweet_data, raw=True)
            tweets_scraped += 1
        except Exception as e:
            msg = f"⚠️ Skipping tweet due to error: {e}"
            if log_f:
                log_print(msg, log_f)
            else:
                print(msg)
            continue

def safe_scrape(driver, query, max_retries=3, scroll_times=0, mode="live"):
    for attempt in range(max_retries):
        try:
            scrape_recent_tweets_for_query(driver, query, scroll_times=scroll_times, mode=mode)
            return True
        except WebDriverException as e:
            print(f"⚠️ Error for query '{query}' (mode={mode}): {e}. Retrying ({attempt+1}/{max_retries})...")
            time.sleep(random.uniform(10, 30) * (attempt + 1))  # Exponential backoff
    print(f"❌ Failed to scrape for query '{query}' (mode={mode}) after {max_retries} attempts.")
    return False

def save_logs(queries, combos, accounts):
    if os.path.exists(LOGS_DIR):
        shutil.rmtree(LOGS_DIR)
    os.makedirs(LOGS_DIR, exist_ok=True)
    # Write queries_searched.txt
    with open(QUERIES_LOG, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write(f"QUERIES SEARCHED LOG  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n")
        f.write(f"Total Queries: {len(queries)}\n\n")
        f.write("{:<5} {:<60} {:<6}\n".format('No.', 'Query', 'Mode'))
        f.write("-"*80 + "\n")
        for idx, (q, mode, _) in enumerate(queries, 1):
            f.write(f"{idx:<5} {q:<60} {mode:<6}\n")
    # Write combination_keywords.txt
    with open(COMBOS_LOG, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write(f"COMBINATION KEYWORDS  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n")
        f.write(f"Total Combination Keywords: {len(combos)}\n\n")
        for idx, c in enumerate(combos, 1):
            f.write(f"{idx:>3}. {c}\n")
    # Write accounts_searched.txt
    with open(ACCOUNTS_LOG, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write(f"ACCOUNTS SEARCHED  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n")
        f.write(f"Total Accounts: {len(accounts)}\n\n")
        for idx, a in enumerate(accounts, 1):
            f.write(f"{idx:>3}. {a}\n")

def log_print(msg, log_f):
    print(msg)
    log_f.write(msg + '\n')
    log_f.flush()

# Main function to search all fire hashtags and accounts

def main():
    # Only use combination search (state + fire keyword) and account searches
    combinations = get_all_fire_search_combinations()
    accounts = get_all_fire_accounts()
    searched = set()
    queries = []
    # Combination searches (live only)
    for combo in combinations:
        mode = "live"
        key = (combo.lower(), mode)
        if key not in searched:
            queries.append((combo, mode, 4))
            searched.add(key)
    # Account searches (live only)
    for account in accounts:
        mode = "live"
        query = f'from:{account}'
        key = (query.lower(), mode)
        if key not in searched:
            queries.append((query, mode, 4))
            searched.add(key)
    # Remove duplicate queries (by query string and mode)
    unique_queries = []
    seen = set()
    for q, mode, scroll_times in queries:
        key = (q.lower(), mode)
        if key not in seen:
            unique_queries.append((q, mode, scroll_times))
            seen.add(key)
    save_logs(unique_queries, combinations, accounts)
    batch_size = 6
    from selenium.common.exceptions import WebDriverException
    import time
    import random
    scraping_failed = False
    with open(SCRAPE_LOG, "w", encoding="utf-8") as log_f:
        driver = setup_driver()
        twitter_login(driver)
        for batch_start in range(0, len(unique_queries), batch_size):
            batch = unique_queries[batch_start:batch_start+batch_size]
            # Open tabs for this batch
            for _ in range(len(batch) - 1):
                driver.execute_script("window.open('about:blank', '_blank');")
            for i, (query, mode, scroll_times) in enumerate(batch):
                log_print(f"\nProcessing tab {i+1+batch_start}/{len(unique_queries)}: {query} (mode: {mode})", log_f)
                # Retry logic for network errors
                max_retries = 3
                for attempt in range(1, max_retries + 1):
                    try:
                        scrape_recent_tweets_for_query(driver, query, mode=mode, scroll_times=scroll_times, tab_index=i, log_f=log_f)
                        break  # Success, exit retry loop
                    except WebDriverException as e:
                        if "net::ERR_NAME_NOT_RESOLVED" in str(e):
                            log_print(f"Network error on attempt {attempt} for query '{query}'. Retrying...", log_f)
                            time.sleep(5)
                        else:
                            log_print(f"WebDriverException for query '{query}': {e}", log_f)
                            break  # Don't retry for other errors
                    except Exception as e:
                        log_print(f"Unexpected error for query '{query}': {e}", log_f)
                        break
                else:
                    log_print(f"Failed to load query '{query}' after {max_retries} attempts. Stopping all further scraping.", log_f)
                    scraping_failed = True
                    break
                time.sleep(random.uniform(2, 4))
            # Close all but the first tab to prepare for next batch
            handles = driver.window_handles
            for h in handles[1:]:
                driver.switch_to.window(h)
                driver.close()
            driver.switch_to.window(driver.window_handles[0])
            if scraping_failed:
                break
        driver.quit()
        # Do not clean the raw JSON automatically
        # clean_tweets_json()  # <-- Not called
        from ai_fire_verifier import verify_and_save_to_excel
        verify_and_save_to_excel(OUTPUT_RAW_FILE)

us_states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
    "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
    "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
    "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

major_us_cities = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas",
    "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis",
    "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville", "Detroit", "Oklahoma City", "Portland",
    "Las Vegas", "Memphis", "Louisville", "Baltimore", "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Sacramento",
    "Mesa", "Kansas City", "Atlanta", "Omaha", "Colorado Springs", "Raleigh", "Miami", "Long Beach", "Virginia Beach",
    "Oakland", "Minneapolis", "Tulsa", "Tampa", "Arlington"
]



# US states and major cities for filtering
US_LOCATIONS = us_states + major_us_cities


# Fire incident/damage keywords
FIRE_INCIDENT_KEYWORDS = [
    "burn", "evacuate", "evacuation", "damage", "destroy", "blaze", "smoke", "flames", "emergency", "brushfire", "structure fire", "forest fire", "house fire", "apartment fire", "building fire", "outbreak", "spread"
]

# Structure/damage keywords for fire incidents
STRUCTURE_DAMAGE_KEYWORDS = [
    "structure fire", "building fire", "house fire", "apartment fire", "commercial fire", "warehouse fire", "residential fire", "industrial fire", "office fire", "school fire", "church fire", "hospital fire", "barn fire", "garage fire", "hotel fire", "motel fire", "condo fire", "duplex fire", "multi-family fire", "business fire", "restaurant fire", "store fire", "shopping center fire", "mall fire",
    "destroyed", "damaged", "total loss", "collapsed", "evacuated"
]


def is_today_or_yesterday(iso_timestamp):
    try:
        tweet_time = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        now = datetime.now(tweet_time.tzinfo)
        today = now.date()
        yesterday = today - timedelta(days=1)
        return tweet_time.date() in (today, yesterday)
    except Exception:
        return False

def tweet_mentions_fire_and_us_location_and_structure_damage(tweet):
    content = tweet.get("content", "").lower()
    # Check for fire/damage keywords
    fire_present = any(kw in content for kw in FIRE_INCIDENT_KEYWORDS)
    # Check for structure/damage keywords
    structure_damage_present = any(kw in content for kw in STRUCTURE_DAMAGE_KEYWORDS)
    # Check for US location
    location_present = any(loc.lower() in content for loc in US_LOCATIONS)
    return fire_present and structure_damage_present and location_present

def clean_tweets_json():
    tweets = load_existing_tweets(raw=True)
    cleaned = [tw for tw in tweets if (
        is_today_or_yesterday(tw.get("timestamp", "")) and
        ((any(kw in tw.get("content", "").lower() for kw in FIRE_INCIDENT_KEYWORDS) or
          any(kw in tw.get("content", "").lower() for kw in STRUCTURE_DAMAGE_KEYWORDS)) or
         any(loc.lower() in tw.get("content", "").lower() for loc in US_LOCATIONS))
    )]
    with open(OUTPUT_CLEANED_FILE, "w", encoding="utf-8") as file:
        json.dump(cleaned, file, indent=4, ensure_ascii=False)
    print(f"🧹 Cleaned tweets_cleaned.json: {len(cleaned)} relevant tweets remain.")

def threaded_scrape(driver, query, mode, scroll_times, tab_index):
    try:
        scrape_recent_tweets_for_query(driver, query, mode=mode, scroll_times=scroll_times, tab_index=tab_index)
    except Exception as e:
        print(f"Thread error for query '{query}': {e}")

if __name__ == "__main__":
    main() 