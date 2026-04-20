import pandas as pd
import numpy as np

def calculate_metrics(equity_curve: pd.Series) -> dict:
    """
    Calculates standard quantitative performance metrics.
    """
    # 1. Total Return
    total_return = equity_curve.iloc[-1] - 1.0
    
    # 2. Sharpe Ratio (Annualized)
    # We calculate the daily percentage changes in our account
    returns = equity_curve.pct_change().dropna()
    # Multiply by the square root of 252 (the number of trading days in a year)
    sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
    
    # 3. Max Drawdown
    # Track the highest point our account has ever reached up to today
    roll_max = equity_curve.cummax()
    # Calculate how far down we currently are from that peak
    drawdown = (equity_curve - roll_max) / roll_max
    max_drawdown = drawdown.min()
    
    return {
        'Total Return': f"{total_return*100:.2f}%",
        'Sharpe Ratio': f"{sharpe:.2f}",
        'Max Drawdown': f"{max_drawdown*100:.2f}%"
    }

def run_backtest(df:pd.DataFrame,signals:pd.DataFrame,trailing_stop:float=0.05,ma_window:int =20):
    print("Initializing backtest engine...")
    position = 0
    entry_price=0.0
    stop_price=0.0
    trade_log=[]
    equity=[1.0]

    ma=df['Close'].rolling(ma_window).mean()
    for i in range(1,len(df)):
        date = df.index[i]
        price=df['Close'].iloc[i]
        if position == 0 and signals['buy_signal'].iloc[i]:
            position = 1
            entry_price = price
            # Set initial stop loss 5% below buy price
            stop_price = price * (1 - trailing_stop) 
            trade_log.append({'Date': date, 'Type': 'Buy', 'Price': price})
            
        # --- EXIT LOGIC ---
        # If we currently own the stock
        elif position == 1:
            # Trailing Stop: Move the stop price UP if the stock goes up, but never move it down
            stop_price = max(stop_price, price * (1 - trailing_stop))
            
            # Did the price crash through our stop loss OR drop below the 20-day MA?
            if price < stop_price or price < ma.iloc[i]:
                position = 0 # Sell!
                trade_log.append({'Date': date, 'Type': 'Sell', 'Price': price})
                
        # --- ACCOUNT BALANCE TRACKING ---
        # If we are holding the stock, our account grows/shrinks with the daily price change
        if position == 1:
            daily_return = price / df['Close'].iloc[i-1]
        else:
            daily_return = 1.0 # Cash doesn't change value
            
        # Update our running equity curve
        equity.append(equity[-1] * daily_return)
        
    # Format the outputs
    equity_curve = pd.Series(equity[1:], index=df.index[1:])
    trades_df = pd.DataFrame(trade_log)
    
    return equity_curve, trades_df

  # Format the outputs
    equity_curve = pd.Series(equity[1:], index=df.index[1:])
    trades_df = pd.DataFrame(trade_log)
    
    return equity_curve, trades_df

if __name__ == "__main__":
    from data import fetch_data
    from strategy import generate_signals
    
    # 1. Get Data
    df = fetch_data('RELIANCE.NS', '2025-01-01', '2026-01-01')
    
    # 2. Get Signals
    signals = generate_signals(df)
    
    # 3. Run Simulation
    equity_curve, trades = run_backtest(df, signals)
    
    print("\n--- Trade History ---")
    print(trades)
    
    print(f"\nFinal Account Multiplier: {equity_curve.iloc[-1]:.4f}")
    # Example: 1.05 means a 5% profit. 0.95 means a 5% loss.
    # Calculate and print metrics
    metrics = calculate_metrics(equity_curve)
    print("\n--- Strategy Performance ---")
    for key, value in metrics.items():
        print(f"{key}: {value}")