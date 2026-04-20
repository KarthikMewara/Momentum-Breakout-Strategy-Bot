import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def plot_all(df: pd.DataFrame, signals: pd.DataFrame, trades: pd.DataFrame, equity_curve: pd.Series):
    """
    Shows price, equity curve, and volume in a single dark-themed window.
    """
    print("Generating visual dashboard...")
    
    # Set the dark theme
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(14, 10))
    # Create 3 rows for our charts: Price (largest), Equity, Volume
    gs = gridspec.GridSpec(3, 1, height_ratios=[2, 1, 1])

    # --- 1. PRICE CHART ---
    ax1 = plt.subplot(gs[0])
    # Plot the closing price in neon cyan
    ax1.plot(df.index, df['Close'], color='#00ffe7', linewidth=2, label='Close', alpha=0.9, zorder=1)
    
    # Overlay our Buy and Sell markers
    if trades is not None and not trades.empty:
        buys = trades[trades['Type'] == 'Buy']
        sells = trades[trades['Type'] == 'Sell']
        ax1.scatter(buys['Date'], buys['Price'], marker='^', color='#39ff14', s=100, label='Buy', edgecolor='black', zorder=2)
        ax1.scatter(sells['Date'], sells['Price'], marker='v', color='#ff073a', s=100, label='Sell', edgecolor='black', zorder=2)
        
    ax1.set_title('Price Chart with Breakouts', color='white', fontsize=16)
    ax1.legend()
    ax1.grid(False)
    
    # Set background colors to match the specific dark hex code
    fig.patch.set_facecolor('#181a20')
    ax1.set_facecolor('#181a20')

    # --- 2. EQUITY CURVE ---
    ax2 = plt.subplot(gs[1], sharex=ax1)
    ax2.plot(equity_curve.index, equity_curve.values, color='#00ffe7', linewidth=2.5, alpha=0.95, label='Equity Curve', zorder=1)
    ax2.fill_between(equity_curve.index, equity_curve.values, color='#00ffe7', alpha=0.08)
    ax2.set_title('Equity Curve', color='white', fontsize=15)
    ax2.grid(False)
    ax2.set_facecolor('#181a20')

    # --- 3. VOLUME CHART ---
    ax3 = plt.subplot(gs[2], sharex=ax1)
    # Plot normal volume in dark gray
    ax3.bar(df.index, df['Volume'], color='#222', alpha=0.7, label='Volume')
    
    # Highlight the specific days where our volume breakout logic triggered
    spikes = signals['buy_signal']
    ax3.bar(df.index[spikes], df['Volume'][spikes], color='#39ff14', alpha=0.9, label='Breakout Volume')
    
    ax3.set_title('Volume (Breakout Spikes Highlighted)', color='white', fontsize=13)
    ax3.legend()
    ax3.set_facecolor('#181a20')
    
    # Render the UI
    plt.tight_layout()
    return fig