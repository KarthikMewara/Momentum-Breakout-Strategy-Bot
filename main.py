from data import fetch_data
from strategy import generate_signals
from backtest import run_backtest, calculate_metrics
from visualization import plot_all

if __name__ == "__main__":
    # You can easily change the ticker and dates here to test other assets
    SYMBOL = 'RELIANCE.NS'
    START_DATE = '2025-01-01'
    END_DATE = '2026-01-01'

    print(f"--- Starting Quantitative Pipeline for {SYMBOL} ---")
    
    # 1. Fetch Data
    df = fetch_data(SYMBOL, START_DATE, END_DATE)
    
    # 2. Generate Signals
    signals = generate_signals(df)
    
    # 3. Run Backtest
    equity_curve, trades = run_backtest(df, signals)
    
    # 4. Calculate Metrics
    metrics = calculate_metrics(equity_curve)
    
    print("\n--- Strategy Performance ---")
    for key, value in metrics.items():
        print(f"{key}: {value}")
        
    print("\n--- Trade History ---")
    print(trades)
    
    # 5. Render Visualization
    plot_all(df, signals, trades, equity_curve)