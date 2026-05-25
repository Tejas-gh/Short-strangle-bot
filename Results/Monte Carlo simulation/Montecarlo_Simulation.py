import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_monte_carlo_with_plot(file_path, iterations=1000):
    """
    Runs a Monte Carlo simulation on historical PnL and plots the resulting equity curves.
    """
    # 1. Load the data
    df = pd.read_excel(file_path)
    
    if 'net pnl' not in df.columns:
        raise ValueError("Column 'net pnl' not found in the dataset.")
        
    pnl_array = df['net pnl'].dropna().values
    num_trades = len(pnl_array)
    
    print(f"Running {iterations} Monte Carlo simulations on {num_trades} periods...")
    
    # Array to store the cumulative equity curves for plotting
    simulated_equity_curves = np.zeros((iterations, num_trades))
    simulated_max_drawdowns = np.zeros(iterations)
    
    # 2. Run the simulations
    for i in range(iterations):
        # Resample PnL with replacement
        simulated_pnl = np.random.choice(pnl_array, size=num_trades, replace=True)
        
        # Calculate cumulative PnL
        cum_pnl = np.cumsum(simulated_pnl)
        simulated_equity_curves[i] = cum_pnl
        
        # Calculate max drawdown for this iteration
        rolling_max = np.maximum.accumulate(cum_pnl)
        drawdown = cum_pnl - rolling_max
        simulated_max_drawdowns[i] = np.min(drawdown)

    # 3. Print Statistical Output
    historical_dd = np.min(np.cumsum(pnl_array) - np.maximum.accumulate(np.cumsum(pnl_array)))
    print("\n--- Monte Carlo Drawdown Analysis ---")
    print(f"Historical Max Drawdown:           {historical_dd:.2f}")
    print(f"Median Simulated Max Drawdown:     {np.percentile(simulated_max_drawdowns, 50):.2f}")
    print(f"95% Confidence Worst Drawdown:     {np.percentile(simulated_max_drawdowns, 5):.2f}")
    print(f"Absolute Worst Simulated Drawdown: {np.min(simulated_max_drawdowns):.2f}")

    # 4. Generate the Visualization
    plt.figure(figsize=(12, 6))
    
    # Plot all 1,000 simulated curves with low opacity (gray background)
    for i in range(iterations):
        plt.plot(simulated_equity_curves[i], color='gray', alpha=0.02)
        
    # Calculate statistical bounds across all simulations at each trade step
    median_curve = np.median(simulated_equity_curves, axis=0)
    worst_5_curve = np.percentile(simulated_equity_curves, 5, axis=0)
    best_5_curve = np.percentile(simulated_equity_curves, 95, axis=0)
    historical_curve = np.cumsum(pnl_array)
    
    # Plot the highlight lines over the gray noise
    plt.plot(historical_curve, color='blue', linewidth=2, label='Historical Equity Curve')
    plt.plot(median_curve, color='green', linewidth=2, linestyle='--', label='Median Simulated Curve')
    plt.plot(worst_5_curve, color='red', linewidth=2, linestyle='--', label='Worst 5% Probability Curve')
    plt.plot(best_5_curve, color='purple', linewidth=2, linestyle='--', label='Best 5% Probability Curve')
    
    plt.title('Monte Carlo Simulation: Equity Curves (1,000 Iterations)')
    plt.xlabel('Trade Number')
    plt.ylabel('Cumulative PnL')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Display the graph
    plt.tight_layout()
    plt.show()

# Execute the function
data_path = r"path"
run_monte_carlo_with_plot(data_path, iterations=1000)