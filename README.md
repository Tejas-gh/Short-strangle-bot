# Automated Short Strangle Strategy

An automated algorithmic trading bot designed to execute a short strangle strategy during statistically proven periods of low market volatility. The bot is written in Python, interfaces with the Delta Exchange API, and is fully automated using AWS infrastructure to ensure precise, serverless execution schedules.

## 📖 Overview

A short strangle involves selling an Out-of-the-Money (OTM) Call and an OTM Put simultaneously. The strategy profits when the underlying asset remains within the strike price range, allowing us to collect the theta (time decay) and benefit from dropping implied volatility. 

Because selling options exposes the seller to theoretically unlimited risk if the market trends aggressively, execution timing is everything. This bot is specifically scheduled to operate *only* during low-volatility windows.

## 📊 Volatility & Execution Strategy

Through backtesting and historical analysis of Parkinson Volatility, we identified specific days and times when market volatility reliably contracts. The bot's execution logic is strictly bound to these observations.

### Execution Schedule
The bot is scheduled to run on:
1. Wednesday, Thursday, Saturday, and Sunday
- Time: 12:30 AM 

### The Quantitative Rationale
1. **Time Selection (12:30 AM):** Average Parkinson volatility experiences a sharp drop immediately following the close of regular US market hours. By entering the market at 12:30 AM, the strategy capitalizes on this structural cool-down period, capturing premium while the underlying asset is statistically less likely to make erratic directional moves.
2. **Day Selection (Mid-week & Weekends):** The strategy intentionally avoids Mondays, Tuesdays, and Fridays. 
- **Monday & Tuesday:** Parkinson volatility spikes due to the post-weekend opening of the US and global market sessions as institutions price in weekend news.
- **Friday:** Volatility rises again as traders and institutions adjust their books, close positions, and hedge ahead of the weekend.
- By operating only on Wed, Thu, Sat, and Sun, the bot avoids the "whipsaw" effects of institutional volume and weekend-hedging behaviors.

## 🏗️ Architecture

The deployment architecture is designed to be lightweight, cost-effective, and entirely hands-off.

1. **Compute:** AWS EC2 Instance (runs the Python trading script).
2. **Automation:** Amazon EventBridge Scheduler.
3. **Workflow:** EventBridge is configured with a cron schedule to automatically start the EC2 instance at 12:30 AM on the designated days. The EC2 instance runs a startup script to execute the trade logic, log the outputs, and automatically shut itself down upon completion to optimize cloud compute costs.

## ⚙️ Prerequisites

To deploy this bot yourself, you will need:
1. An active AWS Account.
2. Python 3.x installed on your EC2 instance.
3. API Keys (Public and Secret) for Delta Exchange.

## 🚀 Setup & Deployment

1. **AWS Elastic IP & Delta Exchange Whitelisting (Crucial):**
- Allocate an Elastic IP address in your AWS EC2 console.
- Associate this Elastic IP with your EC2 instance. Since EventBridge stops and starts the instance, a standard public IP would change every time. An Elastic IP ensures your server's IP remains static.
- Log into Delta Exchange, navigate to your API settings, and whitelist this Elastic IP.
2. **Clone the repository:**
- Run the clone command: git clone https://github.com/yourusername/short-strangle-bot.git
- Navigate to directory: cd short-strangle-bot
3. **Install dependencies:**
- Run the pip command: pip install -r requirements.txt
4. **Configure Environment Variables:**
- Create a .env file in the root directory and add your API credentials securely:
+ API_KEY=your_public_key_here
+ API_SECRET=your_secret_key_here
5. **AWS EventBridge Setup:**
- Navigate to Amazon EventBridge in your AWS console.
- Create a new Schedule.
- Define the cron expression for 12:30 AM on Wed, Thu, Sat, Sun.
- Set the target as your specific EC2 instance, using the StartInstances API.

## 📊 Live Execution vs. Backtest Variance

To validate the statistical edge found in the Parkinson Volatility profiling, this strategy was forward-tested in a live environment using a real-money account on Delta Exchange.

* **Target Daily Risk:** 1.00%
* **Live Monthly PnL:** ~+6.00%
* **Observed Slippage:** Up to 20% on stop-loss market orders during high-volatility spikes. 

**Proof of Execution:**
To verify the system's live performance and AWS automation, please review the following artifacts in the `Live execution results` folder:
1. [View live trade log](<Live execution results/march 2026/delta_exchange_live_trades_mar_2026.csv>): A complete ledger of live entries and exits.
2. [View cleaned live trade log](<Live execution results/march 2026/cleaned_delta_exchange_live_trades_mar_2026.csv>): Cleaned PNL



## ⚠️ Challenges & Limitations

While this strategy has proven profitable in live testing (yielding ~6% per month on a small capital base at 1% risk per day), it has strict operational and market constraints. Anyone looking to deploy this should be aware of the following:

1. **Execution Slippage on Stop-Losses**
   - **Take-Profits (TP):** Experience zero slippage because they are submitted as resting limit orders.
   - **Stop-Losses (SL):** Are triggered as market orders to ensure an exit. During sudden market spikes, live testing has shown slippage of up to 20% on the SL execution. For example, a hard stop placed at 120 may realistically fill at 144 as it sweeps the available liquidity.

2. **Capital Scaling Constraints**
   - This strategy thrives on small capital. Crypto options order books (especially for specific OTM strikes) often have thin liquidity.
   - As capital and position sizes increase, the edge degrades. Larger market orders will sweep deeper into the order book on entries and SL exits, creating prohibitive slippage that eventually neutralizes the strategy's alpha.

3. **Blind Time-Based Execution**
   - The bot executes purely based on the clock (12:30 AM). It does not dynamically scan the macroeconomic calendar or parse real-time news. If an unexpected, high-impact market event occurs exactly at this time, the bot will still execute its trades blindly into a high-volatility environment.
  
4. **The Risk: Assuming the Future Looks Like the Past**
   - The strategy bets that weekends will always be quiet just because they have been in the past. But in financial markets, there is always a risk that historical patterns could suddenly change.

   - Why It Still Makes Sense (The Defense)
This quiet-weekend pattern isn't a random coincidence—it happens for a very concrete reason. Weekends are quiet because major global stock markets are closed. Trading activity jumps back up on Mondays and Tuesdays because large institutional investors return to their desks and start moving capital around again.

   - The Crypto Factor: A 24/7 Market
Even though the crypto market itself never sleeps and trades 24/7, it is still heavily driven by traditional finance. Because the massive institutional money tied to traditional equity markets exits on Friday nights and re-enters on Monday mornings, the crypto market still experiences this weekend slowdown.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading futures and options involves substantial risk of loss and is not suitable for all investors. Past performance of this quantitative logic is not indicative of future results. Use this bot at your own risk.
