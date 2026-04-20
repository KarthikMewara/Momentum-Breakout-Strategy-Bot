import streamlit as st
import datetime # --- ADD THIS IMPORT ---
from data import fetch_data
from strategy import generate_signals
from backtest import run_backtest, calculate_metrics
from visualization import plot_all

st.set_page_config(layout="wide", page_title="Quant Dashboard")

# --- ASSET DICTIONARY ---
AVAILABLE_ASSETS = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys",
    "ICICIBANK.NS": "ICICI Bank",
    "SBIN.NS": "State Bank of India",
    "ITC.NS": "ITC Limited",
    "LT.NS": "Larsen & Toubro",
    "AAPL": "Apple Inc.",
    "NVDA": "NVIDIA Corp.",
    "TSLA": "Tesla Inc.",
    "BTC-USD": "Bitcoin"
}

display_options = [f"{ticker} ({name})" for ticker, name in AVAILABLE_ASSETS.items()]
apple_index = display_options.index("AAPL (Apple Inc.)")

# --- UI CONTROLS (Sidebar) ---
st.sidebar.header("Strategy Parameters")

selected_option = st.sidebar.selectbox("Select Asset", display_options, index=apple_index)
symbol = selected_option.split(" ")[0]

interval = st.sidebar.selectbox("Timeframe", ["1d", "1wk", "1mo", "1h", "15m", "5m"])

lookback = st.sidebar.slider("Breakout Lookback (Periods)", min_value=5, max_value=100, value=20)
vol_window = st.sidebar.slider("Volume Window (Periods)", min_value=5, max_value=100, value=20)
trailing_stop = st.sidebar.number_input("Trailing Stop %", min_value=0.01, max_value=0.20, value=0.05)

# --- DYNAMIC DATE LOGIC ---
# Calculate 'today' for the end date
end_date = datetime.date.today()

# If intraday (hours/minutes), yfinance only allows the last 60 days
if interval in ["1h", "15m", "5m"]:
    start_date = end_date - datetime.timedelta(days=59)
# Otherwise, pull a full year of data for daily/weekly/monthly
elif interval == "1mo":
    start_date = end_date - datetime.timedelta(days=365 * 5)
    
# Weekly charts: Let's pull 3 years of data
elif interval == "1wk":
    start_date = end_date - datetime.timedelta(days=365 * 3)
    
# Daily charts: 2 years gives a great historical view
else:
    start_date = end_date - datetime.timedelta(days=365 * 2)

# Convert dates to the string format yfinance expects (YYYY-MM-DD)
start_str = start_date.strftime('%Y-%m-%d')
end_str = end_date.strftime('%Y-%m-%d')

# --- EXECUTION ---
with st.spinner(f"Crunching {interval} data for {symbol}..."):
    # Pass the DYNAMIC dates into fetch_data instead of hardcoded ones
    df = fetch_data(symbol, start=start_str, end=end_str, interval=interval)
    
    signals = generate_signals(df, lookback=lookback, vol_window=vol_window)
    equity_curve, trades = run_backtest(df, signals, trailing_stop=trailing_stop)
    metrics = calculate_metrics(equity_curve)

# --- UI RENDERING (Main Page) ---
st.title(f"Backtest Results: {symbol} ({interval})")

col1, col2, col3 = st.columns(3)
col1.metric("Total Return", metrics['Total Return'])
col2.metric("Sharpe Ratio", metrics['Sharpe Ratio'])
col3.metric("Max Drawdown", metrics['Max Drawdown'])

fig = plot_all(df, signals, trades, equity_curve)
st.plotly_chart(fig, use_container_width=True)