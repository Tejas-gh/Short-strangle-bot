import pandas as pd
import numpy as np
from itertools import combinations

def optimize_trading_days(file_path):
    """
    Evaluates trading performance for all 127 possible combinations 
    of days in a week and exports them sorted by day combinations.
    """
    # 1. Load the data
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return None

    # 2. Convert 'Date' and extract Day/Month
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    df['DayName'] = df['Date'].dt.day_name().str.lower()
    df['Month'] = df['Date'].dt.to_period('M')

    # 3. Define Win/Loss
    df['Result'] = np.where(df['Total PnL'] > 0, 'Win', 'Loss')

    all_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    # Mapping days to numbers to maintain chronological sorting
    day_map = {day: index + 1 for index, day in enumerate(all_days)}
    
    results_list = []

    # 4. Generate all combinations (1 to 7 days)
    for r in range(1, 8):
        for combo in combinations(all_days, r):
            included_days = list(combo)
            
            # Create a sorting key based on chronological day order
            # E.g., ('monday', 'wednesday') becomes (2, 1, 3) -> (length, day1, day2)
            sort_key = [r] + [day_map[d] for d in included_days]
            
            # Filter the dataframe to ONLY include the selected combination
            df_filtered = df[df['DayName'].isin(included_days)].copy()
            
            total_trades = len(df_filtered)
            if total_trades == 0:
                continue
            
            # Calculate overall metrics
            wins = len(df_filtered[df_filtered['Result'] == 'Win'])
            overall_win_rate = (wins / total_trades) * 100
            
            # Calculate monthly win rates to find the standard deviation
            monthly_stats = df_filtered.groupby('Month')['Result'].apply(
                lambda x: (x == 'Win').sum() / len(x) * 100 if len(x) > 0 else 0
            )
            
            mean_monthly_wr = monthly_stats.mean()
            std_monthly_wr = monthly_stats.std(ddof=1)
            
            if pd.isna(std_monthly_wr):
                std_monthly_wr = 0.0

            # Store the results with the sort key
            results_list.append({
                '_sort_key': sort_key, # Hidden column for sorting
                'Included Days': ', '.join(included_days).title(),
                'Days Traded per Week': r,
                'Total Trades': total_trades,
                'Overall Win Rate (%)': overall_win_rate,
                'Monthly Mean WR (%)': mean_monthly_wr,
                'Monthly Std Dev (%)': std_monthly_wr
            })

    # 5. Convert to DataFrame
    results_df = pd.DataFrame(results_list)
    
    # Sort logically by the combinations rather than Win Rate
    # Because lists/tuples evaluate element by element, this perfectly sorts by:
    # 1. Number of days (r)
    # 2. Chronological order of the first day, then the second day, etc.
    results_df = results_df.sort_values(by='_sort_key').reset_index(drop=True)
    
    # Drop the temporary sorting key so it doesn't show up in Excel
    results_df = results_df.drop(columns=['_sort_key'])
    
    # 6. Format numerical columns for readability
    results_df['Overall Win Rate (%)'] = results_df['Overall Win Rate (%)'].round(2)
    results_df['Monthly Mean WR (%)'] = results_df['Monthly Mean WR (%)'].round(2)
    results_df['Monthly Std Dev (%)'] = results_df['Monthly Std Dev (%)'].round(2)
    
    return results_df

# --- Execution and Export ---
input_file = ''
output_file = ''

# Run the optimization
optimization_results = optimize_trading_days(input_file)

if optimization_results is not None:
    # Print a preview to the console
    print("Top 15 Sorted Combinations Preview:")
    print("-" * 100)
    print(optimization_results.head(15).to_string()) 
    
    # Export the full DataFrame to an Excel file
    optimization_results.to_excel(output_file, index=False)
    print("\n" + "=" * 60)
    print(f"SUCCESS: Combinatorially sorted results exported to '{output_file}'")
    print("=" * 60)