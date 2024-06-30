from .Class_StockData import StockData as SD
import pandas as pd



class Portfolio():
    
    def __init__(self, PortfolioData: dict) -> None:
        self.PortfolioData = PortfolioData
        self.PortfolioList: list = []
        self.PortfolioValue: float = 0
        self.diffDf: pd.DataFrame = None

    def SetupPortfolio(self):
        for i in self.PortfolioData:
            newStock = SD(i, self.PortfolioData[i])
            newStock.SetupStock()
            self.PortfolioList.append(newStock)

    def PortfoliValuefunc(self):
        for i in self.PortfolioList:
            self.PortfolioValue = self.PortfolioValue + (i.Darab*i.Price)

    def GetGrowthValue(self):
        DataToAdd = []
        for i in self.PortfolioList:
            diff = i.Price - i.prevClose
            diff = round(diff, 2)
            diffPercent = round((diff/i.Price)*100,2)
            DataToAdd.append([i.ticker, diffPercent, i.Price])
        self.diffDf = pd.DataFrame(DataToAdd, columns=["Ticker", "Different %", "Price"])

    def HTMLData(self) -> str:
        html = """
        <hr>
        <h2>Portfolio Data</h2>
        <table border="1" style="border-collapse: collapse;">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Growth</th>
                    <th>Price</th>
                    <th>Trend</th>
                </tr>
            </thead>
            <tbody>
        """
    
        for _, row in self.diffDf.iterrows():
            arrow = '↑' if row['Different %'] > 0 else '↓'
            color = 'green' if row['Different %'] > 0 else 'red'
        
            html += f"""
            <tr>
                <td>{row['Ticker']}</td>
                <td>{row['Different %']}</td>
                <td>{row['Price']}</td>
                <td style="color: {color};">{arrow}</td>
            </tr>
            """
    
        html += f"""
            </tbody>
        </table>
        <br>
        <p>Your current Portfolio Value: {self.PortfolioValue} $. </p>
        <hr>
        """
        return html





