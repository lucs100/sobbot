import yfinance as yf

gme = yf.Ticker("GME")

print(gme.info["regularMarketPrice"])
print("\n\n\n")
print(gme.history(period="1d"))