import requests
import time
import hmac
import hashlib
import json
import urllib.parse
from datetime import datetime, timedelta
import sys

# 1. Import these two modules to handle environment variables
import os
from dotenv import load_dotenv

# 2. Tell Python to find and load the .env file
load_dotenv()

# ================== CONFIGURATION ================== #
# 3. Fetch the keys safely from the hidden environment
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://api.india.delta.exchange" 

# TRADING SETTINGS
TARGET_TIME = "22:09"       # HH:MM (24-hour format)
TARGET_PREMIUM = 30.0       # Minimum Premium to accept
SL_MULTIPLIER = 4.0         # SL = Entry x 4
TAKE_PROFIT_PRICE = 1.0     
MAX_RISK_PER_LEG = 0.80      # Max dollars to lose per leg

# ---------------- AUTHENTICATION ---------------- #

def generate_signature(method, path, payload, timestamp, secret):
    if method == 'GET' and payload:
        query_string = urllib.parse.urlencode(payload)
        path = f"{path}?{query_string}"
        body_str = ""
    else:
        body_str = json.dumps(payload) if payload else ""

    signature_data = method + timestamp + path + body_str
    return hmac.new(
        secret.encode('utf-8'),
        signature_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def send_request(method, endpoint, payload=None):
    timestamp = str(int(time.time()))
    path = endpoint
    
    signature = generate_signature(method, path, payload, timestamp, API_SECRET)
    
    headers = {
        "api-key": API_KEY,
        "timestamp": timestamp,
        "signature": signature,
        "Content-Type": "application/json"
    }

    url = BASE_URL + path
    
    try:
        if method == "GET":
            response = requests.get(url, params=payload, headers=headers)
        else:
            response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

# ---------------- MARKET DATA LOGIC ---------------- #

def get_best_strikes():
    print("🔍 Scanning Option Chain for premiums >= $30...")
    data = send_request("GET", "/v2/products")
    if not data or not data.get('result'):
        print("❌ Failed to fetch products.")
        return None, None

    products = data['result']
    btc_options = [p for p in products if (p['symbol'].startswith("C-BTC") or p['symbol'].startswith("P-BTC")) and p['state'] == "live"]

    if not btc_options:
        print("❌ No active BTC options found.")
        return None, None

    btc_options.sort(key=lambda x: x['settlement_time'])
    nearest_expiry_ts = btc_options[0]['settlement_time']
    todays_options = [p for p in btc_options if p['settlement_time'] == nearest_expiry_ts]
    
    tickers_resp = send_request("GET", "/v2/tickers")
    if not tickers_resp: return None, None
    
    price_map = {}
    for t in tickers_resp['result']:
        if t.get('mark_price') is not None:
            try:
                price_map[t['symbol']] = float(t['mark_price'])
            except: continue

    best_ce = None
    best_pe = None
    closest_ce_diff = 9999
    closest_pe_diff = 9999

    for opt in todays_options:
        symbol = opt['symbol']
        price = price_map.get(symbol)
        if price is None: continue

        # --- STRICT FILTER ---
        if price >= TARGET_PREMIUM:
            
            diff = abs(price - TARGET_PREMIUM)

            if "C-BTC" in symbol:
                if diff < closest_ce_diff:
                    closest_ce_diff = diff
                    best_ce = {**opt, "current_price": price}
            elif "P-BTC" in symbol:
                if diff < closest_pe_diff:
                    closest_pe_diff = diff
                    best_pe = {**opt, "current_price": price}
        # ---------------------

    return best_ce, best_pe

# ---------------- DYNAMIC RISK CALCULATION ---------------- #

def calculate_quantity(entry_price):
    """
    Calculates quantity based on MAX_RISK_PER_LEG.
    Formula: Qty = Risk / (SL_Price - Entry_Price)
    """
    sl_price = entry_price * SL_MULTIPLIER
    loss_per_contract = sl_price - entry_price
    
    if loss_per_contract <= 0:
        return 1 
        
    raw_qty = MAX_RISK_PER_LEG / loss_per_contract
    
    # 1 Contract = 0.001 BTC. So we multiply raw BTC qty by 1000 to get lots.
    qty = round(raw_qty * 1000) 
    
    # Ensure at least 1 contract is traded
    final_qty = max(1, qty)
    
    print(f"⚖️ Risk Calc: Entry {entry_price} | SL {sl_price} | Loss/BTC {loss_per_contract:.2f} | Risk ${MAX_RISK_PER_LEG} -> Qty {final_qty}")
    return final_qty

# ---------------- EXECUTION LOGIC ---------------- #

def place_entry_with_sl(product_id, side, entry_mark_price, quantity):
    """
    Places Entry with Dynamic Quantity
    """
    sl_price = round(entry_mark_price * SL_MULTIPLIER, 2)
    
    print(f"🚀 Placing Entry for ID {product_id} | Qty: {quantity} | SL: {sl_price} (Bracket)")
    
    payload = {
        "product_id": product_id,
        "size": quantity, 
        "side": side,
        "order_type": "market_order",
        "bracket_stop_loss_price": str(sl_price),
        "bracket_stop_trigger_method": "mark_price"
    }
    
    return send_request("POST", "/v2/orders", payload)

def place_tp_limit(product_id, quantity):
    """
    Places TP with Dynamic Quantity
    """
    tp_price = TAKE_PROFIT_PRICE
    
    print(f"🎯 Placing separate TP Limit for ID {product_id} | Qty: {quantity} at ${tp_price}")
    
    payload = {
        "product_id": product_id,
        "size": quantity, 
        "side": "buy",
        "order_type": "limit_order",
        "limit_price": str(tp_price),
        "post_only": True,
        "reduce_only": True 
    }
    
    return send_request("POST", "/v2/orders", payload)

# ---------------- MAIN LOOP ---------------- #

def run_bot():
    print(f"🤖 Bot Started. Waiting for {TARGET_TIME}...")
    print(f"Strategy: Sell Call/Put >= ${TARGET_PREMIUM}.")
    print(f"Risk Management: Max Loss ${MAX_RISK_PER_LEG} per leg.")

    # We remove 'while True' logic regarding day-looping. 
    # This script is designed to run ONCE per day via Task Scheduler.

    while True:
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")

        if current_time_str == TARGET_TIME:
            print(f"\n⏰ Time Reached: {current_time_str}. Executing Strategy.")
            
            # 1. Find Strikes
            ce, pe = get_best_strikes()
            
            if ce and pe:
                print(f"✅ Selected Call: {ce['symbol']} (Mark: {ce['current_price']})")
                print(f"✅ Selected Put:  {pe['symbol']} (Mark: {pe['current_price']})")
                
                # --- CALL LEG ---
                qty_ce = calculate_quantity(ce['current_price'])
                ce_res = place_entry_with_sl(ce['id'], "sell", ce['current_price'], qty_ce)
                
                if ce_res and ce_res.get('success'):
                        print(f"✅ Call Entry Placed. ID: {ce_res['result']['id']}")
                        place_tp_limit(ce['id'], qty_ce)
                else:
                        print(f"❌ Call Entry Failed! {ce_res}")

                # --- PUT LEG ---
                qty_pe = calculate_quantity(pe['current_price'])
                pe_res = place_entry_with_sl(pe['id'], "sell", pe['current_price'], qty_pe)
                
                if pe_res and pe_res.get('success'):
                        print(f"✅ Put Entry Placed. ID: {pe_res['result']['id']}")
                        place_tp_limit(pe['id'], qty_pe)
                else:
                        print(f"❌ Put Entry Failed! {pe_res}")
                
                print("🏁 Strategy executed successfully. Exiting code.")
                break # <--- THIS STOPS THE SCRIPT AFTER TRADING
            else:
                print("❌ No strikes found >= $30. Retrying in 10s...")
                time.sleep(10)
        
        else:
            # Script started early? Wait 10s and check again.
            # If script started late (e.g., 22:43), you might want to adjust logic,
            # but for now it waits for the exact minute.
            time.sleep(10)

if __name__ == "__main__":
    run_bot()