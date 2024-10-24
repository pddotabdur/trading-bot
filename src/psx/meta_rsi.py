import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Load_data
# df = pd.read_csv("mebl_stock.csv")
#RSI
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

# df['RSI'] = calculate_rsi(df)
# print(df)


def calculate_ma(data, n=14, type='SMA'):
    if type == 'SMA':
        return data.rolling(window=n).mean()
    elif type == 'EMA':
        return data.ewm(span=n, adjust=False).mean()
    elif type == 'WMA':
        return data.ewm(span=n, adjust=False).mean()
    elif type == 'VWMA':
        return data.ewm(span=n, adjust=False).mean()

# df['RSI_MA'] = calculate_ma(df['RSI'], n=14, type='SMA')
# print(df.tail())

#Calculate Bollinger Bands
def calculate_bollinger_bands(data, n=14, mult=2):
    ma = data.rolling(window=n).mean()
    std = data.rolling(window=n).std()
    upper = ma + mult * std
    lower = ma - mult * std
    return upper, lower

# df['BB_Upper'], df['BB_Lower'] = calculate_bollinger_bands(df['RSI'], n=14, mult=2)

##################### Plot data for RSI ###############
# plt.figure(figsize=(12, 6))
# plt.plot(df['RSI'], label='RSI')
# plt.plot(df['RSI_MA'], label='RSI MA')
# plt.plot(df['BB_Upper'], label='BB Upper')
# plt.plot(df['BB_Lower'], label='BB Lower')
# plt.axhline(y=70, color='r', linestyle='--')
# plt.axhline(y=30, color='g', linestyle='--')
# plt.legend(loc='upper left')
# plt.show()

#Divergence detection
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

# df['Bull_Cond'], df['Bear_Cond'] = detect_divergence(df)

####################### Plot divergence #################
# plt.figure(figsize=(12, 6))
# plt.plot(df['RSI'], label='RSI')
# plt.scatter(df.index[df['Bull_Cond']], df['RSI'][df['Bull_Cond']], label='Bullish Divergence', color='g')
# plt.scatter(df.index[df['Bear_Cond']], df['RSI'][df['Bear_Cond']], label='Bearish Divergence', color='r')
# plt.legend(loc='upper left')
# plt.show()