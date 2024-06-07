import os
import requests
import time
import csv

def analyze_sentiment(json_response, target_ticker):
    print(f"Starting sentiment analysis for ticker: {target_ticker}")
    
    if not json_response or "feed" not in json_response:
        print("No valid data in JSON response.")
        return "No data available for analysis"

    sentiment_label = "Neutral"  # Default sentiment if no stronger signals found
    highest_relevance = 0  # Track the highest relevance score

    for item in json_response.get("feed", []):
        for ticker_data in item.get("ticker_sentiment", []):
            if ticker_data["ticker"] == "FOREX:"+str(target_ticker):
                relevance_score = float(ticker_data.get("relevance_score", 0))
                sentiment_score = float(ticker_data.get("ticker_sentiment_score", 0))
                
                if relevance_score > highest_relevance:
                    highest_relevance = relevance_score
                    if sentiment_score <= -0.35:
                        sentiment_label = "Bearish"
                    elif -0.35 < sentiment_score <= -0.15:
                        sentiment_label = "Somewhat-Bearish"
                    elif -0.15 < sentiment_score < 0.15:
                        sentiment_label = "Neutral"
                    elif 0.15 <= sentiment_score < 0.35:
                        sentiment_label = "Somewhat_Bullish"
                    elif sentiment_score >= 0.35:
                        sentiment_label = "Bullish"
                    print(f"Updated sentiment label to {sentiment_label} based on relevance and score")

    print(f"Final sentiment label for {target_ticker}: {sentiment_label}")
    return sentiment_label

def fetch_sentiment_data(api_endpoint, ticker, api_key, sort='LATEST', limit=50):
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': ticker,
        'apikey': api_key,
        'sort': sort,
        'limit': limit
    }
    response = requests.get(api_endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error fetching data: {response.status_code}"
    
api_endpoint = "https://www.alphavantage.co/query"
api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
tickers = ["EUR", "USD", "JPY", "GBP", "CAD", "AUD", "CHF", "NZD", "RUB"]

for base_ticker in tickers:
    print(f"Fetching sentiment data for: {base_ticker}")
    json_response = fetch_sentiment_data(api_endpoint, "FOREX:"+base_ticker, api_key)
    if json_response is None:
        print("Failed to fetch sentiment data.")
    base_sentiment = analyze_sentiment(json_response, base_ticker)
    with open('sentiment_data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([base_ticker, base_sentiment])
        print(f"Sentiment for {base_ticker}: {base_sentiment}")
        print("Sentiment data saved to CSV file.")
    time.sleep(30)
