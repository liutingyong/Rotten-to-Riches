# 🎲 Kalshi Betting System

A simple betting system for Kalshi prediction markets with safety features and user confirmation prompts.

## 🚀 Quick Start

1. **Set up your .env file:**
```env
KALSHI_URL=https://demo.kalshi.co/trade/YOUR-MARKET-TICKER
DEMO_KEYID=your_demo_key_id_here
DEMO_KEYFILE=KalshiDemoAPI.pem
```

2. **Run the system:**
```bash
python3 main.py
```

3. **Follow the prompts:**
   - Enter your Kalshi URL
   - Review market analysis
   - Choose whether to bet
   - Confirm each bet (1 share limit)

## 🛡️ Safety Features

- **1-Share Limit**: All bets limited to exactly 1 share
- **Double Confirmation**: Two confirmations required for each bet
- **Skip Options**: Can skip any bet or exit anytime
- **Balance Display**: Shows account balance before betting

## 📁 Files

- `main.py` - Main betting system (run this)
- `betting_system.py` - Core betting functionality
- `client_wrapper.py` - Wrapper for official Kalshi client
- `requirements.txt` - Python dependencies

## 🎯 How It Works

1. **Market Analysis**: Fetches and analyzes markets for your event
2. **Betting Recommendations**: Shows betting opportunities with confidence scores
3. **User Confirmation**: Asks you to confirm each bet (1 share limit)
4. **Bet Placement**: Places confirmed bets on Kalshi
5. **Summary**: Shows results of all betting activity

## 🔧 Setup

1. **Activate virtual environment:**
```bash
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure .env file** with your Kalshi credentials

4. **Place your private key file** (e.g., `KalshiDemoAPI.pem`) in this directory

## 🎓 Example Usage

```
🚀 Kalshi Market Analyzer
==================================================
🔗 Analyzing URL: https://demo.kalshi.co/trade/KXRTCONJURING-60
🌍 Environment: demo
Connected to demo environment

🔍 Finding all markets for event: KXRTCONJURING
📋 Found 3 markets: ['KXRTCONJURING-60', 'KXRTCONJURING-80', 'KXRTCONJURING-100']

📊 Market Analysis Results...
Successfully analyzed 3 markets!

🎲 BETTING WORKFLOW
==================================================
Do you want to proceed with betting analysis? (yes/no): yes

💰 ACCOUNT BALANCE
Available Balance: $100.00

🎯 BETTING RECOMMENDATIONS (2 opportunities):
1. Will The Conjuring 4 gross over $60M worldwide?
   Recommendation: BET YES
   Confidence: 75%
   Current Price: 45 cents

🛡️ SAFETY LIMIT: Betting exactly 1 share
Do you want to proceed with betting 1 share? (yes/no/skip): yes
Do you want to place this bet? (yes/no): yes

🚀 Placing bet order...
✅ Bet placed successfully!
Order ID: ORD-12345
```

## ⚠️ Important Notes

- **Start with demo environment** for safety
- **All bets are 1 share maximum** for risk management
- **Double confirmation required** for each bet
- **You can skip any bet** or exit anytime

## 🔮 Future: Sentiment Analysis Integration

The system is ready to integrate with your existing sentiment analysis modules:
- `src/basic_processing_and_sentiment_analysis/`
- `src/scikit_ensemble/`
- `src/webscraping/`

Replace the mock analysis in `betting_system.py` with your real sentiment analysis.

---

**Ready to start? Run `python main.py`**