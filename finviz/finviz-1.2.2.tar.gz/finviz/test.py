import finviz

# aapl_data = finviz.get_stock('WMT')
# aapl_insider = finviz.get_insider('WMT')
aapl_news = finviz.get_news('WMT')
print(aapl_news)
