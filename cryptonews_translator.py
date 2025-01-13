# Import required libraries
import os
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
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

# Function to save cookies after manual login
def save_cookies(username, password):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://x.com/i/flow/login")
    time.sleep(5)

    # Log in manually
    try:
        print("Finding username field...")
        username_field = driver.find_element(By.NAME, "text")
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)
        time.sleep(5)

        print("Finding password field...")
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)

        if "home" in driver.current_url:
            print("Login successful! Saving cookies...")
            with open("cookies.pkl", "wb") as file:
                pickle.dump(driver.get_cookies(), file)
            print("Cookies saved successfully.")
        else:
            print("Login failed. Please check credentials or security prompts.")
            driver.save_screenshot("login_failed.png")
    except Exception as e:
        print("Error during manual login:", e)
    finally:
        driver.quit()

# Function to load cookies and post a tweet
def post_to_twitter_with_cookies(tweet):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://x.com")
    time.sleep(5)

    # Load cookies
    try:
        with open("cookies.pkl", "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("Cookies loaded successfully.")
    except FileNotFoundError:
        print("Cookies file not found. Please log in manually to save cookies first.")
        driver.quit()
        return

    # Refresh the page to apply cookies
    driver.refresh()
    time.sleep(5)

    # Verify login persistence
    if "home" in driver.current_url:
        print("Persistent login successful. Ready to post tweet.")
    else:
        print("Persistent login failed. Please log in again to update cookies.")
        driver.save_screenshot("persistent_login_failed.png")
        driver.quit()
        return

    # Post the tweet
    try:
        print("Finding tweet box...")
        tweet_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Tweet text']"))
        )
        tweet_box.send_keys(tweet)
        tweet_box.send_keys(Keys.CONTROL, Keys.ENTER)  # Post the tweet
        time.sleep(5)
        print(f"Tweet posted: {tweet}")
    except Exception as e:
        print("Error posting tweet:", e)
        driver.save_screenshot("error_posting_tweet.png")
    finally:
        driver.quit()

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

    # Step 3: Post the tweet using cookies
    post_to_twitter_with_cookies(tweet)

# Uncomment the line below to save cookies initially
# save_cookies("your_twitter_username", "your_twitter_password")

# Run the main script
if __name__ == "__main__":
    main()
