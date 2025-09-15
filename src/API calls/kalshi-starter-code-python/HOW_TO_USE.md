# 🚀 Kalshi Market Analyzer - How to Use

## 📝 Super Simple Setup

### Step 1: Add Your Kalshi URL
Open your `.env` file and add this line:
```
KALSHI_URL=https://kalshi.com/markets/your-event/market-name
```

### Step 2: Run the Program
```bash
python3 main.py
```

That's it! 🎉

## 📋 Supported URL Formats

The program works with **any** Kalshi URL:

### ✅ Production URLs
```
KALSHI_URL=https://kalshi.com/markets/kxrttronares/tron-ares-rotten-tomatoes-score/kxrttronares
KALSHI_URL=https://kalshi.com/markets/kxrtconjuring/conjuring-rotten-tomatoes-score
```

### ✅ Demo URLs
```
KALSHI_URL=https://demo.kalshi.co/trade/KXRTCONJURING-60
KALSHI_URL=https://demo.kalshi.co/markets/some-event/market-name
```

### ✅ Direct Tickers
```
KALSHI_URL=KXRTCONJURING-60
KALSHI_URL=KXRTRONARES
```

## 🔍 What It Does

1. **Extracts the event ticker** from your URL
2. **Finds all markets** for that event
3. **Analyzes all prices** (bid, ask, last price)
4. **Shows comparison table** for easy analysis

## 📊 Example Output

```
🚀 Kalshi Market Analyzer
==================================================
🔗 Analyzing URL: https://kalshi.com/markets/kxrttronares/tron-ares-rotten-tomatoes-score/kxrttronares
🔗 Extracted event ticker 'KXRTTRONARES' from market ticker 'KXRTTRONARES'
🌍 Environment: prod
✅ Loaded private key: KalshiProdAPI.pem
✅ Connected to prod environment

🔍 Finding all markets for event: KXRTTRONARES
🔍 Fetching all markets for event: KXRTTRONARES
✅ Found 7 markets for event KXRTTRONARES
📋 Found 7 markets:
Market tickers: ['KXRTTRONARES-80', 'KXRTTRONARES-70', 'KXRTTRONARES-65', 'KXRTTRONARES-90', 'KXRTTRONARES-75', 'KXRTTRONARES-60', 'KXRTTRONARES-45']

🔍 Analyzing 7 markets...

--- Market 1/7 ---
📊 Tron: Ares Rotten Tomatoes score?
Ticker: KXRTTRONARES-80
Yes Bid: 8 cents
Yes Ask: 13 cents
No Bid: 87 cents
No Ask: 92 cents
Last Price: 13 cents

[... more markets ...]

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
📈 All market data is stored in 'all_market_data' for your analysis
```

## 🔄 To Analyze Different Events

Just change the URL in your `.env` file:
```
KALSHI_URL=https://kalshi.com/markets/new-event/market-name
```

Then run:
```bash
python3 main.py
```

## 💡 Pro Tips

- **Paste any Kalshi URL** - the program figures out the rest
- **Works with both demo and production** environments
- **Automatically finds all related markets** for comparison
- **Clean, easy-to-read output** for analysis
- **Perfect for comparing your predictions** against market sentiment

## 🛠️ Troubleshooting

### "KALSHI_URL not provided"
- Make sure you have `KALSHI_URL=your_url_here` in your `.env` file

### "API credentials not configured"
- Add your API keys to the `.env` file (see `ENV_SETUP.md`)

### "Private key file not found"
- Place your `.pem` file in this directory

### "No markets found"
- The event might not be active or the URL might be incorrect
- Try a different URL or check if the event is live
