import os
import pandas as pd
import requests
from openai import OpenAI
import datetime

# Read data from CSV file
df = pd.read_csv('sentiment_data.csv', header=None, names=['Currency', 'Sentiment'])

# Create DataFrame from sample data
df = pd.DataFrame(df)

# Corrected function to determine the action
def determine_action(sentiment1, sentiment2):
    # Define the strength of sentiment (this can be adjusted based on your analysis)
    sentiment_strength = {'Bearish': 1, 'Somewhat-Bearish': 2, 'Somewhat_Bearish': 2, 'Neutral': 3, 'Somewhat_Bullish': 4, 'Bullish': 5}
    
    # Determine the action based on the relative strength of sentiment
    if sentiment_strength[sentiment1] > sentiment_strength[sentiment2]:
        return "Buy"  # Buy the currency with stronger bullish sentiment
    elif sentiment_strength[sentiment1] < sentiment_strength[sentiment2]:
        return "Sell"  # Sell the currency with stronger bearish sentiment
    else:
        return "Neutral"  # Sentiments are equal or one is neutral; no clear action

# Adjust the rest of the code to use this logic and re-run the analysis

# Create list to hold data
pair_data = []

# Populate list with pair data
for index, row in df.iterrows():
    for index2, row2 in df.iterrows():
        if row['Currency'] != row2['Currency']:
            action = determine_action(row['Sentiment'], row2['Sentiment'])
            pair_data.append({
                "Currency 1": row['Currency'],
                "Sentiment 1": row['Sentiment'],
                "Currency 2": row2['Currency'],
                "Sentiment 2": row2['Sentiment'],
                "Action": action
            })

# Create DataFrame from list
result_df = pd.DataFrame(pair_data)

# Add the 'Consider Trading Now' column based on the 'Buy' and 'Sell' options
result_df['Consider Trading Now'] = result_df['Action'].apply(lambda x: 'Yes' if x in ['Buy', 'Sell'] else 'No')

# Add the 'Consider Buy Now' column based on the 'Buy' options
result_df['Consider Buy Now'] = result_df['Action'].apply(lambda x: 'Yes' if x == 'Buy' else 'No')

# Add the 'Consider Sell Now' column based on the 'Sell' options
result_df['Consider Sell Now'] = result_df['Action'].apply(lambda x: 'Yes' if x == 'Sell' else 'No')

# Export to CSV
result_df.to_csv('output.csv', index=False)

# Function to generate report using OpenAI SDK
def generate_report(dataframe):
    client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

    now = datetime.datetime.now()
    prompt = f"Assume the role of a forex financial analyst providing a report of trade recommendations for {now.strftime('%Y-%m-%d %H:%M')} based off news sentiment. "
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": prompt + "\n\n" + dataframe.to_string()}
    ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )

    return response.choices[0].message.content

# Generate report
report = generate_report(result_df)

# Save or print the report
with open('report.txt', 'w') as file:
    file.write(report)

print("Report generated and saved as 'report.txt'")
print(report)
print("Output data saved as 'output.csv'")
print(result_df)
