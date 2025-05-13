
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

# Lista med intressanta aktier
tickers = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "EVO.ST", "VOLV-B.ST", "SINCH.ST", "TRUE-B.ST", "CAMX.ST"]

# Teknisk analys-funktion
def analyze_stock(ticker):
    data = yf.download(ticker, period="5d", interval="1m")
    if data.empty:
        return None

    df = data.copy()
    df['EMA9'] = ta.trend.ema_indicator(df['Close'], window=9)
    df['EMA50'] = ta.trend.ema_indicator(df['Close'], window=50)
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    macd = ta.trend.macd(df['Close'])
    df['MACD'] = macd.macd_diff()
    df['VWAP'] = (df['Volume'] * (df['High'] + df['Low']) / 2).cumsum() / df['Volume'].cumsum()

    last = df.iloc[-1]

    if (
        last['Close'] > last['EMA9'] and
        last['Close'] > last['EMA50'] and
        last['RSI'] > 30 and
        last['MACD'] > 0 and
        last['Close'] > last['VWAP']
    ):
        return f"KÖPSIGNAL för {ticker} | Pris: {last['Close']:.2f}"
    elif last['RSI'] > 70 and last['MACD'] < 0:
        return f"SÄLJSIGNAL för {ticker} | RSI: {last['RSI']:.2f}"
    return None

# Streamlit gränssnitt
st.title("Daytrading Signalapp")
st.subheader("Analyserar marknaden varje minut...")

for t in tickers:
    with st.spinner(f"Analyserar {t}..."):
        signal = analyze_stock(t)
        if signal:
            st.success(signal)
        else:
            st.info(f"Inga signaler för {t}")
