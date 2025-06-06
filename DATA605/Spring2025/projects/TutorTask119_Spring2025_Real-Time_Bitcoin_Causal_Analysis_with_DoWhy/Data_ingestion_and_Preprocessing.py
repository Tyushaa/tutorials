# -*- coding: utf-8 -*-
"""Data_Ingestion & Preprocessing.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1lizrNh-fqTJmGhusOsFjmIHRRgz-3q_L
"""

# bitcoin_utils.py
import requests
import pandas as pd
from datetime import datetime
import os

def fetch_bitcoin_price():
    """
    Fetches the current Bitcoin price in USD from CoinGecko API.
    Returns:
        float: Current BTC price or None if request fails.
    """
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {'ids': 'bitcoin', 'vs_currencies': 'usd'}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        price = response.json()['bitcoin']['usd']
        return price
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API request failed: {e}")
        return None

def record_price(output_path="data/bitcoin_prices.csv"):
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    price = fetch_bitcoin_price()
    if price is None:
        print("[WARNING] Skipping write due to failed fetch.")
        return

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    row = pd.DataFrame([[timestamp, price]], columns=["timestamp_utc", "price_usd"])

    # Write or append
    if not os.path.exists(output_path):
        row.to_csv(output_path, index=False)
    else:
        row.to_csv(output_path, mode='a', header=False, index=False)

    # ✅ Add this here — runs in both cases
    print(f"[{timestamp}] ✅ BTC Price: ${price:.2f} logged")
    print(f"📁 Saved to: {os.path.abspath(output_path)}")  # << ADD THIS


# main.py
import time


def main():
    print("\n📈 Real-Time Bitcoin Price Logger")
    print("=====================================")
    print("Fetching data from CoinGecko every 30 seconds...\n")

    try:
        while True:
            record_price()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n⛔️ Logging stopped manually. Goodbye!")

if __name__ == "__main__":
    main()

if df.empty:
    print("⚠️ Dataframe is empty. No data to plot.")
else:
    # plotting code here...

   import pandas as pd
   import matplotlib.pyplot as plt

   df = pd.read_csv("data/bitcoin_prices.csv")
   df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])

   plt.figure(figsize=(10, 4))
   plt.plot(df["timestamp_utc"], df["price_usd"], label="BTC Price")
   plt.title("Live Bitcoin Price Feed (So Far)")
   plt.xlabel("Time (UTC)")
   plt.ylabel("Price (USD)")
   plt.grid(True)
   plt.legend()
   plt.tight_layout()
   plt.show()

import pandas as pd
from datetime import datetime

# Load your streaming data
df = pd.read_csv("data/bitcoin_prices.csv")
df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])

# Show basic info
print("\n📊 Dataset Summary:")
print(df.tail())

# -------------------------------
# 🧨 Step 1: Define Market Event
# -------------------------------
# You can change this to a real event timestamp if available
event_time = pd.to_datetime("2025-05-02 13:00:00")

# Create 'event' column (binary treatment)
df["event"] = (df["timestamp_utc"] >= event_time).astype(int)

# -------------------------------
# 📉 Step 2: Simulate a Confounder
# -------------------------------
# Here: rolling average of last 3 prices
df["volume"] = df["price_usd"].rolling(window=3, min_periods=1).mean()

# Optional: Save processed data to new CSV
df.to_csv("data/processed_data.csv", index=False)

print("\n✅ Processed dataset with 'event' and 'volume' columns created.")
print(df.tail())

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 4))
plt.plot(df["timestamp_utc"], df["price_usd"], label="BTC Price")
plt.axvline(event_time, color="red", linestyle="--", label="Injected Event")
plt.title("Bitcoin Price Around Event")
plt.xlabel("Time (UTC)")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()