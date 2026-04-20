import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_all(df: pd.DataFrame, signals: pd.DataFrame, trades: pd.DataFrame, equity_curve: pd.Series):
    """
    Shows price, equity curve, and volume in a single interactive Plotly dashboard.
    """
    # Create the 3-row layout
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05,
                        row_heights=[0.5, 0.25, 0.25],
                        subplot_titles=("Price Chart with Breakouts", "Equity Curve", "Volume"))

    # --- 1. PRICE CHART ---
    # The main price line
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price',
                             line=dict(color='#00ffe7', width=2)), row=1, col=1)
    
    # Buy and Sell Markers
    if trades is not None and not trades.empty:
        buys = trades[trades['Type'] == 'Buy']
        sells = trades[trades['Type'] == 'Sell']
        
        fig.add_trace(go.Scatter(x=buys['Date'], y=buys['Price'], mode='markers', name='Buy Signal',
                                 marker=dict(symbol='triangle-up', color='#39ff14', size=14, line=dict(color='black', width=1))), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=sells['Date'], y=sells['Price'], mode='markers', name='Sell Signal',
                                 marker=dict(symbol='triangle-down', color='#ff073a', size=14, line=dict(color='black', width=1))), row=1, col=1)

    # --- 2. EQUITY CURVE ---
    # The account balance line with a subtle area fill below it
    fig.add_trace(go.Scatter(x=equity_curve.index, y=equity_curve.values, mode='lines', name='Equity Multiplier',
                             line=dict(color='#00ffe7', width=2),
                             fill='tozeroy', fillcolor='rgba(0, 255, 231, 0.1)'), row=2, col=1)

    # --- 3. VOLUME CHART ---
    # Base volume bars
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', 
                         marker_color='#333333', opacity=0.8), row=3, col=1)
    
    # Highlighted breakout volume bars
    spikes = signals['buy_signal']
    if spikes.any():
        breakout_dates = df.index[spikes]
        breakout_vols = df['Volume'][spikes]
        fig.add_trace(go.Bar(x=breakout_dates, y=breakout_vols, name='Breakout Volume',
                             marker_color='#39ff14', opacity=1.0), row=3, col=1)

    # --- LAYOUT & STYLING ---
    fig.update_layout(
        height=850,
        template="plotly_dark",
        plot_bgcolor='#181a20',
        paper_bgcolor='#181a20',
        hovermode="x unified", # This gives a nice vertical line crosshair when hovering
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )

# --- LAYOUT & STYLING ---
    fig.update_layout(
        height=850,
        template="plotly_dark",
        plot_bgcolor='#181a20',
        paper_bgcolor='#181a20',
        hovermode="x",             # Changed from "x unified" to unlock the full-height crosshair
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )
    
    # This creates the vertical line that spans across all 3 charts simultaneously
    fig.update_xaxes(
        showgrid=False,
        showspikes=True,           # Turn on the vertical crosshair line
        spikemode='across',        # Force it to drop down through all subplots
        spikesnap='cursor',        # Lock it to the mouse pointer
        spikedash='solid',         # Make it a solid line
        spikecolor='#ffffff',      # Changed to white so it is highly visible
        spikethickness=1           # Keep it thin and clean
    )
    
    fig.update_yaxes(showgrid=False)

    return fig