from web import DataReader
import pandas as pd
import datetime
from datetime import timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, JavascriptException
import time
from io import StringIO

data_reader = DataReader()

def download_symbols():

    options = Options()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')

    driver = webdriver.Chrome(options=options)  
    driver.get('https://dps.psx.com.pk/')

    try:
        close_button = driver.find_element(By.CLASS_NAME, "tingle-modal__close")
        close_button.click()
        print("Popup closed")
    except NoSuchElementException:
        print("No popup found, continuing...")
    except JavascriptException as e:
        print(f"Error clicking the close button: {e}")

    index_dropdown = Select(driver.find_element(By.NAME, 'index'))
    index_dropdown.select_by_value('KMIALLSHR')

    entries_dropdown = Select(driver.find_element(By.NAME, 'DataTables_Table_0_length'))
    entries_dropdown.select_by_value('-1')

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    table = soup.find('table', id='DataTables_Table_0')

    tbody = table.find('tbody')
    table = tbody.find_parent('table')

    with open("extracted_table.html", "w") as file:
        file.write(str(table.prettify()))

    table_html = str(table)

    df = pd.read_html(StringIO(table_html))[0]

    # Save the DataFrame as a CSV file
    # df.to_csv("extracted_table.csv", index=False)


    # Close the WebDriver
    driver.quit()

    return df

def calculate_rsi(data, n=14):
    delta = data['Close'].diff().dropna()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    roll_up = up.ewm(com=n-1, adjust=False).mean()
    roll_down = down.ewm(com=n-1, adjust=False).mean().abs()
    RS = roll_up / roll_down
    RSI = 100.0 - (100.0 / (1.0 + RS))
    return RSI

def detect_divergence(data, lookback_right=5, lookback_left=5):
    rsi = data['RSI']
    low = data['Low']
    high = data['High']
    
    #Regular Bullish
    rsi_hl = rsi.shift(lookback_right) > rsi.shift(lookback_right + 1)
    price_ll = low.shift(lookback_right) < low.shift(lookback_right + 1)
    bull_cond = rsi_hl & price_ll
    
    #Regular Bearish
    rsi_lh = rsi.shift(lookback_right) < rsi.shift(lookback_right + 1)
    price_hh = high.shift(lookback_right) > high.shift(lookback_right + 1)
    bear_cond = rsi_lh & price_hh    
    return bull_cond, bear_cond

def cal_rsi(symbol):
    end = datetime.date.today()
    start = end - timedelta(days=1000)
    
    df = data_reader.stocks(symbol, start=start, end=end)
    
    if df.empty:
        print(f"No historical data for {symbol}")
        return None, None
    
    df['RSI'] = calculate_rsi(df)
    df['Bull_Cond'], df['Bear_Cond'] = detect_divergence(df)
    
    last_row = df.iloc[-1]
    last_row_index = df.index[-1]

    if last_row['RSI'] > 60 or last_row['RSI'] < 30:
        return last_row, last_row_index
    else:
        return None, None


symbs = download_symbols()
df_results = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'Bull_Cond', 'Bear_Cond'])

for index, row in symbs.iterrows():
    symbol = str(row['SYMBOL'])
    results_row, results_index = cal_rsi(symbol=symbol)

    try:
        if results_row is not None:
            new_row = pd.DataFrame([results_row], index=[results_index], columns=df_results.columns)
            if not new_row.empty and new_row.notna().any().any():
                new_row['SYMBOL'] = symbol
                df_results = pd.concat([df_results, new_row], ignore_index=False)

    except Exception as e:
        print(f"Error for {symbol}: {e}")


current_time = time.localtime()
current_month = current_time.tm_mon
current_day = current_time.tm_mday

filename = f'stocks_report_{current_day}_{current_month}.csv'
df_results.to_csv(filename)