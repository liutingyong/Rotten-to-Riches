# Kalshi API Setup Guide

## Prerequisites
- A Kalshi account at [https://kalshi.com](https://kalshi.com)
- Python 3.7+ installed
- Virtual environment activated

## Step 1: Get Your API Credentials

1. Go to [https://kalshi.com](https://kalshi.com) and log in
2. Navigate to your account settings
3. Go to the API section
4. Generate a new API key pair
5. Download your private key file (`.pem` format)
6. Note your API Key ID

## Step 2: Configure Your Credentials

You have two options:

### Option A: Environment Variables (Recommended)
Create a `.env` file in this directory with:

```bash
# Demo Environment (for testing)
DEMO_KEYID=your_actual_demo_key_id
DEMO_KEYFILE=KalshiDemoAPI.pem

# Production Environment (for live trading)
PROD_KEYID=your_actual_production_key_id
PROD_KEYFILE=KalshiProductionAPI.pem
```

### Option B: Direct Configuration
Edit `main.py` and replace the placeholder values:

```python
# Change these lines in main.py
KEYID = "your_actual_demo_key_id"
KEYFILE = "KalshiDemoAPI.pem"
```

## Step 3: Place Your Private Key File

1. Rename your downloaded private key file to `KalshiDemoAPI.pem`
2. Place it in this directory (same folder as `main.py`)
3. Make sure the file has the correct permissions

## Step 4: Test Your Setup

Run the application:

```bash
python main.py
```

## Troubleshooting

### "Private key file not found" Error
- Make sure `KalshiDemoAPI.pem` is in the same directory as `main.py`
- Check that the filename matches exactly (case-sensitive)
- Verify file permissions

### "API credentials not configured" Error
- Create a `.env` file with your credentials
- Or edit `main.py` directly to set KEYID and KEYFILE
- Make sure you're not using placeholder values

### "Failed to load private key" Error
- Verify your private key file is valid and not corrupted
- Make sure it's in the correct PEM format
- Check if your key requires a password

### "Failed to get balance" Error
- Verify your API credentials are correct
- Check your internet connection
- Ensure your API key has the necessary permissions

## Security Notes

⚠️ **IMPORTANT**: Never commit your private key files or `.env` files to version control!
- Add `*.pem` and `.env` to your `.gitignore` file
- Keep your private keys secure and don't share them
- Use demo environment for testing, production only for live trading

## Support

If you continue to have issues:
1. Check the Kalshi API documentation
2. Verify your API key permissions
3. Contact Kalshi support if needed
