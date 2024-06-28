from Portfolio import Class_PortfolioData as PD

StocksData = {
    "AAPL":3,
    "BRK-B" :3,
    "BLK": 2,
    "KO":24,
    "XOM": 10,
    "FRT": 8,
    "NNN": 23,
    "PG": 3,
    "O": 15
}

newPortfolio = PD.Portfolio(StocksData)
newPortfolio.SetupPortfolio()
newPortfolio.PortfoliValuefunc()
newPortfolio.GetGrowthValue()
print(newPortfolio)