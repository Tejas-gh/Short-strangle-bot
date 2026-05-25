import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_monte_carlo_full_risk_profile(file_path, iterations=100000):
    """
    Runs a Monte Carlo simulation on historical PnL to estimate 
    maximum depth, maximum duration of drawdowns, and extreme streaks.
    """
    # Helper function to efficiently count the max consecutive 'True' values
    def get_max_streak(condition_array):
        if not np.any(condition_array):
            return 0
        edges = np.diff(np.concatenate(([0], condition_array.view(np.int8), [0])))
        starts = np.where(edges == 1)[0]
        ends = np.where(edges == -1)[0]
        return np.max(ends - starts)

    # 1. Load the data
    df = pd.read_excel(file_path)
    
    if 'net pnl' not in df.columns:
        raise ValueError("Column 'net pnl' not found in the dataset.")
        
    pnl_array = df['net pnl'].dropna().values
    num_trades = len(pnl_array)
    
    print(f"Running {iterations} Monte Carlo simulations on {num_trades} periods...")
    
    # Arrays to store the metrics for each simulation
    simulated_max_dd_depth = np.zeros(iterations)
    simulated_max_dd_duration = np.zeros(iterations)
    simulated_max_win_streak = np.zeros(iterations)
    simulated_max_loss_streak = np.zeros(iterations)
    
    # 2. Run the simulations
    for i in range(iterations):
        # Resample PnL with replacement
        simulated_pnl = np.random.choice(pnl_array, size=num_trades, replace=True)
        
        # Calculate cumulative PnL and drawdown depth
        cum_pnl = np.cumsum(simulated_pnl)
        rolling_max = np.maximum.accumulate(cum_pnl)
        drawdown = cum_pnl - rolling_max
        
        # Store the maximum depth
        simulated_max_dd_depth[i] = np.min(drawdown)
        
        # Calculate maximum duration of the drawdown
        simulated_max_dd_duration[i] = get_max_streak(drawdown < 0)
        
        # Calculate maximum winning and losing streaks
        simulated_max_win_streak[i] = get_max_streak(simulated_pnl > 0)
        simulated_max_loss_streak[i] = get_max_streak(simulated_pnl < 0)

    # 3. Calculate Historical Baselines
    historical_cum = np.cumsum(pnl_array)
    historical_rmax = np.maximum.accumulate(historical_cum)
    historical_dd = historical_cum - historical_rmax
    
    historical_dd_depth = np.min(historical_dd)
    historical_dd_duration = get_max_streak(historical_dd < 0)
    historical_win_streak = get_max_streak(pnl_array > 0)
    historical_loss_streak = get_max_streak(pnl_array < 0)

    # 4. Analyze the Statistical Output
    print("\n--- Monte Carlo Drawdown DEPTH Analysis ---")
    print(f"Historical Max Drawdown:           {historical_dd_depth:.2f}")
    print(f"Median Simulated Max Drawdown:     {np.percentile(simulated_max_dd_depth, 50):.2f}")
    print(f"95% Confidence Worst Drawdown:     {np.percentile(simulated_max_dd_depth, 5):.2f}")
    print(f"Absolute Worst Simulated Drawdown: {np.min(simulated_max_dd_depth):.2f}")

    print("\n--- Monte Carlo Drawdown DURATION Analysis (Days/Trades) ---")
    print(f"Historical Max DD Duration:        {historical_dd_duration:.0f}")
    print(f"Median Simulated Max DD Duration:  {np.percentile(simulated_max_dd_duration, 50):.0f}")
    print(f"95% Confidence Longest Duration:   {np.percentile(simulated_max_dd_duration, 95):.0f}")
    print(f"Absolute Longest Simulated DD:     {np.max(simulated_max_dd_duration):.0f}")

    print("\n--- Monte Carlo STREAK Analysis (Days/Trades) ---")
    print(f"Historical Max Winning Streak:     {historical_win_streak:.0f}")
    print(f"Median Simulated Max Win Streak:   {np.percentile(simulated_max_win_streak, 50):.0f}")
    print(f"95% Confidence Longest Win Streak: {np.percentile(simulated_max_win_streak, 95):.0f}")
    print(f"Absolute Longest Sim. Win Streak:  {np.max(simulated_max_win_streak):.0f}")
    print(f"-")
    print(f"Historical Max Losing Streak:      {historical_loss_streak:.0f}")
    print(f"Median Simulated Max Loss Streak:  {np.percentile(simulated_max_loss_streak, 50):.0f}")
    print(f"95% Confidence Longest Loss Streak:{np.percentile(simulated_max_loss_streak, 95):.0f}")
    print(f"Absolute Longest Sim. Loss Streak: {np.max(simulated_max_loss_streak):.0f}")

# Execute the function
# Replace with your specific file path. 
data_path = r"Strategies Github/Short Strangle/Backtest/after fees/after_fees_Backtest_2025-01-01_to_2026-01-31.xlsx"
run_monte_carlo_full_risk_profile(data_path, iterations=100000)