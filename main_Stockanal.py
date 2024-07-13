from Portfolio import Class_StockData as CS
from Analize import Multiples as M


def main():
    None

    newStock = CS.StockData("XOM")
    newStock.SetupStock()
    M.MultipleAnal(newStock)



if __name__ == "__main__":
    main()