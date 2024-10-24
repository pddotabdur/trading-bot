import numpy as np
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from datetime import date, timedelta
from web import DataReader
import pandas as pd
from meta_rsi import calculate_rsi, detect_divergence
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
data_reader = DataReader()

def download_data(symbol):
    end = datetime.date.today()
    start = end - timedelta(days=1000)
    df = data_reader.stocks(symbol, start=start, end=end)
    return df

# data = download_data('MTL')
data = pd.read_csv('mtl_stock.csv')
print(data)
#mommentum based indicators
data['SMA 50'] = ta.sma(data['Close'], 50)
data['SMA 100'] = ta.sma(data['Close'], 100)
data['SMA 200'] = ta.sma(data['Close'], 200)
data['rsi'] = ta.rsi(data['Close'], 14)
data[['MACD', 'MACD_Histogram', 'MACD_Signal']] = ta.macd(data['Close'])

data[['STOCH_K', 'STOCK_D']] = ta.stoch(data['High'], data['Low'], data['Close'])

#volatility based indicators
data[['BB_Lower','BB_Middle', 'BB_Upper','BB_Bandwith', 'BB_Percent']] = ta.bbands(data['Close'], 20)
data['ATR'] = ta.atr(data['High'], data['Low'], data['Close'])

#trends indicator
data['EMA 50'] = ta.ema(data['Close'], 50)
data['EMA 100'] = ta.ema(data['Close'], 100)
data['EMA 200'] = ta.ema(data['Close'], 200)
ichimoku = ta.ichimoku(data['High'], data['Low'], data['Close'], 
                       tenkan=9, kijun=26, senkou=52, chikou=26)

data[['Tenkan_sen', 'Kijun_sen', 'Senkou_span_A', 'Senkou_span_B', 'Chikou_span']] = ichimoku[0]

#volume indicator
data['OBV'] = ta.obv(data['Close'], data['Volume'])
data['Accumulation_Distribution'] = ta.ad(data['High'], data['Low'], data['Close'], data['Volume'])

#Statistics
data['Returns'] = data['Close'].pct_change()


data['Median'] = ta.median(data['Returns'])
data['Standard Deviation'] = ta.stdev(data['Returns'])
data['Variance'] = ta.variance(data['Returns'])
data['Skewness'] = ta.skew(data['Returns'])
data['Kurtosis'] = ta.kurtosis(data['Returns'])

# data['Sharpe Ratio'] = ta.sharpe_ratio()

data.to_csv('mtl_indicators.csv')


