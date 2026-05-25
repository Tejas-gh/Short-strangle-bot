# 📈 Volatility Analysis: Parkinson Volatility Profiler

## 📖 Overview

The `interactivegraph.py` script generates a dynamic Plotly chart that visualizes the average intraday Parkinson volatility profile across each day of the week (Monday through Sunday). By analyzing historical hourly OHLC data, this tool helps identify the specific time windows and days where market volatility reliably contracts or expands.

## ⚙️ How It Works

### The Mathematics (Parkinson Volatility)
The script computes the Parkinson volatility for every individual row of price data. Unlike standard volatility measures that only use closing prices, the Parkinson method uses High and Low prices to capture intraday price extremes.

The constant factor is defined as:
$$C = \frac{1}{4 \ln(2)}$$

The per-row volatility is then calculated using the natural log of the High/Low ratio:
$$V = \sqrt{C \cdot \left(\ln\left(\frac{\text{High}}{\text{Low}}\right)\right)^2}$$

### Data Processing Pipeline
1. **Data Loading:** Loads hourly price data from a CSV file, parsing the `timestamp` column into a usable datetime index.
2. **Feature Engineering:** Extracts the `hour` and the `day_name` (weekday) from the timestamp to categorize the data.
3. **Aggregation:** Generates a pivot table that calculates the mean volatility for each specific hour (rows) across each day of the week (columns).
4. **Chronological Sorting:** Automatically reorders the columns to ensure the days appear in standard chronological order (Monday to Sunday).
5. **Visualization:** Plots each weekday as a distinct `lines+markers` trace. It features custom color coding and detailed hover information for precise data inspection.

## 📥 Input Requirements

The script requires a CSV file containing historical price data. The dataset must include at least the following columns:
1. `timestamp`
2. `high`
3. `low`

**Default Configuration:**
The current execution block is hardcoded to read from the following path:
`Volatility Analysis/btc_1hour.csv`

## 📤 Output

Executing the script produces the following:
1. **Interactive HTML File:** Generates and saves a `volatility_profile.html` file in your directory. This file is standalone and can be opened or hosted in any standard web browser.
2. **Live Chart Display:** Automatically opens the interactive Plotly chart in a new window, allowing you to zoom, pan, and isolate specific days for deeper analysis.