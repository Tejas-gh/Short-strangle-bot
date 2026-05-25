# Montecarlo_Simulation.py — Description

## Overview

- Performs a Monte Carlo simulation on historical daily PnL to estimate possible equity
  curve outcomes and drawdown statistics by resampling past trade PnLs with replacement.

## Expected input

- An Excel file (or DataFrame) containing a `net pnl` column with sequential per-trade or
  per-day PnL values. The script currently sets `data_path = r"path"` at the bottom — update
  this to the real file path before running.

## Main function

- `run_monte_carlo_with_plot(file_path, iterations=1000)`
  - Loads PnL data from `file_path` and validates presence of `net pnl` column.
  - For `iterations` times, resamples the `net pnl` array with replacement to build
    simulated PnL sequences and computes cumulative equity curves and max drawdowns.
  - Computes and prints: historical max drawdown, median simulated max drawdown,
    95% confidence worst drawdown (5th percentile), and the absolute worst simulated drawdown.
  - Plots: a background of all simulated equity curves (low-opacity), and highlighted
    lines for the historical equity curve, median simulated curve, worst 5% curve, and best 5% curve.

## Outputs

- Console statistics for drawdowns and an interactive matplotlib figure showing simulated
  equity curves and key percentiles.

## Notes & recommendations

- The simulation assumes trade independence and identical distribution when resampling.
- Adjust `iterations` for smoother percentile estimates (more iterations = more stability).
- Replace `data_path` with the correct path to your backtest results before executing.
- Consider seeding `np.random` for reproducible results when needed.

---


# Montecarlo_DD_duration.py — Description

## Overview

- Extended Monte Carlo simulation focused on risk-profile statistics: computes the
  distribution of maximum drawdown depth, maximum drawdown duration, and extreme
  win/loss streaks by resampling historical PnL sequences.

## Expected input

- An Excel file with a `net pnl` column (per-trade or per-day PnL). The script sets
  `data_path = r"path"` at the bottom — replace this with the actual file path.

## Main function

- `run_monte_carlo_full_risk_profile(file_path, iterations=100000)`
  - Loads `net pnl` from `file_path` and validates the column.
  - Uses an internal helper `get_max_streak(condition_array)` to quickly compute
    the longest consecutive True run in a boolean array.
  - For each simulation: resamples `net pnl` with replacement, computes cumulative PnL,
    rolling max, drawdown series, and then records:
    - maximum drawdown depth (min drawdown)
    - maximum drawdown duration (longest consecutive drawdown period)
    - maximum winning streak length
    - maximum losing streak length
  - After simulations, computes historical baselines from the true sequence and
    prints percentiles (median, 95% or 5th percentiles as appropriate) and absolute extremes.

## Outputs

- Console summary showing historical metrics and simulated percentile-based risk
  estimates for drawdown depth, drawdown duration, and win/loss streaks.

## Notes & recommendations

- The script currently uses a very large default `iterations=100000` which may be slow;
  reduce iterations for quicker runs during exploration.
- Replace `data_path` with the correct file path and consider seeding `np.random`
  for reproducible results.

