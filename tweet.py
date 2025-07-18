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

# 🔹 Twitter Credentials
TWITTER_USERNAME = "TechWfm63921"
TWITTER_PASSWORD = "Pass@123"

# 🔹 Output File
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "tweets.json")

# 🔹 Setup WebDriver
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# 🔹 Load Existing Tweets
def load_existing_tweets():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []  # Return empty list if file is corrupt
    return []

# 🔹 Save Tweets to File (Continuous)
def save_tweet(tweet_data):
    existing_tweets = load_existing_tweets()

    if tweet_data not in existing_tweets:
        existing_tweets.append(tweet_data)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(existing_tweets, file, indent=4, ensure_ascii=False)

        print(f"✅ Tweet saved: {tweet_data['content'][:50]}...")

# 🔹 Twitter Login
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
    time.sleep(5)  # Wait for login

# 🔹 Scrape Tweets Continuously
def scrape_tweets():
    driver = setup_driver()
    twitter_login(driver)

    search_url = "https://twitter.com/search?q=fire%20USA&f=live"
    driver.get(search_url)
    time.sleep(5)

    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0

    while True:
        time.sleep(random.uniform(3, 5))
        tweet_elements = driver.find_elements(By.XPATH, "//article[@role='article']")

        for tweet in tweet_elements:
            try:
                username = tweet.find_element(By.XPATH, ".//div[@dir='ltr']/span").text
                content = tweet.find_element(By.XPATH, ".//div[@lang]").text
                timestamp = tweet.find_element(By.XPATH, ".//time").get_attribute("datetime")

                # 🔹 Extract Tweet URL
                try:
                    tweet_url = "https://twitter.com" + tweet.find_element(By.XPATH, ".//time/parent::a").get_attribute("href")
                except:
                    tweet_url = "URL Not Found"

                # 🔹 Handle missing retweets/likes
                try:
                    retweets = tweet.find_element(By.XPATH, ".//div[@data-testid='retweet']").get_attribute("textContent") or "0"
                except:
                    retweets = "0"  # Default if missing

                try:
                    likes = tweet.find_element(By.XPATH, ".//div[@data-testid='like']").get_attribute("textContent") or "0"
                except:
                    likes = "0"  # Default if missing

                media = tweet.find_elements(By.XPATH, ".//img[contains(@src, 'twimg')]")
                media_urls = [img.get_attribute("src") for img in media]

                tweet_data = {
                    "username": username,
                    "content": content,
                    "timestamp": timestamp,
                    "tweet_url": tweet_url,  # ✅ Added Tweet URL
                    "retweets": retweets,
                    "likes": likes,
                    "media": media_urls
                }

                # 🔹 Save each tweet immediately
                save_tweet(tweet_data)

            except Exception as e:
                print(f"⚠️ Skipping tweet due to error: {e}")
                continue

        # 🔹 Scroll Down
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(random.uniform(2, 4))

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
            if scroll_attempts > 3:
                print("🚀 No more tweets to load. Stopping.")
                break
        else:
            scroll_attempts = 0  # Reset attempts if new tweets load
        last_height = new_height

    driver.quit()

# 🔹 Run Script
if __name__ == "__main__":
    scrape_tweets()
