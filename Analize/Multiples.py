from Portfolio import Class_StockData as CS

class MultipleAnal():
    def __init__(self, Stock: CS.StockData):
        self.Stock = Stock
        print(Stock.IncomeStatement.index)