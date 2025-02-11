import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from pytrends.request import TrendReq

# Telegram Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Initialize Pytrends
pytrends = TrendReq(hl='en-US', tz=360)

# Define fashion brands to track
fashion_brands = ["gucci", "chanel", "dior", "prada", "louis vuitton"]

# Fetch data
pytrends.build_payload(fashion_brands, timeframe='today 12-m', geo='US')
trend_data = pytrends.interest_over_time()

# Remove isPartial column if present
if "isPartial" in trend_data.columns:
    trend_data = trend_data.drop(columns=["isPartial"])

# Calculate daily percentage change
percent_changes = trend_data.pct_change().iloc[-1] * 100

# Detect spikes (custom threshold)
spike_threshold = 30
spike_alerts = []
for brand in fashion_brands:
    change = percent_changes[brand]
    if change > spike_threshold:
        spike_alerts.append(f"🚨 TREND ALERT! '{brand.title()}' spiked by {change:.2f}%!")

# Format stock market-like report
summary = "📊 **Daily Fashion Trend Update** 📊\n\n"
for brand in fashion_brands:
    change = percent_changes[brand]
    emoji = "🔺" if change > 0 else "🔻"
    summary += f"{emoji} {brand.title()}: {change:.2f}%\n"

# Append trend alerts if any
if spike_alerts:
    summary += "\n🔥 **TRENDING NOW:** 🔥\n" + "\n".join(spike_alerts)

# Save trend graph
plt.figure(figsize=(12, 6))
trend_data.plot()
plt.title("Fashion Search Trends Over Time")
plt.xlabel("Date")
plt.ylabel("Search Interest")
plt.legend(fashion_brands, bbox_to_anchor=(1.05, 1), loc="upper left")
plt.grid()
plt.savefig("trend_report.png", bbox_inches="tight")

# Function to send Telegram notification
def send_telegram_message():
    # Send text summary
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": summary})

    # Send trend report image
    url_photo = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open("trend_report.png", "rb") as photo:
        requests.post(url_photo, data={"chat_id": TELEGRAM_CHAT_ID}, files={"photo": photo})

    print("📲 Telegram notification sent!")

# Run the script
if __name__ == "__main__":
    send_telegram_message()
