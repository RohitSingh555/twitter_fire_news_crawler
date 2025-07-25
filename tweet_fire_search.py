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
from fire_search_targets import get_all_fire_accounts, get_all_fire_search_combinations
from urllib.parse import quote
from datetime import datetime, timedelta, timezone
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

# Date string for filenames
DATE_STR = datetime.now().strftime('%d%b').lower()  # e.g., '24jul'

TWITTER_USERNAME = "TechWfm63921"
TWITTER_PASSWORD = "Pass@123"
OUTPUT_RAW_FILE = os.path.join(os.path.dirname(__file__), f"{DATE_STR}_tweets_raw.json")
# Remove unused OUTPUT_CLEANED_FILE

# Setup WebDriver

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Only set binary_location on Linux
    if sys.platform.startswith("linux"):
        chrome_options.binary_location = "/usr/bin/google-chrome"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def load_existing_tweets(raw=True):
    file_path = OUTPUT_RAW_FILE if raw else None
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def save_tweet(tweet_data, raw=True):
    file_path = OUTPUT_RAW_FILE if raw else None
    # Always reload, deduplicate, and overwrite
    existing_tweets = load_existing_tweets(raw=raw)
    # Remove any duplicate (by content, timestamp, and username)
    is_duplicate = any(
        tweet_data.get("content") == t.get("content") and
        tweet_data.get("timestamp") == t.get("timestamp") and
        tweet_data.get("username") == t.get("username")
        for t in existing_tweets
    )
    if not is_duplicate:
        existing_tweets.append(tweet_data)
    # Overwrite the file with deduplicated list
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(existing_tweets, file, indent=4, ensure_ascii=False)
    print(f"✅ Tweet saved: {tweet_data['content'][:50]}... (raw)")

def twitter_login(driver):
    driver.get("https://twitter.com/login")
    try:
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_input.send_keys(TWITTER_USERNAME)
        username_input.send_keys(Keys.RETURN)
        time.sleep(3)
        password_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(TWITTER_PASSWORD)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)
    except Exception as e:
        print(f"Error during Twitter login: {e}")
        print("Page source for debugging:")
        print(driver.page_source)
        raise

def scrape_recent_tweets_for_query(driver, query, max_tweets=10, scroll_times=4, mode="live", tab_index=0):
    encoded_query = quote(query)
    if mode == "live":
        search_url = f"https://twitter.com/search?q={encoded_query}&f=live"
    else:
        search_url = f"https://twitter.com/search?q={encoded_query}&f=top"
    driver.get(search_url)
    time.sleep(7)
    for _ in range(scroll_times):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(random.uniform(2, 4))
    tweet_elements = driver.find_elements(By.XPATH, "//article[@role='article']")
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
            save_tweet(tweet_data, raw=True)
            tweets_scraped += 1
        except Exception as e:
            print(f"⚠️ Skipping tweet due to error: {e}")
            continue

LOG_FILE = os.path.join(os.path.dirname(__file__), f"logs_{DATE_STR}.log")

def log_print(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def filter_tweets_last_72_hours(input_path, output_path):
    from datetime import datetime, timezone
    with open(input_path, "r", encoding="utf-8") as f:
        tweets = json.load(f)
    now = datetime.now(timezone.utc)
    filtered = []
    for tweet in tweets:
        ts = tweet.get("timestamp", "")
        content = tweet.get("content", "")
        try:
            tweet_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            within_72h = (now - tweet_time).total_seconds() <= 72 * 3600
            long_enough = len(content.strip()) >= 30
            log_print(f"[DEBUG] Tweet timestamp: {ts} | Now: {now.isoformat()} | Within 72h: {within_72h} | Content length: {len(content.strip())} | Long enough: {long_enough}")
            if within_72h and long_enough:
                filtered.append(tweet)
                # Save live after each addition
                with open(output_path, "w", encoding="utf-8") as f_out:
                    json.dump(filtered, f_out, indent=4, ensure_ascii=False)
        except Exception as e:
            log_print(f"[DEBUG] Error parsing timestamp '{ts}': {e}")
            continue
    log_print(f"Filtered {len(filtered)} tweets from last 72 hours to {output_path}")

def main():
    combinations = get_all_fire_search_combinations()
    accounts = get_all_fire_accounts()
    queries = []
    for combo in combinations:
        queries.append((combo, "live", 10))
    for account in accounts:
        query = f'from:{account}'
        queries.append((query, "live", 10))
    total_queries = len(queries)
    log_print(f"[INFO] Total queries to process: {total_queries}")
    log_print(f"[INFO] Starting Chrome WebDriver...")
    driver = setup_driver()
    log_print(f"[INFO] WebDriver started.")
    log_print(f"[INFO] Logging into Twitter...")
    twitter_login(driver)
    log_print(f"[INFO] Twitter login successful.")
    for idx, (query, mode, scroll_times) in enumerate(queries, 1):
        log_print(f"[INFO] Processing tab {idx}/{total_queries}: Query='{query}' | Mode={mode} | Scrolls={scroll_times}")
        scrape_recent_tweets_for_query(driver, query, mode=mode, scroll_times=scroll_times)
        log_print(f"[INFO] Finished processing tab {idx}/{total_queries}: Query='{query}'")
        time.sleep(random.uniform(2, 4))
    log_print(f"[INFO] Quitting WebDriver...")
    driver.quit()
    log_print(f"[INFO] WebDriver stopped.")
    RAW_PATH = OUTPUT_RAW_FILE
    CLEANED_PATH = os.path.join(os.path.dirname(__file__), f"{DATE_STR}_cleaned_tweets.json")
    log_print(f"[INFO] Filtering tweets from raw file to cleaned file...")
    filter_tweets_last_72_hours(RAW_PATH, CLEANED_PATH)
    log_print(f"[INFO] Running AI verifier on cleaned tweets...")
    from ai_fire_verifier import verify_and_save_to_excel
    verify_and_save_to_excel(CLEANED_PATH)
    log_print(f"[INFO] All steps complete.")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable is not set. Please set it before running the script.")
    exit(1)
else:
    masked_key = OPENAI_API_KEY[:4] + "*" * (len(OPENAI_API_KEY) - 8) + OPENAI_API_KEY[-4:]
    print(f"OPENAI_API_KEY loaded: {masked_key}")

if __name__ == "__main__":
    main() 