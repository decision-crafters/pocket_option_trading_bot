import pandas as pd

# Read data from CSV file
df = pd.read_csv('sentiment_data.csv', header=None, names=['Currency', 'Sentiment'])

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
    else:
        return "Neutral"  # Change to Neutral if both are bullish or bearish

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

# Set display options to show all rows and columns
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)  # Increase the display width

# Apply styling to the DataFrame using map
styled_df = result_df.style

# Highlight 'Consider Buy Now' and 'Consider Sell Now' columns
styled_df.set_properties(**{'background-color': '#FFF', 'color': '#000', 'border': '1px solid #000'}) \
    .format({'Consider Trading Now': lambda x: 'background-color: yellow' if x == 'Yes' else '',
             'Consider Buy Now': lambda x: 'background-color: green' if x == 'Yes' else '',
             'Consider Sell Now': lambda x: 'background-color: red' if x == 'Yes' else ''})

# Display the styled DataFrame
print(styled_df)

# Alternatively, export to HTML
result_df.to_html('output.html')

