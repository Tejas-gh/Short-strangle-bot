# Optimization.py & Group_sorting.py — Description

## Optimization.py

### Overview

- Evaluates performance for every combination of weekdays (1 to 7 days) to find
  which day-of-week subsets produce the best trading outcomes, and exports the
  combinatorially-sorted results.

### Expected input

- An Excel file with a `Date` column (format `%d-%m-%Y`) and a `Total PnL` column.
  The script's `input_file` and `output_file` variables at the bottom must be set
  to the actual paths before execution.

### Main function

- `optimize_trading_days(file_path)`:
  - Loads the Excel file and parses `Date` into datetime, derives `DayName` and `Month`.
  - Labels each row as `Win` if `Total PnL` > 0 else `Loss`.
  - Iterates all 127 non-empty combinations of weekdays and filters the dataset
    to include only rows matching the chosen combination.
  - For each combination computes:
    - `Total Trades`
    - `Overall Win Rate (%)`
    - `Monthly Mean WR (%)` and `Monthly Std Dev (%)` (month-by-month win rates)
  - Collects results and sorts them using a hidden `_sort_key` that preserves
    chronological ordering and combination size (number of days selected).
  - Returns a formatted DataFrame of results.

### Outputs

- Returns a DataFrame sorted by combination size and day order. The script prints
  a preview and writes the full results to `output_file` when run directly.

### Notes & recommendations

- Set `input_file` and `output_file` to valid paths before running.
- Date parsing expects `%d-%m-%Y`; adjust the `to_datetime` format if your data
  uses a different format.
- The sorting key ensures combinations are grouped by length and chronological order
  (e.g., "Monday, Wednesday" will appear before "Monday, Thursday" because Wednesday comes before Thursday in the week).

---

## Group_sorting.py

### Overview

- Groups optimization results into win-rate brackets (5% bins) and sorts combinations
  inside each bracket by monthly win-rate volatility (standard deviation). This helps
  surface high-win-rate combinations with lower variability.

### Expected input

- An Excel file (the output from `Optimization.py`) containing at least the columns:
  `Monthly Mean WR (%)` and `Monthly Std Dev (%)`.
  Set `input_filename` and `output_filename` variables at the bottom before running.

### Main function

- `group_and_sort_by_winrate(input_file, output_file)`:
  - Reads the input Excel file into a DataFrame.
  - Creates 5%-wide bins from 0% to 100% and labels them like `50-55%`.
  - Assigns each row to a `WR Bracket` based on `Monthly Mean WR (%)`.
  - Sorts rows by `WR Bracket` (descending, so highest brackets first) and within
    each bracket by `Monthly Std Dev (%)` ascending (lower volatility first).
  - Moves `WR Bracket` next to `Monthly Mean WR (%)` for easier reading and
    exports the sorted DataFrame to `output_file`.

### Outputs

- Writes an Excel file with grouped and sorted optimization results and returns the
  sorted DataFrame. The script also prints a console preview of the top rows.

### Notes & recommendations

- Ensure `Monthly Mean WR (%)` values are within 0-100; out-of-range values may
  fall outside defined bins and become NaN in `WR Bracket`.
- Adjust bin width if you need finer or coarser grouping.
