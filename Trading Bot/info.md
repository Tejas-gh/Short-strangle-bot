# 🤖 Trading Execution: Short Strangle Bot

## 📖 Overview

The `shortstrangle.py` script is an automated trading bot designed to execute a short strangle strategy on Delta Exchange. It automatically locates appropriate option strikes, sells an Out-of-the-Money Call and Put at a target premium, sizes the positions based on a predefined dollar risk budget, places market entries with bracket stop-losses, and submits separate take-profit limit orders. The bot is intended to run once per day at a configured time.

## ⚙️ Configuration & Environment

1. **Authentication:**
- Reads `API_KEY` and `API_SECRET` from a `.env` file using the `python-dotenv` library.
- Ensure your API keys have the necessary trading permissions on Delta Exchange.
2. **Key Parameters (Top of File):**
- `TARGET_TIME`: The specific daily execution time.
- `TARGET_PREMIUM`: The minimum premium threshold for selecting strikes.
- `SL_MULTIPLIER`: The multiplier used to calculate the stop-loss price.
- `TAKE_PROFIT_PRICE`: The fixed take-profit target for the legs.
- `MAX_RISK_PER_LEG`: The maximum dollar risk allocated per leg for position sizing.
3. **Network:**
- `BASE_URL` is configured to point directly to the Delta Exchange API endpoints.

## 🛠️ Main Functions

1. **`generate_signature(method, path, payload, timestamp, secret)`**
- Builds the required HMAC-SHA256 signature for authenticated API requests, automatically handling both GET queries and POST bodies.
2. **`send_request(method, endpoint, payload=None)`**
- Sends signed requests to the exchange and returns parsed JSON data (or `None` on error).
3. **`get_best_strikes()`**
- Fetches the product list and tickers from the exchange.
- Filters live BTC options for the nearest expiry.
- Selects the closest Call and Put whose mark price is `>= TARGET_PREMIUM`.
4. **`calculate_quantity(entry_price)`**
- Converts `MAX_RISK_PER_LEG` and `SL_MULTIPLIER` into a tradable contract quantity.
- Assumes 1 contract = 0.001 BTC and strictly returns an integer `>= 1`.
5. **`place_entry_with_sl(product_id, side, entry_mark_price, quantity)`**
- Places a market order and simultaneously attaches a bracket stop-loss order.
6. **`place_tp_limit(product_id, quantity)`**
- Places a separate, reduce-only limit order at the predefined `TAKE_PROFIT_PRICE`.
7. **`run_bot()`**
- The main execution loop. It waits until `TARGET_TIME`, finds strikes, sizes each leg, places entries and TPs, and then safely exits the script.
- Retries API calls every 10 seconds until the precise target minute matches.

## 📊 Behavior & Outputs

1. **Execution Logic:**
- When both a Call and a Put successfully meet the premium criteria, the bot sells each leg and immediately places their respective TP limit orders.
2. **Console Output:**
- Prints detailed status messages for API responses, successful order IDs, and any execution failures for easy debugging via AWS CloudWatch or your local terminal.

## ⚠️ Notes & Recommendations

1. **Scheduling Precision:**
- The time check uses exact string equality (`HH:MM`). If running via AWS EventBridge or cron, ensure the instance boots up slightly *before* `TARGET_TIME` so the script is running when the minute rolls over.
2. **Risk Mathematics:**
- Risk sizing assumes `SL = entry * SL_MULTIPLIER`.
- It calculates loss per BTC as `SL - entry`. 
+ *Action Required:* Verify this matches your exact intended stop-loss semantics for option premiums.
3. **Testing:**
- **Strongly recommended:** Test this script on a paper trading or sandbox account first.
- Confirm that API fields like `product_id`, `bracket_stop_loss_price`, and `reduce_only` perfectly match Delta Exchange's current API documentation.