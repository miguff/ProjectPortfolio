from .Class_StockData import StockData as SD
import pandas as pd
import sqlite3
from datetime import datetime
import warnings



class Portfolio():
    
    def __init__(self, PortfolioData: dict, Database: str) -> None:
        self.PortfolioData = PortfolioData
        self.PortfolioList: list = []
        self.PortfolioValue: float = 0
        self.diffDf: pd.DataFrame = None
        self.Database = Database

    def FillDividendValue(self):
        sqlStringbegin = "INSERT INTO Dividend ( "
        sqlStringend =  " VALUES ("

        for key, value in self.PortfolioData.items():
            # Add column name to the SQL string
            sqlStringbegin += f"[{key}],"
            
            # Check the type of value to format it correctly for SQL
            if isinstance(value, str):  # Add single quotes for strings
                sqlStringend += f"'{value}',"
            elif value is None:  # Handle NULL values
                sqlStringend += "NULL,"
            else:  # Numeric values (int, float, etc.)
                sqlStringend += f"{value},"

        # Remove the trailing commas
        sqlStringbegin = sqlStringbegin.rstrip(",") + ")"
        sqlStringend = sqlStringend.rstrip(",") + ")"

        # Combine the parts
        sqlString = sqlStringbegin + sqlStringend

        # Print the final SQL string
        print(sqlString)
        try:
            self.SQLUpload(sqlString)
        except Exception as e:
            warnings.warn(f"I could not upload, There was an error, please check: {e}")

    def FillPortfolioValue(self, datatype: str, datedata: str = None, data: pd.DataFrame = None, ):
        sqlString = f"INSERT INTO PortfolioValue ([LogDate], "
        match datatype:
            case "EoM":
                for i in range(len(data)):
                    sqlString = sqlString + f"[{data.loc[i, 'Ticker']}],"
                sqlString = sqlString + f"[SUM])"
                sqlString = sqlString + f" VALUES ('{datedata}',"
                for i in range(len(data)):
                    sqlString = sqlString + f"{data.loc[i, 'Price']},"
                sqlString = sqlString + f"{round(data['Price'].sum(),2)})"
            case "Mid-month":
                for i in self.PortfolioList:
                    sqlString = sqlString + f"[{i.ticker}],"
                sqlString = sqlString + f"[SUM])"
                sqlString = sqlString + f" VALUES ('{datetime.now().strftime('%Y-%m-%d')}',"
                for i in self.PortfolioList:
                    sqlString = sqlString + f"{round(i.Darab*i.Price,2)},"
                
                if self.PortfolioValue != 0:
                    sqlString = sqlString + f"{round(self.PortfolioValue,2)})"
                else:
                    for i in self.PortfolioList:
                        self.PortfolioValue = self.PortfolioValue + (i.Darab*i.Price)
                    self.PortfolioValue = round(self.PortfolioValue,2)
                    sqlString = sqlString + f"{self.PortfolioValue})"
        print(sqlString)
        try:
            self.SQLUpload(sqlString)
        except Exception as e:
            warnings.warn(f"I could not upload, There was an error, please check: {e}")

    def SQLUpload(self, sqlString:str):
        conn = sqlite3.connect(self.Database)
        cursorObj = conn.cursor()
        cursorObj.execute(sqlString)
        conn.commit()
        conn.close()

    def SetupPortfolio(self):
        for i in self.PortfolioData:
            newStock = SD(i, self.PortfolioData[i])
            newStock.SetupStock()
            self.PortfolioList.append(newStock)

    def PortfoliValuefunc(self):
        if self.PortfolioValue == 0: 
            for i in self.PortfolioList:
                self.PortfolioValue = self.PortfolioValue + (i.Darab*i.Price)
        self.PortfolioValue = round(self.PortfolioValue,2)
        

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





