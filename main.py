import requests
import time
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TRUMP_USER_ID = os.getenv("TRUTH_USER_ID", "107780257626128497")

# Simple keyword lists for beginner level
BULL_KEYWORDS = ["great economy", "strong economy", "record high", "beautiful", "winning", "boom"]
BEAR_KEYWORDS = ["tariff", "tariffs", "china", "bad economy", "terrible", "crash", "fed", "rate hike"]

last_post_id = None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except:
        print("Telegram failed")

def get_latest_truth():
    # Using a simple public endpoint approach (works as of 2026 for basic use)
    # For more reliable, you can later switch to Apify or truthbrush library
    url = f"https://truthsocial.com/api/v1/accounts/{TRUMP_USER_ID}/statuses?limit=1"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            posts = r.json()
            if posts:
                return posts[0]
    except:
        pass
    return None

def analyze_signal(text):
    text_lower = text.lower()
    
    bull_score = sum(1 for word in BULL_KEYWORDS if word in text_lower)
    bear_score = sum(1 for word in BEAR_KEYWORDS if word in text_lower)
    
    if bull_score > bear_score:
        return "🚀 <b>BULL SIGNAL</b> for MNQ"
    elif bear_score > bull_score:
        return "🔻 <b>BEAR SIGNAL</b> for MNQ"
    else:
        return "➡️ NEUTRAL - Trump posted"

def main():
    global last_post_id
    print("Trump MNQ Alert Bot started... (Ctrl+C to stop)")
    
    while True:
        post = get_latest_truth()
        
        if post and post.get("id") != last_post_id:
            last_post_id = post.get("id")
            text = post.get("content", "").replace("<br>", "\n").strip()
            created_at = post.get("created_at", "")
            
            signal = analyze_signal(text)
            
            alert = f"""
🔔 <b>New Trump Truth</b>

{signal}

📝 {text}

🕒 {created_at}
            """.strip()
            
            send_telegram(alert)
            print(f"[{datetime.now()}] Alert sent!")
        
        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    main()
