import pandas as pd

def generate_signals(df: pd.DataFrame, lookback: int = 20, vol_window: int = 20) -> pd.DataFrame:
    """
    Scans the data and generates buy signals based on price breakouts and volume.
    """
    print(f"Generating signals using a {lookback}-day breakout and {vol_window}-day volume average...")
    
    # Create a new DataFrame just to hold our signals
    signals = pd.DataFrame(index=df.index)
    
    # 1. The Breakout Level: Find the highest 'High' over the last 20 days
    signals['rolling_high'] = df['High'].rolling(window=lookback).max()
    
    # 2. The Volume Baseline: Find the average volume over the last 20 days
    signals['avg_volume'] = df['Volume'].rolling(window=vol_window).mean()
    
    # 3. The Trigger: 
    #   - Today's Close is strictly greater than YESTERDAY'S rolling high (.shift(1))
    #   - Today's Volume is strictly greater than today's average volume
    signals['buy_signal'] = (df['Close'] > signals['rolling_high'].shift(1)) & \
                            (df['Volume'] > signals['avg_volume'])
                            
    # We will let the backtester handle the sell logic later
    signals['sell_signal'] = False 
    
    return signals[['buy_signal', 'sell_signal']]

# --- TEST BLOCK ---
if __name__ == "__main__":
    # We import the function you just wrote in data.py!
    from data import fetch_data
    
    # Fetch the data
    historical_data = fetch_data('RELIANCE.NS', '2025-01-01', '2026-01-01')
    
    # Run the strategy on the data
    signal_data = generate_signals(historical_data)
    
    # Let's count how many times the bot decided to buy
    total_buys = signal_data['buy_signal'].sum()
    print(f"\nTotal Buy Signals Generated: {total_buys}")
    
    # Show the exact days a buy signal was triggered
    print("\nDates where the strategy bought:")
    print(signal_data[signal_data['buy_signal'] == True].head())