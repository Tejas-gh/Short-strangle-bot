import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def calculate_backtest_metrics(df):
    # Ensure Date is datetime and sort
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    
    daily_pnl = df['net pnl']
    
    # Calculate and store Cumulative PnL and Drawdown in the DataFrame for plotting
    df['cum_pnl'] = daily_pnl.cumsum()
    rolling_max = df['cum_pnl'].cummax()
    df['drawdown'] = df['cum_pnl'] - rolling_max
    
    metrics = {}

    # 1. Sharpe Ratio
    daily_mean = daily_pnl.mean()
    daily_std = daily_pnl.std()
    metrics['Sharpe Ratio'] = (daily_mean / daily_std) * np.sqrt(365) if daily_std != 0 else 0

    # 2. Drawdowns
    metrics['Max Drawdown (Absolute)'] = df['drawdown'].min()

    # 3 & 4. Drawdown Durations
    is_drawdown = df['drawdown'] < 0
    dd_groups = (~is_drawdown).cumsum()
    
    if is_drawdown.any():
        dd_durations = df[is_drawdown].groupby(dd_groups[is_drawdown])['Date'].agg(
            lambda x: (x.max() - x.min()).days + 1
        )
        metrics['Average Drawdown Duration (Days)'] = dd_durations.mean()
        metrics['Max Drawdown Period (Days)'] = dd_durations.max()
    else:
        metrics['Average Drawdown Duration (Days)'] = 0
        metrics['Max Drawdown Period (Days)'] = 0

    # 5. Average Monthly Returns (PnL)
    monthly_pnl = df.set_index('Date')['net pnl'].resample('ME').sum()
    metrics['Average Monthly PnL'] = monthly_pnl.mean()

    # 6. Trade Count
    metrics['Trade Count'] = len(daily_pnl)

    # 7. Win Rate, Total Wins, Total Loss, Max Win, Max Loss
    wins = daily_pnl[daily_pnl > 0]
    losses = daily_pnl[daily_pnl < 0]
    
    total_wins = len(wins)
    total_losses = len(losses)
    
    metrics['Total Wins'] = total_wins
    metrics['Total Losses'] = total_losses
    metrics['Win Rate (%)'] = (total_wins / len(daily_pnl)) * 100 if len(daily_pnl) > 0 else 0
    metrics['Max Win'] = daily_pnl.max()
    metrics['Max Loss'] = daily_pnl.min()

    # 8. Avg Win / Avg Loss Ratio
    avg_win = wins.mean() if not wins.empty else 0
    avg_loss = abs(losses.mean()) if not losses.empty else 0
    metrics['Avg Win'] = avg_win
    metrics['Avg Loss (Absolute)'] = avg_loss
    metrics['Avg Win / Avg Loss Ratio'] = (avg_win / avg_loss) if avg_loss != 0 else np.inf

    # 9. Expected Value (EV)
    metrics['EV per Day'] = daily_mean
    metrics['EV per Month'] = metrics['Average Monthly PnL']

    # 10. Max Win Streak, Max Loss Streak
    signs = np.sign(daily_pnl)
    signs = signs[signs != 0] 
    
    streak_groups = (signs != signs.shift()).cumsum()
    streak_counts = signs.groupby(streak_groups).agg(['count', 'first'])
    
    win_streaks = streak_counts[streak_counts['first'] == 1]['count']
    loss_streaks = streak_counts[streak_counts['first'] == -1]['count']
    
    metrics['Max Win Streak'] = win_streaks.max() if not win_streaks.empty else 0
    metrics['Max Loss Streak'] = loss_streaks.max() if not loss_streaks.empty else 0

    return metrics, df

def plot_performance_dashboard(df):
    """Generates a 4-panel subplot of the backtest results."""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Strategy Performance Dashboard', fontsize=16)

    # Top Left: Cumulative PnL
    axes[0, 0].plot(df['Date'], df['cum_pnl'], color='blue', linewidth=2)
    axes[0, 0].set_title('Cumulative PnL (Equity Curve)')
    axes[0, 0].set_ylabel('PnL')
    axes[0, 0].grid(True, linestyle='--', alpha=0.6)
    axes[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    # Top Right: Drawdown
    axes[0, 1].fill_between(df['Date'], df['drawdown'], 0, color='red', alpha=0.5)
    axes[0, 1].set_title('Underwater Plot (Drawdown)')
    axes[0, 1].set_ylabel('Drawdown')
    axes[0, 1].grid(True, linestyle='--', alpha=0.6)
    axes[0, 1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    # Bottom Left: Daily PnL
    colors = ['green' if val > 0 else 'red' for val in df['net pnl']]
    axes[1, 0].bar(df['Date'], df['net pnl'], color=colors, width=1)
    axes[1, 0].set_title('Daily Net PnL')
    axes[1, 0].set_ylabel('PnL')
    axes[1, 0].grid(True, linestyle='--', alpha=0.6)
    axes[1, 0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    # Bottom Right: PnL Distribution
    axes[1, 1].hist(df['net pnl'], bins=50, color='purple', alpha=0.7, edgecolor='black')
    axes[1, 1].axvline(df['net pnl'].mean(), color='yellow', linestyle='dashed', linewidth=2, label='Mean')
    axes[1, 1].set_title('Distribution of Daily Returns')
    axes[1, 1].set_xlabel('Daily PnL')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].legend()
    axes[1, 1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

# Execution Block
if __name__ == "__main__":
    # Load data
    data_path = r"Strategies Github/Short Strangle/Backtest/after fees/after_fees_Backtest_2025-01-01_to_2026-01-31.xlsx"
    
    try:
        df = pd.read_excel(data_path) 
        
        # Calculate metrics and get updated DataFrame
        results, processed_df = calculate_backtest_metrics(df)
        
        # Print metrics
        print("--- Backtest Metrics ---")
        for key, value in results.items():
            print(f"{key}: {round(value, 2) if isinstance(value, float) else value}")
            
        # Plot the dashboard
        plot_performance_dashboard(processed_df)
        
    except FileNotFoundError:
        print(f"Error: Could not find the file at {data_path}. Please check the path.")