# Metrics_with_graph.py — Description

## Overview

- Computes backtest performance metrics from a backtest results table and shows a
  4-panel performance dashboard (equity curve, drawdown, daily PnL bars, and PnL distribution).

## Expected input

- Expects a DataFrame (or Excel file when run directly) with a `Date` column and a `net pnl`
  column containing daily PnL values.

## Main functions

- `calculate_backtest_metrics(df)`
  - Converts `Date` to datetime and sorts rows.
  - Computes `cum_pnl` (cumulative PnL) and `drawdown` (cum_pnl minus rolling max).
  - Calculates metrics: Sharpe Ratio (annualized using sqrt(365)), max drawdown,
    average & max drawdown durations (days), average monthly PnL, trade count, wins/losses,
    win rate, max win/loss, average win/loss, avg win/avg loss ratio, EV per day/month,
    and max win/loss streaks.
  - Returns the metrics dict and the DataFrame augmented with `cum_pnl` and `drawdown`.

- `plot_performance_dashboard(df)`
  - Produces a 2x2 matplotlib figure with:
    - Cumulative PnL (equity curve)
    - Underwater plot (drawdown)
    - Daily net PnL bar chart (green for wins, red for losses)
    - Histogram of daily PnL with mean line
  - Uses monthly date formatting on x-axes and shows the plot.

## Execution (if run as script)

- Loads the Excel file, calls `calculate_backtest_metrics`, prints each metric, and
  calls `plot_performance_dashboard` to display charts. If the data file is missing,
  prints an error message with the expected path.

## Notes & limitations

- Sharpe uses daily mean/std and annualizes by sqrt(365); confirm this matches your
  reporting convention (252 trading days vs 365 calendar days). I have used 365 since cryptos trade every day.

