import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# ---------------- CONFIGURATION ---------------- #
BASE_URL = "https://api.india.delta.exchange"
START_DATE = "2025-01-01"   # YYYY-MM-DD Start Date
END_DATE = "2025-06-01"     # End Date
TARGET_TIME_STR = "00:30"   # 12:30 AM
STRIKE_STEP = 200           

# STRATEGY SETTINGS
TARGET_PREMIUM = 30.0
SL_MULTIPLIER = 4.0      # <--- NEW: SL is 4x the Entry Price
TAKE_PROFIT = 1.0        # TP is still fixed at $1 (or you can make this dynamic too)

# ---------------- HELPER FUNCTIONS ---------------- #

def get_timestamp(date_str, time_str):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return int(dt.timestamp())

def get_candle(symbol, timestamp):
    endpoint = f"{BASE_URL}/v2/history/candles"
    params = {
        "symbol": symbol, "resolution": "1m", "start": timestamp, "end": timestamp + 60 
    }
    try:
        r = requests.get(endpoint, params=params, timeout=5)
        data = r.json()
        if 'result' in data and data['result']:
            return data['result'][0] 
        return None
    except:
        return None

def get_price_from_candle(candle, key='open'):
    if isinstance(candle, dict):
        return float(candle.get(key, 0))
    if isinstance(candle, list):
        idx_map = {'time': 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4}
        return float(candle[idx_map.get(key, 1)])
    return 0.0

def get_btc_price_at_time(timestamp):
    symbols = [".DEXBTUSDT"] 
    for sym in symbols:
        candle = get_candle(sym, timestamp)
        if candle:
            return get_price_from_candle(candle, 'open')
    return None

def find_best_strike(btc_price, timestamp, option_type, date_str):
    dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
    date_suffix = dt_obj.strftime("%d%m%y")
    atm_strike = int(round(btc_price / STRIKE_STEP)) * STRIKE_STEP
    
    best_strike = None
    closest_diff = 9999
    
    multiplier = 1 if option_type == 'C' else -1
    search_range = range(0, 40) 

    for i in search_range:
        strike = atm_strike + (i * STRIKE_STEP * multiplier)
        symbol = f"{option_type}-BTC-{strike}-{date_suffix}"
        candle = get_candle(symbol, timestamp)
        
        if candle:
            price = get_price_from_candle(candle, 'open')
            if price >= TARGET_PREMIUM:
                diff = abs(price - TARGET_PREMIUM)
                if diff < closest_diff:
                    closest_diff = diff
                    best_strike = {
                        "symbol": symbol, "entry_price": price, "timestamp": timestamp, "type": option_type
                    }
    return best_strike

def simulate_single_leg(leg_data, end_ts):
    symbol = leg_data['symbol']
    entry_price = leg_data['entry_price']
    start_ts = leg_data['timestamp']
    
    # --- CALCULATE DYNAMIC STOP LOSS ---
    calculated_sl = entry_price * SL_MULTIPLIER
    # -----------------------------------

    endpoint = f"{BASE_URL}/v2/history/candles"
    params = { "symbol": symbol, "resolution": "1m", "start": start_ts, "end": end_ts }
    
    try:
        r = requests.get(endpoint, params=params, timeout=10)
        history = r.json().get('result', [])
    except:
        return {"pnl": 0.0, "exit_price": 0.0, "sl_level": calculated_sl, "status": "Error"}

    if not history:
        return {"pnl": 0.0, "exit_price": 0.0, "sl_level": calculated_sl, "status": "No Data"}

    history.reverse()
    
    for candle in history:
        high = get_price_from_candle(candle, 'high')
        low = get_price_from_candle(candle, 'low')
        
        # CHECK DYNAMIC SL
        if high >= calculated_sl:
            return {
                "pnl": entry_price - calculated_sl, 
                "exit_price": calculated_sl, 
                "sl_level": calculated_sl,
                "status": "SL Hit"
            }

        # CHECK TP
        if low <= TAKE_PROFIT:
            return {
                "pnl": entry_price - TAKE_PROFIT, 
                "exit_price": TAKE_PROFIT, 
                "sl_level": calculated_sl,
                "status": "TP Hit"
            }

    last_candle = history[-1]
    close_price = get_price_from_candle(last_candle, 'close')
    return {
        "pnl": entry_price - close_price, 
        "exit_price": close_price, 
        "sl_level": calculated_sl,
        "status": "Expired"
    }

# ---------------- MAIN EXECUTION ---------------- #

def run_batch_backtest():
    print(f"Starting Batch Backtest: {START_DATE} to {END_DATE}")
    print(f"Strategy: SL = Entry x {SL_MULTIPLIER} | TP = {TAKE_PROFIT}")
    print("---------------------------------------------------")
    
    start_dt = datetime.strptime(START_DATE, "%Y-%m-%d")
    end_dt = datetime.strptime(END_DATE, "%Y-%m-%d")
    delta = end_dt - start_dt
    
    results = []

    for i in range(delta.days + 1):
        current_date = (start_dt + timedelta(days=i)).strftime("%Y-%m-%d")
        print(f"Processing {current_date}...", end="\r")
        
        start_ts = get_timestamp(current_date, TARGET_TIME_STR)
        end_of_day_ts = start_ts + (24 * 60 * 60)
        
        btc_price = get_btc_price_at_time(start_ts)
        
        row = {
            "Date": current_date,
            "Ref Price": btc_price if btc_price else 0,
            "CE Strike": None, "CE Entry": 0, "CE SL Level": 0, "CE Exit": 0, "CE PnL": 0, "CE Status": "N/A",
            "PE Strike": None, "PE Entry": 0, "PE SL Level": 0, "PE Exit": 0, "PE PnL": 0, "PE Status": "N/A",
            "Total PnL": 0
        }

        if btc_price:
            call_leg = find_best_strike(btc_price, start_ts, 'C', current_date)
            put_leg = find_best_strike(btc_price, start_ts, 'P', current_date)
            
            if call_leg:
                ce_res = simulate_single_leg(call_leg, end_of_day_ts)
                row.update({
                    "CE Strike": call_leg['symbol'],
                    "CE Entry": call_leg['entry_price'],
                    "CE SL Level": ce_res['sl_level'],
                    "CE Exit": ce_res['exit_price'],
                    "CE Status": ce_res['status'],
                    "CE PnL": ce_res['pnl']
                })
            
            if put_leg:
                pe_res = simulate_single_leg(put_leg, end_of_day_ts)
                row.update({
                    "PE Strike": put_leg['symbol'],
                    "PE Entry": put_leg['entry_price'],
                    "PE SL Level": pe_res['sl_level'],
                    "PE Exit": pe_res['exit_price'],
                    "PE Status": pe_res['status'],
                    "PE PnL": pe_res['pnl']
                })

            row["Total PnL"] = row["CE PnL"] + row["PE PnL"]
        
        results.append(row)
        time.sleep(0.05)

    print("\nBacktest Complete! Saving CSV...")
    
    df = pd.DataFrame(results)
    
    # Organized Columns
    cols = ["Date", "Ref Price", 
            "CE Strike", "CE Entry", "CE SL Level", "CE Exit", "CE PnL", 
            "PE Strike", "PE Entry", "PE SL Level", "PE Exit", "PE PnL", 
            "Total PnL", "CE Status", "PE Status"]
    
    df = df[cols]
    filename = f"Backtest_{START_DATE}_to_{END_DATE}.csv"
    df.to_csv(filename, index=False)
    
    print(f"✅ Results exported to: {filename}")
    print(df[["Date", "Total PnL", "CE Status", "PE Status"]].head())

if __name__ == "__main__":
    run_batch_backtest()