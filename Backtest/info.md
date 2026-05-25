# SHORT_STRANGLE_BACKTEST.py — Description

## Overview

- Batch backtest script for a short strangle options strategy on BTC (Delta Exchange API).
- For each date in the configured range, the script samples BTC spot at a target time,
  finds call and put option strikes whose premium is near a target premium, shorts them,
  and simulates PnL until end of day, stop-loss, or take-profit.

## Key configuration

- `BASE_URL`: API base for Delta Exchange
- `START_DATE` / `END_DATE`: backtest date range (YYYY-MM-DD)
- `TARGET_TIME_STR`: time of day to sample prices (HH:MM)
- `STRIKE_STEP`: option strike spacing (e.g. 200)
- `TARGET_PREMIUM`: desired option premium to short (float)
- `SL_MULTIPLIER`: stop-loss multiplier applied to entry price
- `TAKE_PROFIT`: fixed take-profit price

## Main functions

- `get_timestamp(date_str, time_str)`: convert date+time to epoch seconds
- `get_candle(symbol, timestamp)`: fetch 1-minute candle(s) from the API
- `get_price_from_candle(candle, key)`: extract open/high/low/close from API response
- `get_btc_price_at_time(timestamp)`: fetch BTC spot open price at timestamp
- `find_best_strike(...)`: search strikes around ATM to find option with premium >= `TARGET_PREMIUM`
- `simulate_single_leg(...)`: iterate minute candles for a leg, check dynamic SL (`entry*SL_MULTIPLIER`) and TP, compute PnL and exit reason
- `run_batch_backtest()`: orchestrates per-day sampling, strike selection, simulation, and CSV export

## Outputs

- Writes a CSV named `Backtest_{START_DATE}_to_{END_DATE}.csv` containing per-day legs, PnL,
  status (SL/TP/Expired), and total PnL.

## Notes / Limitations

- Uses public API endpoints without authentication; relies on 1m candle history availability.

