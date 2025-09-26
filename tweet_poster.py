import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import tweepy
import time
import threading
import requests
import os
import json
from flask import Flask

# -------------------
# Flask dummy web server
# -------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Tweet poster is running!"

# -------------------
# Google Sheets setup
# -------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

service_account_info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)
sheet = client.open(os.environ.get("SHEET_NAME", "QuoteRetweets")).sheet1

# -------------------
# Quotes and hashtags
# -------------------
quotes_list = [
    "Wow! This is 🔥 https://s1d3l1n3media.com/memes",
    "Can’t believe this 🤯 https://s1d3l1n3media.com/memes",
    "Just dropped 👇 https://s1d3l1n3media.com/memes",
    "This one’s wild 😳 https://s1d3l1n3media.com/memes",
    "Must see 👀 https://s1d3l1n3media.com/memes",
    "No way 😂 https://s1d3l1n3media.com/memes",
    "Absolutely 🔥🔥🔥 https://s1d3l1n3media.com/memes",
    "I’m obsessed 🤩 https://s1d3l1n3media.com/memes",
    "Crazy vibes 😎 https://s1d3l1n3media.com/memes",
    "Lol this 💀 https://s1d3l1n3media.com/memes",
    "100% worth it ✅ https://s1d3l1n3media.com/memes",
    "This goes hard 🎶 https://s1d3l1n3media.com/memes",
    "New favorite 🚀 https://s1d3l1n3media.com/memes",
    "Can’t stop watching 👏 https://s1d3l1n3media.com/memes",
    "Game changer 💡 https://s1d3l1n3media.com/memes",
    "Pure 🔥 energy https://s1d3l1n3media.com/memes",
    "Too good 😂😂 https://s1d3l1n3media.com/memes",
    "Don’t sleep 😴 https://s1d3l1n3media.com/memes",
    "Legendary 👑 https://s1d3l1n3media.com/memes",
    "Instant classic 🎯 https://s1d3l1n3media.com/memes",
    "Sending this to everyone 📲 https://s1d3l1n3media.com/memes",
    "Viral vibes 📈 https://s1d3l1n3media.com/memes",
    "Mad respect 🙌 https://s1d3l1n3media.com/memes",
    "Love it 💖 https://s1d3l1n3media.com/memes",
    "This slaps 🎵 https://s1d3l1n3media.com/memes",
    "Too funny 😂🤣 https://s1d3l1n3media.com/memes",
    "Nah this is crazy 🤯 https://s1d3l1n3media.com/memes",
    "Big mood 😏 https://s1d3l1n3media.com/memes",
    "Shocked 😱 https://s1d3l1n3media.com/memes",
    "Instant 🔥🔥 https://s1d3l1n3media.com/memes",
    "No words 🤐 https://s1d3l1n3media.com/memes",
    "Stop scrolling ⏸️ https://s1d3l1n3media.com/memes",
    "Can’t unsee 😳 https://s1d3l1n3media.com/memes",
    "Classic 🤌 https://s1d3l1n3media.com/memes",
    "That part 💯 https://s1d3l1n3media.com/memes",
    "Wild clip 🎥 https://s1d3l1n3media.com/memes",
    "Major win 🏆 https://s1d3l1n3media.com/memes",
    "I’m crying 😂😭 https://s1d3l1n3media.com/memes",
    "Unbelievable 🤯 https://s1d3l1n3media.com/memes",
    "Forever iconic ✨ https://s1d3l1n3media.com/memes",
    "This cooked 💀🔥 https://s1d3l1n3media.com/memes",
    "Speechless 😶 https://s1d3l1n3media.com/memes",
    "No chill 🥶 https://s1d3l1n3media.com/memes",
    "This energy ⚡ https://s1d3l1n3media.com/memes",
    "Too real 😅 https://s1d3l1n3media.com/memes",
    "Laughing too hard 🤣 https://s1d3l1n3media.com/memes",
    "Sheeeesh 😮‍💨 https://s1d3l1n3media.com/memes",
    "All facts 📌 https://s1d3l1n3media.com/memes",
    "Absolutely dead 💀 https://s1d3l1n3media.com/memes",
    "Trendy af ✨ https://s1d3l1n3media.com/memes",
    "Look at this 👀🔥 https://s1d3l1n3media.com/memes",
    "Big vibes 🌊 https://s1d3l1n3media.com/memes",
    "This wins internet 🏅 https://s1d3l1n3media.com/memes"
]

hashtags_list = [
    "#trending", "#meme", "#memes", "#fyp", "#foryou",
    "#trendingnow", "#life", "#news", "#funny", "#lol",
    "#dankmemes", "#funnymemes", "#positivevibes", "#believe",
    "#positive", "#goodvibes", "#mindset", "#goals",
    "#behappy", "#dreambig", "#viral", "#viralvideo"
]

# -------------------
# Twitter API credentials
# -------------------
API_KEY = os.environ.get("TWITTER_API_KEY")
API_SECRET = os.environ.get("TWITTER_API_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# -------------------
# Safe Google Sheets update
# -------------------
def safe_update_cell(row, col, value):
    try:
        sheet.update_cell(row, col, value)
        time.sleep(2)  # throttle writes (avoid 429 quota exceeded)
    except Exception as e:
        print(f"Error updating cell {row},{col} -> {e}")

# -------------------
# Post one tweet from sheet
# -------------------
def post_next_tweet():
    rows = sheet.get_all_values()
    for idx, row in enumerate(rows[1:], start=2):
        posted = row[3].strip().upper() if len(row) > 3 else "FALSE"
        tweet_url = row[0].strip() if len(row) > 0 else None

        if posted != "FALSE" or not tweet_url:
            continue

        try:
            resp = requests.head(tweet_url, timeout=5)
            if resp.status_code != 200:
                print(f"Skipping invalid/deleted URL: {tweet_url}")
                safe_update_cell(idx, 4, "SKIPPED")
                continue
        except Exception as e:
            print(f"Error checking URL {tweet_url}: {e}")
            safe_update_cell(idx, 4, "SKIPPED")
            continue

        quote = row[1] if len(row) > 1 and row[1] else random.choice(quotes_list)
        hashtags = row[2] if len(row) > 2 and row[2] else " ".join(random.sample(hashtags_list, 2))

        status = f"{quote} {hashtags} {tweet_url}"

        try:
            api.update_status(status=status)
            safe_update_cell(idx, 4, "TRUE")
            print(f"Posted and marked TRUE: {tweet_url}")
        except Exception as e:
            print(f"Error posting {tweet_url} -> {e}")
            safe_update_cell(idx, 4, "SKIPPED")

        break

# -------------------
# Posting loop
# -------------------
def posting_loop():
    max_per_day = 100
    count = 0
    while count < max_per_day:
        post_next_tweet()
        count += 1
        time.sleep(900)  # wait 15 minutes between posts

# -------------------
# Main
# -------------------
if __name__ == "__main__":
    # Start background tweeting thread
    threading.Thread(target=posting_loop, daemon=True).start()
    print("Tweet posting loop started...")

    # Run Flask server (Render needs this for free plan)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

