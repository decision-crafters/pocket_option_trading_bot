import base64
import json
import random
import time
import requests
import os
import sys
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


BASE_URL = 'https://pocketoption.com'  # change if PO is blocked in your country
LENGTH_STACK_MIN = 750  # Increased from 500 to consider more data for each decision
LENGTH_STACK_MAX = 3500  # Increased to allow a broader historical context
PERIOD = 5  # PERIOD on the graph
TIME = 1  # quotes
SMA_LONG = 50
SMA_SHORT = 8
PERCENTAGE = 0.91 # 0.91  # create orders more than PERCENTAGE
STACK = {}  # {1687021970: 0.87, 1687021971: 0.88}
ACTIONS = {}  # dict of {datetime: value} when an action has been made
MAX_ACTIONS = 50 # maximum number of actions
MAX_ALLOWED_FAIL_RATE = 0.3  # Set this value based on your desired failure rate (e.g., 30%)
ACTIONS_SECONDS = PERIOD - 25  # how long action still in ACTIONS
LAST_REFRESH = datetime.now()
CURRENCY = None
CURRENCY_CHANGE = False
CURRENCY_CHANGE_DATE = datetime.now()
HISTORY_TAKEN = False  # becomes True when history is taken. History length is 900-1800
CLOSED_TRADES_LENGTH = 3
HEADER = [
    # '00',
    # '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
    # '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
    # '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
    # '31', '32', '33', '34', '35', '36', '37', '38', '39', '40',
    # '41', '42', '43', '44', '45', '46', '47', '48', '49', '50',
    'adx',
    'pdi',
    'mdi',
    'rsi',
    'trend',
    'psar',
    'aroon_up',
    'aroon_down',
    'oscillator',
    'vortex_pvi',
    'vortex_nvi',
    'stoch_rsi',
    'stoch_signal',
    'macd',
    'macd_signal',
    'profit',
]
MODEL = None
SCALER = None
PREVIOUS = 0
MAX_DEPOSIT = 0
MIN_DEPOSIT = 45
PROFIT_GOAL = 88  #92 88 
INIT_DEPOSIT = None
NUMBERS = {
    '0': '11',
    '1': '7',
    '2': '8',
    '3': '9',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '1',
    '8': '2',
    '9': '3',
}
IS_AMOUNT_SET = True
AMOUNTS = [  3, 6, 9 ]  # 1, 3, 8, 18, 39, 82, 172
EARNINGS = 15  # euros.
MARTINGALE_COEFFICIENT = 2.0  # everything < 2 have worse profitability

options = Options()
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
options.add_argument('--ignore-ssl-errors')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-certificate-errors-spki-list')
#options.add_argument(r'--user-data-dir=/Users/tosinakinosho/Library/Application Support/Google/Chrome/Default')
# chromedriver can be downloaded from here: https://googlechromelabs.github.io/chrome-for-testing/
service = Service(executable_path=r'/home/tosinakinosho/workspace/pocket_option_trading_bot/chrome-linux64/chromedriver')
driver = webdriver.Chrome(options=options, service=service)
companies = {
    'AUD/USD OTC': 'AUDUSD_otc',
    'EUR/USD OTC': 'EURUSD_otc',
    'GBP/USD OTC': 'GBPUSD_otc',
    'USD/JPY OTC': 'USDJPY_otc',
    'USD/CAD OTC': 'USDCAD_otc',
    'USD/CHF OTC': 'USDCHF_otc',
    'USD/RUB OTC': 'USDRUB_otc',
    'USD/JPY': 'USDJPY',
    'EUR/USD': 'EURUSD',
    'GBP/USD': 'GBPUSD',
    'USD/CAD': 'USDCAD',
    'Apple OTC': '#AAPL_otc',
    'American Express OTC': '#AXP_otc',
    'Boeing Company OTC': '#BA_otc',
    'Johnson & Johnson OTC': '#JNJ_otc',
    "McDonald's OTC": '#MCD_otc',
    'Tesla OTC': '#TSLA_otc',
    'Amazon OTC': 'AMZN_otc',
    'VISA OTC': 'VISA_otc',
    'Netflix OTC': 'NFLX_otc',
    'Alibaba OTC': 'BABA_otc',
    'ExxonMobil OTC': '#XOM_otc',
    'FedEx OTC': 'FDX_otc',
    'FACEBOOK INC OTC': '#FB_otc',
    'Pfizer Inc OTC': '#PFE_otc',
    'Intel OTC': '#INTC_otc',
    'TWITTER OTC': 'TWITTER_otc',
    'Microsoft OTC': '#MSFT_otc',
    'Cisco OTC': '#CSCO_otc',
    'Citigroup Inc OTC': 'CITI_otc',
    'AUD/USD OTC': 'AUDUSD_otc'
}

def make_trade_decision(base_currency, quote_currency, quote_sentiment, base_sentiment):
    """
    Make a trade decision based on sentiment analysis and forex signal parameters.
    
    :param quote_sentiment: Sentiment analysis result for {base_currency}.
    :param base_sentiment: Sentiment analysis result for {quote_currency}.
    :param entry: Entry price for the trade.
    :param stop_loss: Stop loss price.
    :param take_profit: Take profit price.
    :return: A decision to make the trade or not, along with sentiment analysis results.
    """
    trade_decision = "No trade"
    decision_reason = f"{base_currency} Sentiment: {quote_sentiment}, {quote_currency} Sentiment: {base_sentiment}"

    # Adjust the logic to account for somewhat bullish/bearish sentiments
    bullish_sentiments = ["Bullish", "Somewhat_Bullish"]
    bearish_sentiments = ["Bearish", "Somewhat-Bearish"]

    if quote_sentiment in bullish_sentiments and base_sentiment not in bullish_sentiments:
        trade_decision = f"Sell {base_currency}/{quote_currency}"
    elif base_sentiment in bullish_sentiments and quote_sentiment not in bullish_sentiments:
        trade_decision = f"Buy {base_currency}/{quote_currency}"
    elif quote_sentiment in bearish_sentiments and base_sentiment not in bearish_sentiments:
        trade_decision = f"Buy {base_currency}/{quote_currency}"
    elif base_sentiment in bearish_sentiments and quote_sentiment not in bearish_sentiments:
        trade_decision = f"Sell {base_currency}/{quote_currency}"

def analyze_sentiment(json_response, target_ticker):
    """
    Analyze the sentiment data for a specific ticker.
    
    :param json_response: The JSON response from the API.
    :param target_ticker: The ticker symbol to analyze (e.g., base_ticker).
    :return: A string describing the overall sentiment for the target ticker.
    """
    print(f"Starting sentiment analysis for ticker: {target_ticker}")
    
    if not json_response or "feed" not in json_response:
        print("No valid data in JSON response.")
        return "No data available for analysis"

    sentiment_label = "Neutral"  # Default sentiment if no stronger signals found
    highest_relevance = 0  # Track the highest relevance score

    # Loop through each news item in the feed
    for item in json_response.get("feed", []):
        print(f"Analyzing item: {item}")  # Debugging output for each item
        # Check each ticker sentiment in the item
        for ticker_data in item.get("ticker_sentiment", []):
            print(f"Checking ticker data: {ticker_data}")  # Output each ticker sentiment data
            if ticker_data["ticker"] == "FOREX:"+str(target_ticker):
                relevance_score = float(ticker_data.get("relevance_score", 0))
                sentiment_score = float(ticker_data.get("ticker_sentiment_score", 0))
                print(f"Found matching ticker: {ticker_data['ticker']} with relevance {relevance_score} and sentiment score {sentiment_score}")
                
                # Determine the sentiment label based on the score
                if relevance_score > highest_relevance:
                    highest_relevance = relevance_score  # Update the highest relevance found
                    # Assign sentiment label based on sentiment score
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
    # Prepare the query parameters
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': ticker,
        'apikey': api_key,
        'sort': sort,
        'limit': limit
    }
    
    # Make the API request
    response = requests.get(api_endpoint, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the JSON response
        return response.json()
    else:
        # Return an error message
        return f"Error fetching data: {response.status_code}"
    
def load_web_driver():
    url = f'{BASE_URL}/en/cabinet/demo-quick-high-low/'
    driver.get(url)


def change_currency():
    current_symbol = driver.find_element(by=By.CLASS_NAME, value='current-symbol')
    print("Attempted to Change Currency"+str(current_symbol.text))
    current_symbol.click()
    # time.sleep(random.random())  # 0-1 sec
    currencies = driver.find_elements(By.XPATH, "//li[contains(., '"+str(PROFIT_GOAL)+"%')]")
    if currencies:
        # click random currency
        while True:
            currency = random.choice(currencies)
            if CURRENCY not in currency.text:
                break  # avoid repeats
        currency.click()
    else:
        pass


def do_action(signal):
    """ Execute trade based on signal and sentiment analysis """
    print(f"Starting do_action with signal: {signal}")
    
    # Check the current state of STACK and retrieve the last value if available
    last_value = list(STACK.values())[-1] if STACK else None
    if last_value is None:
        print("No data available in STACK to proceed with action.")
        return
    if len(ACTIONS) >= MAX_ACTIONS:
        print("Maximum number of actions reached, cannot execute more trades.")
        input("Press Enter to continue...")
        return

    # Set up API parameters and fetch sentiment data
    api_endpoint = "https://www.alphavantage.co/query"
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    base_ticker = CURRENCY.split('/')[0].strip()  # This will get 'AUD'
    print(f"Fetching sentiment data for: {base_ticker}")
    
    json_response = fetch_sentiment_data(api_endpoint, "FOREX:"+base_ticker, api_key)
    if json_response is None:
        print("Failed to fetch sentiment data.")
        return
    
    # Analyze sentiment and determine the appropriateness of the trade signal
    base_sentiment = analyze_sentiment(json_response, base_ticker)
    print(f"Received sentiment '{base_sentiment}' for {base_ticker}")

    # Check if the sentiment supports the trade signal
    valid_signals = {
        'call': ["Bullish", "Somewhat_Bullish"],
        'put': ["Bearish", "Somewhat-Bearish"]
    }
    if base_sentiment in valid_signals.get(signal, []):
        try:
            # Execute the trade
            print(f"Attempting to execute {signal} on {CURRENCY} at {last_value}")
            driver.find_element(by=By.CLASS_NAME, value=f'btn-{signal}').click()
            ACTIONS[datetime.now()] = last_value
            #global IS_AMOUNT_SET
            #IS_AMOUNT_SET = True
            print(f"Executed {signal} on {CURRENCY} at {last_value} due to {base_sentiment} sentiment.")
            time.sleep(random.random() * 120)  # Simulate delay after action
        except Exception as e:
            print(f"Error executing trade: {e}")
    elif base_sentiment == "Neutral":
        print(f"Sentiment '{base_sentiment}' is neutral, skipping trade execution.")
        input("Press Enter to continue...")
        # go to the next currency
        #try:
        #    change_currency()
        #except Exception as e:
        #    print(f"Error when trying to change currency: {e}")
    else:
        print(f"Sentiment '{base_sentiment}' does not support executing {signal} on {CURRENCY}.")


def hand_delay():
    time.sleep(random.choice([0.2, 0.3, 0.4, 0.5, 0.6]))
    pass


def get_amounts(amount):
    if amount > 1999:
        amount = 1999
    amounts = []
    while True:
        amount = int(amount / MARTINGALE_COEFFICIENT)
        amounts.insert(0, amount)
        if amounts[0] <= 1:
            amounts[0] = 1
            print('Amounts:', amounts, 'init deposit:', INIT_DEPOSIT)
            return amounts


def check_indicators(stack):
    print("Entering check_indicators function")  # Initial entry point
    try:
        deposit = driver.find_element(by=By.CSS_SELECTOR, value='body > div.wrapper > div.wrapper__top > header > div.right-block > div.right-block__item.js-drop-down-modal-open > div > div.balance-info-block__data > div.balance-info-block__balance > div')
        print(f"Current deposit fetched: {deposit.text}")
    except Exception as e:
        print(f"Failed to fetch current deposit: {e}")

    global IS_AMOUNT_SET, AMOUNTS, INIT_DEPOSIT

    if not INIT_DEPOSIT:
        INIT_DEPOSIT = float(deposit.text)
        print(f"Initial deposit set: {INIT_DEPOSIT}")

    if not AMOUNTS:  # Only for initial setup
        AMOUNTS = get_amounts(float(deposit.text))
        print(f"Initial amounts calculated based on deposit: {AMOUNTS}")

    if not IS_AMOUNT_SET:
        if ACTIONS and list(ACTIONS.keys())[-1] + timedelta(seconds=6) > datetime.now():  # Check if recent actions exist
            print("Recent action still within the timeout window, skipping adjustment")
            return

        try:
            closed_tab = driver.find_element(by=By.CSS_SELECTOR, value='#bar-chart > div > div > div.right-widget-container > div > div.widget-slot__header > div.divider > ul > li:nth-child(2) > a')
            closed_tab_parent = closed_tab.find_element(by=By.XPATH, value='..')
            if closed_tab_parent.get_attribute('class') == '':
                print("Closed trades tab is not active, clicking to activate")
                closed_tab_parent.click()
        except Exception as e:
            print(f"Error trying to activate closed trades tab: {e}")

        closed_trades_currencies = driver.find_elements(by=By.CLASS_NAME, value='deals-list__item')
        if closed_trades_currencies:
            last_split = closed_trades_currencies[0].text.split('\n')
            print(f"Last closed trade details: {last_split}")
            try:
                amount = driver.find_element(by=By.CSS_SELECTOR, value='#put-call-buttons-chart-1 > div > div.blocks-wrap > div.block.block--bet-amount > div.block__control.control > div.control__value.value.value--several-items > div > input[type=text]')
                amount_value = int(amount.get_attribute('value')[1:])
                base = '#modal-root > div > div > div > div > div.virtual-keyboard.js-virtual-keyboard > div > div:nth-child(%s) > div'
                print(f"Handling trade amount input: current amount is {amount_value}")

                if '0.00' not in last_split[4]:  # win
                    if amount_value > 1:
                        print(f"Win detected, resetting bet amount")
                        amount.click()
                        hand_delay()
                        driver.find_element(by=By.CSS_SELECTOR, value=base % NUMBERS['1']).click()
                        AMOUNTS = get_amounts(float(deposit.text))  # Refresh amounts after a win
                elif '0.00' not in last_split[3]:  # draw
                    print("Draw detected, no change to bet amount")
                    pass
                else:  # lose
                    print("Loss detected, adjusting bet amount")
                    amount.click()
                    time.sleep(random.choice([0.6, 0.7, 0.8, 0.9, 1.0, 1.1]))
                    if amount_value in AMOUNTS and AMOUNTS.index(amount_value) + 1 < len(AMOUNTS):
                        next_amount = AMOUNTS[AMOUNTS.index(amount_value) + 1]
                        print(f"Increasing bet amount to {next_amount}")
                        for number in str(next_amount):
                            driver.find_element(by=By.CSS_SELECTOR, value=base % NUMBERS[number]).click()
                            hand_delay()
                    else:  # reset to 1
                        print("Resetting bet amount to 1")
                        driver.find_element(by=By.CSS_SELECTOR, value=base % NUMBERS['1']).click()
                        hand_delay()
                closed_tab_parent.click()
            except Exception as e:
                print(f"Error during trade amount adjustment: {e}")
        IS_AMOUNT_SET = True

    # Check if it's time to evaluate indicators
    if datetime.now().second % 10 != 0:
        print("Skipping indicator check due to timing")
        return

    # Decision making based on the latest indicator values
    if list(stack.values())[-1] < list(stack.values())[-1 - PERIOD]:
        print("\033[91mIndicator suggests PUT action\033[0m")
        do_action('put')
        #input("Press Enter to continue...")
    else: 
        print("\033[92mIndicator suggests CALL action\033[0m")
        do_action('call')
        #input("Press Enter to continue...")

def websocket_log(stack):
    try:
        estimated_profit_text = driver.find_element(by=By.CLASS_NAME, value='estimated-profit-block__text').text
        # Remove the '+' sign and '%' to convert the string to an integer
        estimated_profit = int(estimated_profit_text.replace('+', '').replace('%', ''))
        
        # Assume PROFIT_GOAL is defined somewhere as an integer
        if estimated_profit < PROFIT_GOAL:
            print(f"The profit is less than {PROFIT_GOAL}% -> switching to another currency. Current profit: {estimated_profit}%")
            time.sleep(random.random() * 10)  # 1-10 sec
            change_currency()
    except:
        print("Error fetching estimated profit")
        pass

    global CURRENCY, CURRENCY_CHANGE, CURRENCY_CHANGE_DATE, LAST_REFRESH, HISTORY_TAKEN, MODEL, INIT_DEPOSIT
    try:
        current_symbol = driver.find_element(by=By.CLASS_NAME, value='current-symbol').text
        if current_symbol != CURRENCY:
            CURRENCY = current_symbol
            CURRENCY_CHANGE = True
            CURRENCY_CHANGE_DATE = datetime.now()
    except:
        pass

    if CURRENCY_CHANGE and CURRENCY_CHANGE_DATE < datetime.now() - timedelta(seconds=5):
        stack = {}  # drop stack when currency changed
        HISTORY_TAKEN = False  # take history again
        driver.refresh()  # refresh page to cut off unwanted signals
        CURRENCY_CHANGE = False
        MODEL = None
        INIT_DEPOSIT = None

    for wsData in driver.get_log('performance'):
        message = json.loads(wsData['message'])['message']
        response = message.get('params', {}).get('response', {})
        if response.get('opcode', 0) == 2 and not CURRENCY_CHANGE:
            payload_str = base64.b64decode(response['payloadData']).decode('utf-8')
            data = json.loads(payload_str)
            if not HISTORY_TAKEN:
                if 'history' in data:
                    stack = {int(d[0]): d[1] for d in data['history']}
                    print(f"History taken for asset: {data['asset']}, period: {data['period']}, len_history: {len(data['history'])}, len_stack: {len(stack)}")
            try:
                current_symbol = driver.find_element(by=By.CLASS_NAME, value='current-symbol').text
                print(f"Current symbol: {current_symbol}")
                symbol, timestamp, value = data[0]
                print(f"Symbol: {symbol}, Timestamp: {timestamp}, Value: {value}")
                print("Line number 364")
            except:
                continue
            try:
                print("Line number 368")
                if current_symbol.replace('/', '').replace(' ', '') != symbol.replace('_', '').upper() and companies.get(current_symbol) != symbol:
                    continue
            except:
                pass

            print("Curent Stack Length->"+str(len(stack))+" Current Max Stack Length->"+str(LENGTH_STACK_MAX))
            if len(stack) == LENGTH_STACK_MAX:
                print("Line number 375")
                first_element = next(iter(stack))
                del stack[first_element]
            if len(stack) < LENGTH_STACK_MAX:
                if int(timestamp) in stack:
                    return stack
                else:
                    stack[int(timestamp)] = value
            elif len(stack) > LENGTH_STACK_MAX:
                print(f"Len > {LENGTH_STACK_MAX}!!")
                stack = {}  # refresh then
            if len(stack) >= LENGTH_STACK_MIN:
                print("Line number 386")
                check_indicators(stack)
    return stack


print("Starting PO bot")
load_web_driver()
time.sleep(60)
while True:
    STACK = websocket_log(STACK)
