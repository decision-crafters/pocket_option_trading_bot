import pandas as pd

# Read data from CSV file
df = pd.read_csv('sentiment_data.csv', header=None, names=['Currency', 'Sentiment'])

# Create DataFrame from sample data
df = pd.DataFrame(df)

# Corrected function to determine the action
def determine_action(sentiment1, sentiment2):
    if sentiment1 == "Somewhat_Bullish" and sentiment2 == "Bearish":
        return "Buy"
    elif sentiment1 == "Bearish" and sentiment2 == "Somewhat_Bullish":
        return "Sell"
    elif sentiment1 == "Somewhat_Bearish" and sentiment2 == "Somewhat_Bullish":
        return "Buy"
    elif sentiment1 == "Somewhat_Bullish" and sentiment2 == "Somewhat_Bearish":
        return "Sell"
    elif sentiment1 == "Neutral" or sentiment2 == "Neutral":
        return "Neutral"
    elif sentiment1 == "Somewhat_Bullish" and sentiment2 == "Somewhat_Bullish":
        return "Buy"
    elif sentiment1 == "Somewhat_Bearish" and sentiment2 == "Somewhat_Bearish":
        return "Sell"
    else:
        return "Neutral"

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

#import ace_tools as tools; tools.display_dataframe_to_user(name="Tested Sentiment Analysis with Trading Considerations", dataframe=result_df)

# Export to CSV
result_df.to_csv('output.csv', index=False)

# Display the DataFrame to the user (for visualization purposes, can be removed if not needed)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
print(result_df)