import yfinance as yf
from .Class_StockData import StockData as SD
import pandas as pd



class Portfolio():
    
    def __init__(self, PortfolioData: dict) -> None:
        self.PortfolioData = PortfolioData
        self.PortfolioList = []
        self.PortfolioValue = 0
        self.diffDf = pd.DataFrame(columns=["Ticker", "Different %"])

    def SetupPortfolio(self):
        for i in self.PortfolioData:
            newStock = SD(i, self.PortfolioData[i])
            newStock.SetupStock()
            self.PortfolioList.append(newStock)

    def PortfoliValuefunc(self):
        for i in self.PortfolioList:
            self.PortfolioValue = self.PortfolioValue + (i.Darab*i.Price)

    def GetGrowthValue(self):
        for i in self.PortfolioList:
            diff = i.Price - i.prevClose
            diff = round(diff, 2)
            diffPercent = round((diff/i.Price)*100,2)
            print(i.ticker)
            print(diffPercent)

    def __str__(self) -> str:
        returnString = f"A Portfólió részvény értéke: {self.PortfolioValue}"

        return returnString





