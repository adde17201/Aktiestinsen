
import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.title("Daytrading Signalapp")
st.subheader("Analyserar marknaden varje minut...")

tickers = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "EVO.ST", "VOLV-B.ST", "SINCH.ST", "TRUE-B.ST", "CAMX.ST"]

def analyze_stock(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="1m", progress=False)
        if data.empty or len(data) < 60:
            return f"Ingen data för {ticker}"

        df = data.copy()

        # ANVÄND ENDAST 1D SERIES (df['Close']) - aldrig df[['Close']]
        df['EMA9'] = ta.trend.EMAIndicator(close=df['Close'], window=9).ema_indicator()
        df['EMA50'] = ta.trend.EMAIndicator(close=df['Close'], window=50).ema_indicator()
        df['RSI'] = ta.momentum.RSIIndicator(close=df['Close']).rsi()
        df['MACD'] = ta.trend.macd_diff(df['Close'])
        df['VWAP'] = (df['Volume'] * (df['High'] + df['Low']) / 2).cumsum() / df['Volume'].cumsum()

        df.dropna(inplace=True)

        if df.empty:
            return f"Inga giltiga datapunkter efter indikatorberäkning för {ticker}"

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
        else:
            return f"Inga signaler för {ticker}"

    except Exception as e:
        return f"Fel vid analys av {ticker}: {e}"

# Kör analys för varje aktie
for t in tickers:
    with st.spinner(f"Analyserar {t}..."):
        resultat = analyze_stock(t)
        if "KÖPSIGNAL" in resultat:
            st.success(resultat)
        elif "SÄLJSIGNAL" in resultat:
            st.warning(resultat)
        else:
            st.info(resultat)
