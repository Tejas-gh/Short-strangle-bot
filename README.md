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

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading futures and options involves substantial risk of loss and is not suitable for all investors. Past performance of this quantitative logic is not indicative of future results. Use this bot at your own risk.