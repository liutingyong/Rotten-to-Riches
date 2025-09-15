# Environment Configuration (.env) Setup

## ⚠️ SECURITY WARNING
**Never commit API keys or private keys to version control!** This guide shows you how to set up your credentials securely.

## Step 1: Create Your .env File

Create a file named `.env` in this directory with the following content:

```bash
# Demo Environment (for testing)
DEMO_KEYID=your_actual_demo_key_id_here
DEMO_KEYFILE=KalshiDemoAPI.pem

# Production Environment (for live trading)
PROD_KEYID=your_actual_production_key_id_here
PROD_KEYFILE=KalshiProductionAPI.pem

# Market Selection (optional)
MARKET_URL=https://demo.kalshi.co/trade/KXQUICKSETTLE-25SEP01H1500-3
```

## Step 2: Get Your API Credentials

### For Demo Environment:
1. Go to [demo.kalshi.co](https://demo.kalshi.co)
2. Create an account and log in
3. Go to API settings
4. Generate API credentials
5. Download your private key file

### For Production Environment:
1. Go to [kalshi.com](https://kalshi.com)
2. Create an account and log in
3. Go to API settings
4. Generate API credentials
5. Download your private key file

## Step 3: Update Your .env File

Replace the placeholder values with your actual credentials:

```bash
# Example with real credentials (DO NOT use these - they're just examples)
DEMO_KEYID=KXDEMO123456789
DEMO_KEYFILE=KalshiDemoAPI.pem
PROD_KEYID=KXPROD987654321
PROD_KEYFILE=KalshiProductionAPI.pem
MARKET_URL=https://demo.kalshi.co/trade/KXQUICKSETTLE-25SEP01H1500-3
```

## Step 4: Place Your Private Key Files

1. Rename your downloaded private key files:
   - Demo: `KalshiDemoAPI.pem`
   - Production: `KalshiProductionAPI.pem`
2. Place them in this directory (same folder as `main.py`)

## Step 5: Verify Your Setup

Run the program to test your configuration:

```bash
python3 main.py
```

## Security Best Practices

✅ **DO:**
- Keep your `.env` file private
- Add `.env` to your `.gitignore` file
- Use different credentials for demo and production
- Regularly rotate your API keys

❌ **DON'T:**
- Commit `.env` files to version control
- Share your private keys
- Use production credentials for testing
- Hardcode credentials in your code

## File Structure

Your directory should look like this:
```
kalshi-starter-code-python/
├── main.py
├── clients.py
├── .env                    # ← Your credentials (private)
├── KalshiDemoAPI.pem       # ← Your demo private key (private)
├── KalshiProductionAPI.pem # ← Your production private key (private)
├── .gitignore              # ← Should include .env and *.pem
└── README.md
```

## Troubleshooting

### "API credentials not configured"
- Make sure your `.env` file exists
- Check that your API key IDs are correct
- Verify your private key files are in the right location

### "Private key file not found"
- Ensure your private key files are named correctly
- Check file permissions
- Verify the files are in the same directory as `main.py`

### "Invalid market ticker"
- Make sure you're using the right environment (demo vs production)
- Check that your URL is correct
- Verify your API credentials match the environment

