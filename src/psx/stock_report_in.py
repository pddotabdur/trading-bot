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
import time

import tkinter as tk
from tkinter import messagebox

def main():
    # Create the root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.geometry("500x300")

    # Show a message box
    messagebox.showinfo("Success", "Your application is running!")

if __name__ == "__main__":
    main()



data_reader = DataReader()
e=0

def download_symbols():

    options = Options()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')

    driver = webdriver.Chrome(options=options)  
    driver.get('https://dps.psx.com.pk/')

    index_dropdown = Select(driver.find_element(By.NAME, 'index'))
    index_dropdown.select_by_value('KMIALLSHR')

    entries_dropdown = Select(driver.find_element(By.NAME, 'DataTables_Table_0_length'))
    entries_dropdown.select_by_value('-1')

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    table = soup.find('table', id='DataTables_Table_0')

    tbody = table.find('tbody')
    table = tbody.find_parent('table')


    table_html = str(table)

    df = pd.read_html(table_html)[0]

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
    # df.to_csv(f'data/{symbol}.csv')
    df['RSI'] = calculate_rsi(df)

    last_rsi = df['RSI'].iloc[-1]
    last_date = df.index[-1]

    results = {}

    if last_rsi > 70:
        results['RSI'] = f"On {last_date}, the RSI value for {symbol} was {last_rsi}, which is higher than 70."
    elif last_rsi < 30:
        results['RSI'] = f"On {last_date}, the RSI value for {symbol} was {last_rsi}, which is lower than 30."

    df['Bull_Cond'], df['Bear_Cond'] = detect_divergence(df)
    last_bull_cond = df['Bull_Cond'].iloc[-1]
    last_bear_cond = df['Bear_Cond'].iloc[-1]

    if last_bull_cond:
        results['Bull Condition'] = f"The last row of bull_cond for {symbol} is True."
    if last_bear_cond:
        results['Bear Condition'] = f"The last row of bear_cond {symbol} is True."

    return results

def save_results_to_pdf(results_list, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50 
    line_height = 20

    for results in results_list:
        for key, value in results.items():
            if y < 50: 
                c.showPage()
                y = height - 50 
            c.drawString(50, y, f"{key}: {value}")
            y -= line_height

    c.save()

symbs = download_symbols()
results_list = []

for index, row in symbs.iterrows():
    symbol = str(row['SYMBOL'])
    try:
        results = cal_rsi(symbol=symbol)
        if results:
            results_list.append(results)
    except:
        print("Error for", symbol)
    e+=1
    if e==5:
        break


current_time = time.localtime()
current_month = current_time.tm_mon
current_day = current_time.tm_mday

filename = f'stocks_report_{current_day}_{current_month}.pdf'
save_results_to_pdf(results_list, filename)