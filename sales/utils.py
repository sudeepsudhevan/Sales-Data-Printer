import json
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from django.conf import settings

def fetch_date_and_price(url="https://rubberboard.gov.in/public"):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract market date
    date_element = soup.select_one("#tabinfo > div.col-lg-13.rb-div-style1 > div.dark-green-head > h4")
    market_date = None
    if date_element:
        text = date_element.get_text().strip()
        match = re.search(r"\d{2}-\d{2}-\d{4}", text)
        if match:
            market_date = match.group(0)

    # Extract price
    price_element = soup.select_one("#loc1 > table > tbody > tr:nth-child(1) > td:nth-child(2) > i:nth-child(2)")
    price = None
    if price_element:
        raw_value = price_element.get_text().strip()
        price = float(raw_value) / 100

    return market_date, price

def get_today_date():
    return datetime.now().strftime("%Y-%m-%d")

def add_daily_entry(market_date, price, recorded_on, filename="daily_prices.json"):
    filepath = os.path.join(settings.BASE_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                daily_data = json.load(f)
            except json.JSONDecodeError:
                daily_data = []
    else:
        daily_data = []

    # Add new entry
    daily_data.append({
        "date": market_date,
        "price": price,
        "recorded_on": recorded_on
    })

    with open(filepath, "w") as f:
        json.dump(daily_data, f, indent=4)
    
    return daily_data[-1]

def ensure_todays_price():
    """
    Checks if today's price has been recorded. If not, fetches and records it.
    """
    filename = "daily_prices.json"
    filepath = os.path.join(settings.BASE_DIR, filename)
    today = get_today_date()
    
    # Check if run today
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                daily_data = json.load(f)
                if daily_data and isinstance(daily_data, list):
                    last_entry = daily_data[-1]
                    if last_entry.get("recorded_on") == today:
                        # Already recorded today
                        return last_entry
            except json.JSONDecodeError:
                pass

    # If not recorded or file broken/missing, fetch and add
    try:
        market_date, price = fetch_date_and_price()
        if market_date and price is not None:
            return add_daily_entry(market_date, price, today, filename)
    except Exception as e:
        print(f"Failed to fetch daily price: {e}")
        
    return None
