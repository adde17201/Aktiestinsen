
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

        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']

        # Skapa indikatorer
        ema9 = ta.trend.EMAIndicator(close=close, window=9).ema_indicator()
        ema50 = ta.trend.EMAIndicator(close=close, window=50).ema_indicator()
        rsi = ta.momentum.RSIIndicator(close=close).rsi()
        macd = ta.trend.macd_diff(close)

        vwap = (volume * (high + low) / 2).cumsum() / volume.cumsum()

        df = df.assign(EMA9=ema9, EMA50=ema50, RSI=rsi, MACD=macd, VWAP=vwap)
        df.dropna(inplace=True)

        if df.empty:
            return f"Inga giltiga datapunkter efter indikatorberäkning för {ticker}"

        last = df.iloc[-1]

        # Jämför bara faktiska värden, aldrig Series mot Series
        if (
            float(last['Close']) > float(last['EMA9']) and
            float(last['Close']) > float(last['EMA50']) and
            float(last['RSI']) > 30 and
            float(last['MACD']) > 0 and
            float(last['Close']) > float(last['VWAP'])
        ):
            return f"KÖPSIGNAL för {ticker} | Pris: {last['Close']:.2f}"
        elif float(last['RSI']) > 70 and float(last['MACD']) < 0:
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
