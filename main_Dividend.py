from Portfolio import Class_PortfolioData as PD
from DownloadData import DataGather as Data
from DownloadData import isin_to_ticker
from DownloadData import EmailDownload 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3
import os
import osenv
import sys



def main():
    EmailDownloader = EmailDownload("subject:\"Tranzakció értesítő\"", "Dividend", False)
    DownloadedPath = EmailDownloader.fileDownloader()
    DividendDatas = os.listdir(DownloadedPath)
    NotProcessedFiles = []
    for elem in DividendDatas:
        if "Done" not in elem:
            NotProcessedFiles.append(elem)

    for element in NotProcessedFiles:
        gathering = Data(DownloadedPath, f"Done - {element}", element)
        gathering.DePassword()
        dataDf = gathering.DividendExtract()
        if type(dataDf) == int:
            os.remove(os.path.join(DownloadedPath, element))
            continue
        dataDf['Ticker'] = dataDf["ISIN"].apply(isin_to_ticker)
        dataDf['Index'] = dataDf["LogDate"] + dataDf["Ticker"]
        print(dataDf)
        StocksData = dataDf.to_dict('records')
        for data in StocksData:
            newPortfolio = PD.Portfolio(data, "Portfolio.db")
            newPortfolio.FillDividendValue()
        




if __name__ == "__main__":
    main()
