# Kalshi URL Examples

## How to Use URLs with Your Code

Now you can simply paste any Kalshi market URL into the `MARKET_URL` variable and the program will automatically extract the market ticker and analyze it!

### Example 1: Trade Page URL
```python
MARKET_URL = "https://demo.kalshi.co/trade/KXQUICKSETTLE-25SEP01H1500-3"
```
**Extracts:** `KXQUICKSETTLE-25SEP01H1500-3`

### Example 2: Markets Page URL
```python
MARKET_URL = "https://demo.kalshi.co/markets/KXDOGED-25SEP0113-T0.2149999"
```
**Extracts:** `KXDOGED-25SEP0113-T0.2149999`

### Example 3: Any Kalshi URL
```python
MARKET_URL = "https://demo.kalshi.co/some/path/KXTICKER-123"
```
**Extracts:** `KXTICKER-123`

### Example 4: Direct Ticker (still works!)
```python
MARKET_URL = "KXQUICKSETTLE-25SEP01H1500-3"
```
**Extracts:** `KXQUICKSETTLE-25SEP01H1500-3` (no change)

## How to Use

1. **Find a market you want to analyze on Kalshi**
2. **Copy the URL from your browser**
3. **Paste it into the `MARKET_URL` variable in `main.py`**
4. **Run the program**

That's it! The program will automatically:
- Extract the market ticker from the URL
- Fetch the market data
- Extract all the prices
- Organize them into clean data structures

## Supported URL Formats

- ✅ `https://demo.kalshi.co/trade/KXTICKER-123`
- ✅ `https://demo.kalshi.co/markets/KXTICKER-123`
- ✅ `https://kalshi.com/trade/KXTICKER-123`
- ✅ `KXTICKER-123` (direct ticker)
- ✅ Any URL ending with a market ticker

## Quick Test

Try changing the URL in `main.py` to any of these examples and run the program to see it in action!

