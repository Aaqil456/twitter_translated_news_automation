# Import required libraries
import os
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from webdriver_manager.chrome import ChromeDriverManager



# Function to fetch the latest hot news from CryptoPanic
def fetch_latest_hot_news(api_key):
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={api_key}&filter=hot"
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        if news_data.get("results", []):
            # Get the latest news item
            latest_news = news_data["results"][0]
            # Construct the "click" URL
            click_url = f"https://cryptopanic.com/news/click/{latest_news['id']}/"
            return {"title": latest_news["title"], "url": click_url}
        else:
            print("No hot news available.")
            return None
    else:
        print(f"Failed to fetch news: {response.status_code}")
        return None

# Function to translate text using Easy Peasy API
def translate_text_easypeasy(api_key, text):
    url = "https://bots.easy-peasy.ai/bot/e56f7685-30ed-4361-b6c1-8e17495b7faa/api"
    headers = {
        "content-type": "application/json",
        "x-api-key": api_key
    }
    payload = {
        "message": f"translate this title '{text}' into Malay language. Your job is just to translate this title into Malay.",
        "history": [],
        "stream": False
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("bot", {}).get("text", "Translation failed")
    else:
        print(f"Translation API error: {response.status_code}, {response.text}")
        return "Translation failed"

# Function to post tweets using Selenium in headless mode
def post_to_twitter_selenium(username, password, tweet):
    try:
        # Set up Selenium WebDriver with headless Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get("https://x.com/i/flow/login")
        time.sleep(5)

        # Log in to Twitter
        username_field = driver.find_element(By.NAME, "session[username_or_email]")
        password_field = driver.find_element(By.NAME, "session[password]")
        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)

        # Post the tweet
        tweet_box = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Tweet text']")
        tweet_box.send_keys(tweet)
        tweet_box.send_keys(Keys.CONTROL, Keys.ENTER)  # Post the tweet
        time.sleep(5)

        print(f"Tweet posted: {tweet}")
        driver.quit()
    except Exception as e:
        print(f"Error posting to Twitter: {e}")

# Main script
def main():
    # Fetch API keys from environment variables
    CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY")
    EASY_PEASY_API_KEY = os.getenv("EASY_PEASY_API_KEY")
    TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
    TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")

    # Ensure all required environment variables are available
    if not CRYPTOPANIC_API_KEY or not EASY_PEASY_API_KEY or not TWITTER_USERNAME or not TWITTER_PASSWORD:
        print("API keys or Twitter credentials are missing! Please set them as environment variables.")
        return

    # Step 1: Fetch the latest hot news
    print("Fetching the latest hot news from CryptoPanic...")
    latest_news = fetch_latest_hot_news(CRYPTOPANIC_API_KEY)

    if not latest_news:
        print("No latest hot news fetched. Exiting.")
        return

    # Step 2: Translate the news title
    print("Translating the latest news title...")
    malay_title = translate_text_easypeasy(EASY_PEASY_API_KEY, latest_news["title"])

    # Construct the tweet
    tweet = f"{malay_title}\nBaca lagi: {latest_news['url']}"

    # Ensure the tweet is within the character limit
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."

    # Step 3: Post the tweet using Selenium
    post_to_twitter_selenium(TWITTER_USERNAME, TWITTER_PASSWORD, tweet)

# Run the main script
if __name__ == "__main__":
    main()
