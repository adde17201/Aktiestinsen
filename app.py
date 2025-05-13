
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

        df = pd.DataFrame(data)
        df = df.dropna()

        # Skapa Series med rätt index
        close = pd.Series(df['Close'].values.flatten(), index=df.index)
        high = pd.Series(df['High'].values.flatten(), index=df.index)
        low = pd.Series(df['Low'].values.flatten(), index=df.index)
        volume = pd.Series(df['Volume'].values.flatten(), index=df.index)

        df['EMA9'] = ta.trend.EMAIndicator(close=close, window=9).ema_indicator()
        df['EMA50'] = ta.trend.EMAIndicator(close=close, window=50).ema_indicator()
        df['RSI'] = ta.momentum.RSIIndicator(close=close).rsi()
        df['MACD'] = ta.trend.macd_diff(close)
        df['VWAP'] = (volume * (high + low) / 2).cumsum() / volume.cumsum()

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

# Loopa igenom alla aktier
for t in tickers:
    with st.spinner(f"Analyserar {t}..."):
        resultat = analyze_stock(t)
        if "KÖPSIGNAL" in resultat:
            st.success(resultat)
        elif "SÄLJSIGNAL" in resultat:
            st.warning(resultat)
        else:
            st.info(resultat)
