import streamlit as st
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

# Create a list of formatted strings for the UI dropdown
display_options = [f"{ticker} ({name})" for ticker, name in AVAILABLE_ASSETS.items()]

# Find the exact index of Apple so we can set it as the default
apple_index = display_options.index("AAPL (Apple Inc.)")

# --- UI CONTROLS (Sidebar) ---
st.sidebar.header("Strategy Parameters")

# Pass the apple_index to the selectbox
selected_option = st.sidebar.selectbox("Select Asset", display_options, index=apple_index)
symbol = selected_option.split(" ")[0]

lookback = st.sidebar.slider("Breakout Lookback (Days)", min_value=5, max_value=100, value=20)
vol_window = st.sidebar.slider("Volume Window (Days)", min_value=5, max_value=100, value=20)
trailing_stop = st.sidebar.number_input("Trailing Stop %", min_value=0.01, max_value=0.20, value=0.05)

# --- EXECUTION ---
# Without the button, this block executes immediately whenever any input changes.
with st.spinner(f"Crunching data for {symbol}..."):
    df = fetch_data(symbol, '2025-01-01', '2026-01-01')
    
    signals = generate_signals(df, lookback=lookback, vol_window=vol_window)
    equity_curve, trades = run_backtest(df, signals, trailing_stop=trailing_stop)
    metrics = calculate_metrics(equity_curve)

# --- UI RENDERING (Main Page) ---
st.title(f"Backtest Results: {symbol}")

# Display the Scoreboard
col1, col2, col3 = st.columns(3)
col1.metric("Total Return", metrics['Total Return'])
col2.metric("Sharpe Ratio", metrics['Sharpe Ratio'])
col3.metric("Max Drawdown", metrics['Max Drawdown'])

# Catch the figure returned from our interactive Plotly visualization script
fig = plot_all(df, signals, trades, equity_curve)

# Render the interactive charts
st.plotly_chart(fig, use_container_width=True)