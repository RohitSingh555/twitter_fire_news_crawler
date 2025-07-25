# Twitter Fire News Crawler

This project is an automated pipeline for scraping, filtering, and verifying fire-related news and incident tweets in the United States. It uses Selenium to scrape Twitter for fire incidents, cleans and filters the data, and uses OpenAI's GPT models to verify and score the relevance of each tweet. The results are saved in a well-formatted Excel file for easy review and analysis.

---

## Features

- Scrapes recent tweets and news about fire incidents, structure fires, and related perils in high-risk US states.
- Searches using hashtags, keyword combinations, and follows relevant Twitter accounts.
- Cleans and filters tweets for recency and relevance.
- Uses OpenAI GPT to verify if a tweet is truly about a US fire incident with structural damage.
- Scores each tweet for fire-relatedness.
- Outputs a formatted Excel file with clickable links and readable columns.

---

## Requirements

- Python 3.8+
- Google Chrome browser
- ChromeDriver (managed automatically by `webdriver_manager`)
- Twitter account credentials (for login)
- OpenAI API key (for AI verification)

### Python Packages

- selenium
- webdriver_manager
- openpyxl
- pandas
- tqdm
- python-dotenv
- openai

Install all requirements with:

```bash
pip install -r requirements.txt
```

---

## Setup

1. **Clone the repository**
2. **Create a `.env` file** in the project root with your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. **Set your Twitter credentials** in `tweet_fire_search.py`:
   ```python
   TWITTER_USERNAME = "your_twitter_username"
   TWITTER_PASSWORD = "your_twitter_password"
   ```

---

## Usage

### 1. Scrape and Process Tweets

Run the main script to scrape, clean, and verify tweets:

```bash
python tweet_fire_search.py
```

- The script will log in to Twitter, open up to 6 tabs at a time, and search for all relevant hashtags, keyword combinations, and accounts.
- Tweets are saved to `tweets_raw.json` (all scraped) and `tweets_cleaned.json` (filtered for recency and relevance).

### 2. AI Verification and Excel Output

- After scraping and cleaning, the script uses OpenAI GPT to verify and score each tweet.
- Results are saved to `verified_fires.xlsx` with columns:
  - title, content, published_date, url (clickable), source, fire_related_score, verification_result, verified_at

### 3. Manual AI Verification (Optional)

You can run the AI verification separately on any cleaned JSON:

```bash
python ai_fire_verifier.py tweets_cleaned.json
```

---

## Customization

- **Keywords, hashtags, perils, and accounts** are all managed in `fire_search_targets.py`.
- **Batch size** for parallel tabs can be changed in `tweet_fire_search.py` (`batch_size = 6`).
- **Filtering and cleaning logic** can be adjusted in `tweet_fire_search.py`.

---

## Output Files

- `tweets_raw.json`: All scraped tweets.
- `tweets_cleaned.json`: Filtered tweets (recent, relevant).
- `verified_fires.xlsx`: Final, AI-verified and scored fire incident tweets in a formatted Excel file.

---

## Notes

- Excessive scraping or parallel logins may risk your Twitter account. Use responsibly.
- OpenAI API usage may incur costs depending on your plan and the number of tweets processed.
- For best results, keep your Chrome browser and ChromeDriver up to date.

---

## License

This project is for research and educational use. Please respect Twitter's and OpenAI's terms of service.
