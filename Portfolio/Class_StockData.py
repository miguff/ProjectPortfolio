import yfinance as yf


class StockData():
    def __init__(self, ticker, darab) -> None:
        self.Darab = darab
        self.Price = None      
        self.prevClose = None 
        self.ticker = ticker
        #Some value
        self.EnterpriseValue = None
        self.BookValue = None

        #Some Rations
        self.QuickRation = None
        self.PriceToBook = None
        
        #Some Growth
        self.EarningsGrowth = None
        self.RevenueGrowth = None
        
        self.Stock = yf.Ticker(ticker)

    def SetupStock(self):
        self.GrowthData()
        self.Rations()
        self.Values()
        self.Prices()

    def GrowthData(self):
        try:
            self.RevenueGrowth =  self.Stock.info['revenueGrowth']
            self.EarningsGrowth = self.Stock.info['earningsGrowth']
        except KeyError:
            raise ValueError('Ticker not recognized')

    def Rations(self):
        try:
            self.QuickRation =  self.Stock.info['quickRatio']
            self.PriceToBook = self.Stock.info['priceToBook']
        except KeyError:
            raise ValueError('Ticker not recognized')
    
    def Values(self):
        try:
            self.EnterpriseValue =  self.Stock.info['enterpriseValue']
            self.BookValue = self.Stock.info['bookValue']
        except KeyError:
            raise ValueError('Ticker not recognized') 
        
    def Prices(self):
        try:
            self.Price = round(self.Stock.info['currentPrice'],2)
            self.prevClose = round(self.Stock.info['previousClose'],2)
        except KeyError:
            raise ValueError('Ticker not recognized')
