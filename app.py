import streamlit as st
from data import fetch_data
from strategy import generate_signals
from backtest import run_backtest, calculate_metrics
from visualization import plot_all
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Quant Dashboard")

# --- UI CONTROLS (Sidebar) ---
st.sidebar.header("Strategy Parameters")
symbol = st.sidebar.text_input("Ticker Symbol", "RELIANCE.NS")
lookback = st.sidebar.slider("Breakout Lookback (Days)", min_value=5, max_value=100, value=20)
vol_window = st.sidebar.slider("Volume Window (Days)", min_value=5, max_value=100, value=20)
trailing_stop = st.sidebar.number_input("Trailing Stop %", min_value=0.01, max_value=0.20, value=0.05)

# --- EXECUTION ---
if st.sidebar.button("Run Backtest"):
    with st.spinner(f"Fetching data for {symbol}..."):
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
    
    # In visualization.py, modify plot_all to `return fig` at the end instead of `plt.show()`
    # Then render it here in the web app:
    # fig = plot_all(df, signals, trades, equity_curve)
    # st.pyplot(fig)