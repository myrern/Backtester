import matplotlib.pyplot as plt 
import mplfinance as mpf
import pandas as pd 

# Extracting Data for plotting 
df = pd.read_csv('./data/EUR_USD_H1_CURRENCY.csv') 

# Only keep the columns we need and rename them
df = df[['time', 'mid_o', 'mid_h', 'mid_l', 'mid_c', 'volume']]
df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

# Converting 'Date' into datetime format and set as index
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Plot using mplfinance module
mpf.plot(df, type='candle', style='yahoo', volume=True, title='EUR/USD H1', figratio=(12,8))

plt.show()
