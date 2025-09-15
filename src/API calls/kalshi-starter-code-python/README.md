# 🚀 Kalshi Market Analyzer

**Super simple Kalshi market analysis tool** - just paste a URL and get all market data!

## ⚡ Quick Start

### 1. Add Your Kalshi URL
Open your `.env` file and add:
```
KALSHI_URL=https://kalshi.com/markets/your-event/market-name
```

### 2. Run the Program
```bash
python3 main.py
```

**That's it!** 🎉

## 📋 What It Does

✅ **Paste any Kalshi URL** - works with production, demo, or direct tickers  
✅ **Automatically finds all markets** for that event  
✅ **Analyzes all prices** (bid, ask, last price)  
✅ **Shows clean comparison table** for easy analysis  
✅ **Perfect for comparing your predictions** against market sentiment  

## 📖 Detailed Instructions

See `HOW_TO_USE.md` for complete instructions and examples.

## 🛠️ Setup

For API credentials setup, see:
- `SETUP.md` - Complete setup guide
- `ENV_SETUP.md` - Environment variable configuration

## 📁 Files

- `main.py` - Main analyzer (clean and simple!)
- `HOW_TO_USE.md` - **Start here!** Simple usage guide
- `clients.py` - Kalshi API client implementations
- `requirements.txt` - Python dependencies
- `SETUP.md` - Detailed setup instructions
- `ENV_SETUP.md` - Environment variable setup guide

## 🔗 Supported URL Formats

```
KALSHI_URL=https://kalshi.com/markets/kxrttronares/tron-ares-rotten-tomatoes-score/kxrttronares
KALSHI_URL=https://kalshi.com/markets/kxrtconjuring/conjuring-rotten-tomatoes-score
KALSHI_URL=https://demo.kalshi.co/trade/KXRTCONJURING-60
KALSHI_URL=KXRTCONJURING-60
KALSHI_URL=KXRTRONARES
```

**Just paste any Kalshi URL and the program figures out the rest!** 🚀

## 📊 Example Output

```
🚀 Kalshi Market Analyzer
==================================================
🔗 Analyzing URL: https://kalshi.com/markets/kxrttronares/tron-ares-rotten-tomatoes-score/kxrttronares
🎯 Using event ticker: KXRTTRONARES
🌍 Environment: prod
✅ Loaded private key: KalshiProdAPI.pem
✅ Connected to prod environment

🔍 Finding all markets for event: KXRTTRONARES
✅ Found 7 markets for event KXRTTRONARES

📈 COMPARISON SUMMARY (7 markets):
Ticker              Yes Bid   Yes Ask   No Bid    No Ask    Last Price  
------------------------------------------------------------------------
KXRTTRONARES-80     8         13        87        92        13          
KXRTTRONARES-70     27        33        67        73        33          
KXRTTRONARES-65     35        44        56        65        44          
KXRTTRONARES-90     2         5         95        98        7           
KXRTTRONARES-75     17        22        78        83        22          
KXRTTRONARES-60     46        47        53        54        46          
KXRTTRONARES-45     78        81        19        22        81          

✅ Successfully analyzed 7 markets!
```

## 🔄 To Analyze Different Events

Just change the URL in your `.env` file and run again!

## 💡 Pro Tips

- **Works with any Kalshi URL** - production, demo, or direct tickers
- **Automatically detects environment** (demo vs production)
- **Finds all related markets** for comprehensive analysis
- **Clean, easy-to-read output** perfect for comparison
- **No complex setup** - just paste and run!