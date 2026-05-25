import pandas as pd
import numpy as np

def group_and_sort_by_winrate(input_file, output_file):
    """
    Groups trading combinations into 5% win rate bins and sorts by standard deviation.
    """
    try:
        df = pd.read_excel(input_file)
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return None

    # 1. Define the bin edges and labels
    # Creates boundaries at 0, 5, 10... 95, 100
    bin_edges = range(0, 105, 5) 
    
    # Creates labels like '50-55%', '55-60%'
    bin_labels = [f"{i}-{i+5}%" for i in range(0, 100, 5)]

    # 2. Categorize the Monthly Mean WR into groups
    # right=False ensures a value exactly on the edge (e.g., 55.00) goes into the 55-60% group
    df['WR Bracket'] = pd.cut(
        df['Monthly Mean WR (%)'], 
        bins=bin_edges, 
        labels=bin_labels, 
        right=False
    )

    # 3. Sort the DataFrame
    # First by the 'WR Bracket' (descending: highest win rates at the top)
    # Then by 'Monthly Std Dev (%)' (ascending: lowest volatility at the top of each group)
    df_sorted = df.sort_values(
        by=['WR Bracket', 'Monthly Std Dev (%)'], 
        ascending=[False, True]
    ).reset_index(drop=True)

    # 4. Reorder columns so the 'WR Bracket' is next to the Mean WR for easy reading
    columns = list(df_sorted.columns)
    columns.insert(columns.index('Monthly Mean WR (%)'), columns.pop(columns.index('WR Bracket')))
    df_sorted = df_sorted[columns]

    # 5. Export to Excel
    df_sorted.to_excel(output_file, index=False)
    
    return df_sorted

# --- Execution ---
# Replace 'optimization_results.xlsx' with the name of your current file
input_filename = r"Strategies Github/Short Strangle/Results/Optimisation results/after fees/after_fees_optimized.xlsx"
output_filename = r"Strategies Github/Short Strangle/Results/Optimisation results/after fees/group_sorted.xlsx"

grouped_results = group_and_sort_by_winrate(input_filename, output_filename)

if grouped_results is not None:
    # Print a quick preview of the top rows
    print("Grouped and Sorted Results Preview (Highest WR Bracket, Lowest Risk First):")
    print("-" * 105)
    
    # Drop rows with NaN in WR Bracket just for the console preview to keep it clean
    preview_df = grouped_results.dropna(subset=['WR Bracket']).head(15)
    print(preview_df.to_string())
    
    print("\n" + "=" * 60)
    print(f"SUCCESS: Grouped results exported to '{output_filename}'")
    print("=" * 60)