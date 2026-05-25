# shortstrangle.py — Description

## Overview

- Trading bot that locates option strikes on Delta Exchange, sells a call and a put
  (short strangle) at a target premium, sizes positions by a dollar risk budget,
  places market entries with bracket stop-loss, and submits separate take-profit
  limit orders. The bot is intended to run once per day at a configured time.

## Configuration / Environment

- Reads `API_KEY` and `API_SECRET` from a `.env` file using `python-dotenv`.
- Key parameters at top of the file: `TARGET_TIME`, `TARGET_PREMIUM`, `SL_MULTIPLIER`,
  `TAKE_PROFIT_PRICE`, and `MAX_RISK_PER_LEG`.
- `BASE_URL` points to Delta Exchange API endpoints.

## Main functions

- `generate_signature(method, path, payload, timestamp, secret)`
  - Builds HMAC-SHA256 signature for authenticated requests (handles GET query vs body).
- `send_request(method, endpoint, payload=None)`
  - Sends signed GET/POST requests to the exchange and returns parsed JSON or `None` on error.
- `get_best_strikes()`
  - Fetches product list and tickers, filters live BTC options for nearest expiry,
    selects the closest call and put whose mark price is >= `TARGET_PREMIUM`.
- `calculate_quantity(entry_price)`
  - Converts `MAX_RISK_PER_LEG` and `SL_MULTIPLIER` into a contract quantity.
  - Assumes 1 contract = 0.001 BTC and returns an integer >= 1.
- `place_entry_with_sl(product_id, side, entry_mark_price, quantity)`
  - Places a market order with a bracket stop-loss (stop given as `bracket_stop_loss_price`).
- `place_tp_limit(product_id, quantity)`
  - Places a separate reduce-only limit order at `TAKE_PROFIT_PRICE`.
- `run_bot()`
  - Waits until `TARGET_TIME`, finds strikes, sizes each leg, places entries and TPs,
    then breaks (script exits after a successful run). Retries every 10s until the minute matches.

## Behavior / Outputs

- When both call and put meet premium criteria, sells each leg and places TP limits.
- Prints status messages for API responses, order IDs, and failures.

## Notes & Recommendations

- Ensure `.env` contains `API_KEY` and `API_SECRET` and that the keys have
  required permissions on Delta Exchange.
- The time check uses exact string equality on `HH:MM`; run the script continuously
  or schedule it to start slightly before `TARGET_TIME` to avoid missing the minute.
- Risk sizing assumes `SL = entry * SL_MULTIPLIER` and calculates loss per BTC as
  `SL - entry` — verify this matches your intended SL semantics for option premiums.
- Test on paper or a sandbox account first. Confirm API fields `product_id`,
  `bracket_stop_loss_price`, and `reduce_only` match the exchange's current API spec.

