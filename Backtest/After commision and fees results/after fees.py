import pandas as pd
import numpy as np

# --- Configuration ---
FILE_PATH = 'Strategies Github/Short Strangle/Backtest/Backtest_2025-01-01_to_2026-01-31.xlsx'
OUTPUT_PATH = 'Strategies Github/Short Strangle/Backtest/after fees/after_fees_Backtest_2025-01-01_to_2026-01-31.xlsx'

GST_RATE = 0.18
CAP_RATE = 0.035
MAKER_FEE_RATE = 0.0001  # 0.01%
TAKER_FEE_RATE = 0.0001  # 0.01%
RISK_PER_LEG = 3.0       # The "-3" risk you mentioned

def calculate_fee_in_pct_units(premium, index_price, q_btc, is_taker):
    """Calculates the fee dynamically scaled to your 'pct' risk units."""
    if pd.isna(premium) or premium == 0 or pd.isna(q_btc) or q_btc == 0:
        return 0.0
        
    fee_rate = TAKER_FEE_RATE if is_taker else MAKER_FEE_RATE
    
    # 1. Calculate Base Trading Fee based on Notional (Qty of BTC * Index Price)
    trading_fee = q_btc * index_price * fee_rate
    
    # 2. Calculate 3.5% Premium Cap (Qty of BTC * Premium * 3.5%)
    premium_cap = CAP_RATE * q_btc * premium
    
    # 3. Apply Cap and 18% GST
    effective_fee = min(trading_fee, premium_cap)
    total_fee = effective_fee * (1 + GST_RATE)
    
    return total_fee

def process_dynamic_trading_data(file_path, output_path):
    df = pd.read_excel(file_path)
    
    # 1. Calculate the dynamic BTC Quantity for each leg based on the 3-point risk rule
    # Qty = 3 / (SL Level - Entry)
    # Using np.round(..., 3) to ensure it is a multiple of 0.001
    df['CE_Qty_BTC'] = np.where(
        (df['CE SL Level'] - df['CE Entry']) != 0, 
        np.round(RISK_PER_LEG / (df['CE SL Level'] - df['CE Entry']), 3), 
        0
    )
    
    df['PE_Qty_BTC'] = np.where(
        (df['PE SL Level'] - df['PE Entry']) != 0, 
        np.round(RISK_PER_LEG / (df['PE SL Level'] - df['PE Entry']), 3), 
        0
    )
    
    # 2. Calculate Entry Fees (Assuming entries are Limit orders -> Maker)
    df['CE_Entry_Fee_pct'] = df.apply(
        lambda row: calculate_fee_in_pct_units(row['CE Entry'], row['Ref Price'], row['CE_Qty_BTC'], is_taker=False), axis=1
    )
    df['PE_Entry_Fee_pct'] = df.apply(
        lambda row: calculate_fee_in_pct_units(row['PE Entry'], row['Ref Price'], row['PE_Qty_BTC'], is_taker=False), axis=1
    )
    
    # 3. Calculate Exit Fees (TP = Maker / SL = Taker)
    df['CE_Exit_Fee_pct'] = df.apply(
        lambda row: calculate_fee_in_pct_units(
            row['CE Exit'], row['Ref Price'], row['CE_Qty_BTC'], is_taker=(row['CE Status'] == 'SL Hit')
        ), axis=1
    )
    
    df['PE_Exit_Fee_pct'] = df.apply(
        lambda row: calculate_fee_in_pct_units(
            row['PE Exit'], row['Ref Price'], row['PE_Qty_BTC'], is_taker=(row['PE Status'] == 'SL Hit')
        ), axis=1
    )
    
    # 4. Total Commissions for the trade (in 'pct' units)
    df['Total_Commissions_pct'] = (
        df['CE_Entry_Fee_pct'] + 
        df['PE_Entry_Fee_pct'] + 
        df['CE_Exit_Fee_pct'] + 
        df['PE_Exit_Fee_pct']
    )
    
    # 5. Calculate Final Net PnL
    df['True_Net_PnL_After_Fees'] = df['net pnl'] - df['Total_Commissions_pct']
    
    df.to_excel(output_path, index=False)
    print(f"Success! Saved dynamic fee calculations to {output_path}")

if __name__ == "__main__":
    process_dynamic_trading_data(FILE_PATH, OUTPUT_PATH)