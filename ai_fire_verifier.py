import os
import json
import openai
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
from openpyxl import load_workbook
from datetime import datetime, timedelta

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai

def is_today_or_yesterday(iso_timestamp):
    try:
        tweet_time = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        now = datetime.now(tweet_time.tzinfo)
        today = now.date()
        yesterday = today - timedelta(days=1)
        return tweet_time.date() in (today, yesterday)
    except Exception:
        return False

def get_fire_related_score(content):
    prompt = (
        "On a scale of 0 to 10, how strongly is the following tweet related to fire damages or destruction in the United States? "
        "A score of 0 means not related at all, 10 means it is definitely about fire damages or destruction in the USA. "
        "Only use the tweet content for your evaluation.\n\n"
        f"Tweet content: {content[:2000]}"
    )
    messages = [
        {"role": "system", "content": "You are an AI that rates the fire-relatedness of tweets about fire damages or destruction in the USA. Respond with a single integer from 0 to 10."},
        {"role": "user", "content": prompt}
    ]
    try:
        ai_response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            temperature=0,
        )
        answer = ai_response.choices[0].message.content.strip()
        # Extract the first integer in the answer
        import re
        match = re.search(r'\b(10|[0-9])\b', answer)
        if match:
            return int(match.group(1))
        return answer
    except Exception as e:
        print(f"Error with OpenAI API (score): {e}")
        return ""

def verify_fire_incident(title, content, url, country="USA"):
    print(url)
    truncated_content = content[:4000]
    fire_incident_prompt = (
    "You are given the content of a tweet or news snippet. Determine if it describes an unintended or accidental fire incident in the United States that caused damage to physical structures (such as homes, apartments, offices, commercial buildings, factories, or infrastructure). "
    "The fire must have resulted in clear structural damage or destruction, due to causes like electrical faults, negligence, accidents, natural disasters (e.g., wildfires), or arson.\n\n"
    "Respond with 'yes' only if the tweet/news explicitly mentions fire-related damage to physical structures. Otherwise, respond with 'no'.\n\n"
    f"Content: {truncated_content}\nURL: {url}\n"
    "Only use the provided content for your evaluation. Do not infer or assume details not present in the text."
)
    messages = [
        {
            "role": "system",
            "content": "You are an AI tasked with evaluating tweets to determine if they describe fire damages or destruction in the United States. Only tweets clearly about fire damages or destruction in the USA should be considered relevant."
        },
        {"role": "user", "content": fire_incident_prompt}
    ]
    try:
        ai_response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            temperature=0,
        )
        answer = ai_response.choices[0].message.content.strip()
        print(answer)
        return answer
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "no"

def autosize_excel_columns(excel_path):
    wb = load_workbook(excel_path)
    ws = wb.active
    for column_cells in ws.columns:
        max_length = 0
        column = column_cells[0].column_letter
        for cell in column_cells:
            try:
                cell_length = len(str(cell.value)) if cell.value else 0
                if cell_length > max_length:
                    max_length = cell_length
            except Exception:
                pass
        adjusted_width = min(max_length + 2, 80)  # Cap width for readability
        ws.column_dimensions[column].width = adjusted_width
    wb.save(excel_path)

def autosize_and_format_excel(excel_path):
    from openpyxl.utils import get_column_letter
    wb = load_workbook(excel_path)
    ws = wb.active
    default_width = 30
    # Set default column width and wrap text
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = default_width
        for cell in col:
            cell.alignment = cell.alignment.copy(wrap_text=True)
    # Auto-fit row height to content
    for row in ws.iter_rows():
        max_height = 15
        for cell in row:
            if cell.value:
                lines = str(cell.value).count("\n") + 1
                length = len(str(cell.value))
                # Estimate height: 15 per line, or more if long text
                est_height = max(15, min(150, lines * 15 + length // 50 * 15))
                if est_height > max_height:
                    max_height = est_height
        ws.row_dimensions[row[0].row].height = max_height
    # Make URL column clickable
    url_col = None
    for idx, cell in enumerate(ws[1], 1):
        if cell.value and str(cell.value).lower() == "url":
            url_col = idx
            break
    if url_col:
        for row in ws.iter_rows(min_row=2, min_col=url_col, max_col=url_col):
            for cell in row:
                if cell.value and str(cell.value).startswith("http"):
                    cell.hyperlink = cell.value
                    cell.style = "Hyperlink"
    wb.save(excel_path)


def verify_and_save_to_excel(cleaned_json_path, excel_path="verified_fires.xlsx"):
    with open(cleaned_json_path, "r", encoding="utf-8") as f:
        tweets = json.load(f)
    verified_rows = []
    for tweet in tqdm(tweets, desc="Verifying tweets with AI"):
        title = tweet.get("content", "")[:100]
        content = tweet.get("content", "")
        date = tweet.get("timestamp", "")
        url = tweet.get("tweet_url", "")
        source = tweet.get("username", "")
        verification_result = verify_fire_incident(title, content, url, country="USA")
        fire_related_score = get_fire_related_score(content) if verification_result.lower().startswith("yes") else 0
        verified_at = datetime.now().isoformat()
        if verification_result.lower().startswith("yes") and is_today_or_yesterday(date):
            verified_rows.append({
                "title": title,
                "content": content,
                "published_date": date,
                "url": url,
                "source": source,
                "fire_related_score": fire_related_score,
                "verification_result": verification_result,
                "verified_at": verified_at
            })
    if verified_rows:
        df = pd.DataFrame(verified_rows, columns=[
            "title", "content", "published_date", "url", "source", "fire_related_score", "verification_result", "verified_at"
        ])
        df.to_excel(excel_path, index=False)
        autosize_and_format_excel(excel_path)
        print(f"✅ Saved {len(verified_rows)} verified fire incidents to {excel_path}")
    else:
        print("No verified fire incidents found.")

if __name__ == "__main__":
    import sys
    # Default to 'tweets_cleaned.json' if no argument is given
    json_path = sys.argv[1] if len(sys.argv) > 1 else "tweets_cleaned.json"
    excel_path = "verified_fires.xlsx"
    verify_and_save_to_excel(json_path, excel_path) 