import pandas as pd
import numpy as np
import plotly.graph_objects as go

def plot_all_days_volatility_interactive(csv_file):
    """
    Loads OHLCV data, calculates Parkinson volatility, and creates an 
    interactive HTML plot using Plotly.
    """
    print("Processing data for interactive plot...")
    
    # 1. Load the data
    df = pd.read_csv(csv_file, parse_dates=['timestamp'], index_col='timestamp')
    
    # 2. Calculate Parkinson Volatility
    constant = 1 / (4 * np.log(2))
    df['parkinson_vol'] = np.sqrt(constant * (np.log(df['high'] / df['low']))**2)
    
    # 3. Add helper columns for grouping
    df['day_name'] = df.index.day_name()
    df['hour'] = df.index.hour
    
    # 4. Group data by Hour and Day to get the mean volatility
    mean_vol_df = df.pivot_table(index='hour', columns='day_name', values='parkinson_vol', aggfunc='mean')
    
    # 5. Sort columns (Monday -> Sunday)
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    mean_vol_df = mean_vol_df.reindex(columns=days_order)
    
    # 6. Create the Plotly Figure
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
    
    for day, color in zip(days_order, colors):
        if day in mean_vol_df.columns:
            fig.add_trace(go.Scatter(
                x=mean_vol_df.index,
                y=mean_vol_df[day],
                mode='lines+markers',
                name=day,
                line=dict(color=color, width=3),
                hovertemplate='<b>' + day + '</b><br>Hour: %{x}:00<br>Vol: %{y:.6f}<extra></extra>'
            ))
    
    # 7. Update Layout for Professional Look
    fig.update_layout(
        title='Intraday Parkinson Volatility Profile: All Days of the Week',
        xaxis=dict(
            title='Hour of Day (Local Time)',
            tickmode='linear',
            tick0=0,
            dtick=1,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        yaxis=dict(
            title='Mean Volatility (Parkinson)',
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        legend_title="Day of Week",
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # 8. Save and Show
    # This generates a standalone HTML file you can open in any browser
    output_path = "volatility_profile.html"
    fig.write_html(output_path)
    print(f"Interactive plot saved to: {output_path}")
    fig.show()

# --- Execution ---
filepath = "Volatility Analysis/btc_1hour.csv"
plot_all_days_volatility_interactive(filepath)