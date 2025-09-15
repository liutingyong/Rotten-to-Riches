import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from clients import KalshiHttpClient, Environment

def extract_ticker_from_url(url_or_ticker):
    """
    Extract market ticker from Kalshi URL or return the ticker if already provided.
    """
    # If it's already a ticker (contains no URL parts), return as-is
    if not any(domain in url_or_ticker.lower() for domain in ['kalshi.co', 'kalshi.com', 'http', 'www']):
        return url_or_ticker
    
    # Extract ticker from URL
    if 'kalshi.co' in url_or_ticker or 'kalshi.com' in url_or_ticker:
        if '/trade/' in url_or_ticker:
            # Format: https://demo.kalshi.co/trade/KXTICKER-123
            ticker = url_or_ticker.split('/trade/')[-1]
        elif '/markets/' in url_or_ticker:
            path_part = url_or_ticker.split('/markets/')[-1]
            if '/' in path_part:
                # Split by '/' and take the last part
                parts = path_part.split('/')
                ticker = parts[-1]  # Last part should be the full ticker
                ticker = ticker.upper()  # Convert to uppercase
            else:
                ticker = path_part.upper()
        elif '/event/' in url_or_ticker:
            ticker = url_or_ticker.split('/event/')[-1].upper()
        else:
            ticker = url_or_ticker.rstrip('/').split('/')[-1].upper()
        
        # Clean up any query parameters or fragments
        ticker = ticker.split('?')[0].split('#')[0]
        return ticker
    
    return url_or_ticker

def detect_environment_from_url(url):
    """
    Detect if URL is for demo or production environment
    """
    if 'demo.kalshi.co' in url:
        return Environment.DEMO
    elif 'kalshi.com' in url:
        return Environment.PROD
    else:
        return Environment.DEMO

def analyze_single_market(client, ticker):
    """
    Analyze a single market and return price data
    """
    try:
        market_data = client.get_market(ticker)
        
        # Extract the actual market data from the response
        if 'market' in market_data:
            market_info = market_data['market']
        else:
            market_info = market_data
        
        # Extract key price information
        market_prices = {
            'ticker': market_info.get('ticker'),
            'title': market_info.get('title'),
            'yes_bid': market_info.get('yes_bid') or 'N/A',
            'yes_ask': market_info.get('yes_ask') or 'N/A',
            'no_bid': market_info.get('no_bid') or 'N/A',
            'no_ask': market_info.get('no_ask') or 'N/A',
            'last_price': market_info.get('last_price') or 'N/A',
            'status': market_info.get('status'),
            'volume': market_info.get('volume'),
            'open_interest': market_info.get('open_interest')
        }
        
        # Print simplified price summary
        print(f"\n📊 {market_prices['title']}")
        print(f"Ticker: {market_prices['ticker']}")
        print(f"Yes Bid: {market_prices['yes_bid']} cents")
        print(f"Yes Ask: {market_prices['yes_ask']} cents")
        print(f"No Bid: {market_prices['no_bid']} cents")
        print(f"No Ask: {market_prices['no_ask']} cents")
        print(f"Last Price: {market_prices['last_price']} cents")
        
        return market_prices
        
    except Exception as e:
        print(f"ERROR: Failed to get market data for {ticker}: {str(e)}")
        return None

def get_event_markets(client, event_ticker):
    """
    Get all markets for a specific event
    """
    try:
        print(f"🔍 Fetching all markets for event: {event_ticker}")
        markets_response = client.get_markets(event_ticker=event_ticker)
        
        if 'markets' in markets_response:
            markets = markets_response['markets']
            print(f"Found {len(markets)} markets for event {event_ticker}")
            
            # Extract tickers from the markets
            market_tickers = []
            for market in markets:
                ticker = market.get('ticker')
                if ticker:
                    market_tickers.append(ticker)
            
            return market_tickers
        else:
            print(f"No markets found for event {event_ticker}")
            return []
            
    except Exception as e:
        print(f"ERROR: Failed to get markets for event {event_ticker}: {str(e)}")
        return []

def analyze_multiple_markets(client, market_tickers):
    """
    Analyze multiple markets and return comparison data
    """
    all_market_data = {}
    
    print(f"\n🔍 Analyzing {len(market_tickers)} markets...")
    
    for i, ticker in enumerate(market_tickers, 1):
        print(f"\n--- Market {i}/{len(market_tickers)} ---")
        market_data = analyze_single_market(client, ticker)
        if market_data:
            all_market_data[ticker] = market_data
    
    # Print comparison summary
    if all_market_data:
        print(f"\n📈 COMPARISON SUMMARY ({len(all_market_data)} markets):")
        print("Ticker".ljust(20) + "Yes Bid".ljust(10) + "Yes Ask".ljust(10) + "No Bid".ljust(10) + "No Ask".ljust(10) + "Last Price".ljust(12))
        print("-" * 72)
        
        for ticker, data in all_market_data.items():
            print(f"{ticker[:18].ljust(20)}{str(data['yes_bid']).ljust(10)}{str(data['yes_ask']).ljust(10)}{str(data['no_bid']).ljust(10)}{str(data['no_ask']).ljust(10)}{str(data['last_price']).ljust(12)}")
    
    return all_market_data

def main():
    """
    Main function to analyze Kalshi markets
    """
    print("🚀 Kalshi Market Analyzer")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # ========================================
    # 📝 STEP 1: PASTE YOUR KALSHI URL HERE
    # ========================================
    KALSHI_URL = os.getenv('KALSHI_URL')
    
    if not KALSHI_URL:
        print("ERROR: KALSHI_URL not provided!")
        exit(1)
    
    print(f"🔗 Analyzing URL: {KALSHI_URL}")
    
    # ========================================
    # 🔍 STEP 2: EXTRACT EVENT TICKER
    # ========================================
    extracted_ticker = extract_ticker_from_url(KALSHI_URL)
    
    # Check if it's a market ticker or event ticker
    if '-' in extracted_ticker and any(char.isdigit() for char in extracted_ticker):
        # It's a market ticker like KXRTCONJURING-60, extract event part
        EVENT_TICKER = extracted_ticker.split('-')[0]
        print(f"🔗 Extracted event ticker '{EVENT_TICKER}' from market ticker '{extracted_ticker}'")
    else:
        # It's already an event ticker
        EVENT_TICKER = extracted_ticker
        print(f"🎯 Using event ticker: {EVENT_TICKER}")
    
    # ========================================
    # 🌍 STEP 3: DETECT ENVIRONMENT
    # ========================================
    env = detect_environment_from_url(KALSHI_URL)
    print(f"🌍 Environment: {env.value}")
    
    # ========================================
    # 🔑 STEP 4: LOAD CREDENTIALS
    # ========================================
    if env == Environment.DEMO:
        KEYID = os.getenv('DEMO_KEYID')
        KEYFILE = os.getenv('DEMO_KEYFILE') or "KalshiDemoAPI.pem"
    else:
        KEYID = os.getenv('PROD_KEYID')
        KEYFILE = os.getenv('PROD_KEYFILE') or "KalshiProductionAPI.pem"
    
    if not KEYID:
        print("ERROR: API credentials not configured, put key id and pem in .env file.")
        
        exit(1)
    
    # Check if private key file exists
    if not os.path.exists(KEYFILE):
        print(f"ERROR: Private key file not found: {KEYFILE}")
        print(f"Please place your private key file '{KEYFILE}' in this directory")
        exit(1)
    
    # Load private key
    try:
        with open(KEYFILE, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )
        print(f"Loaded private key: {KEYFILE}")
    except Exception as e:
        print(f"ERROR: Failed to load private key: {str(e)}")
        exit(1)
    
    # ========================================
    # 🔌 STEP 5: INITIALIZE CLIENT
    # ========================================
    try:
        client = KalshiHttpClient(
            key_id=KEYID,
            private_key=private_key,
            environment=env
        )
        print(f"Connected to {env.value} environment")
    except Exception as e:
        print(f"ERROR: Failed to connect: {str(e)}")
        exit(1)
    
    # ========================================
    # 📊 STEP 6: ANALYZE MARKETS
    # ========================================
    print(f"\n🔍 Finding all markets for event: {EVENT_TICKER}")
    MARKET_TICKERS = get_event_markets(client, EVENT_TICKER)
    
    if MARKET_TICKERS:
        print(f"📋 Found {len(MARKET_TICKERS)} markets:")
        print("Market tickers:", MARKET_TICKERS)
        
        # Analyze all markets
        all_market_data = analyze_multiple_markets(client, MARKET_TICKERS)
        
        print(f"\nSuccessfully analyzed {len(all_market_data)} markets!")
        print("📈 All market data is stored in 'all_market_data' for your analysis")
        
    else:
        print(f"No markets found for event {EVENT_TICKER}")
        print("The event might not be active or the URL might be incorrect")
        exit(1)

if __name__ == "__main__":
    main()