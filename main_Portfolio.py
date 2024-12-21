from Portfolio import Class_PortfolioData as PD
from DownloadData import DataGather as Data
from DownloadData import isin_to_ticker
from DownloadData import EmailDownload 
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3
import os
import osenv
import sys



def main():
    date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    current_date = datetime.now()
    previous_month_date = current_date.replace(day=1) - timedelta(days=1)
    previous_Year = previous_month_date.strftime("%Y")

    typeofdata = "Mid-month"


    EmailDownloader = EmailDownload("subject:\"Havi értesítő\"", "Portfolio")
    DownloadedPath = EmailDownloader.fileDownloader()
    print(DownloadedPath)

    if typeofdata == "EoM":
        gathering = Data(DownloadedPath, f"Done - {previous_Year} - Havi_ertesito.pdf")
        gathering.inputfile()
    elif typeofdata == "Mid-month":
        gathering = Data(DownloadedPath, f"Done - {previous_Year} - Havi_ertesito.pdf", f"Done - {previous_Year} - Havi_ertesito.pdf")
    
    gathering.DePassword()
    dataDf = gathering.MonthlyExtract()
    dataDf['Ticker'] = dataDf["ISIN"].apply(isin_to_ticker)
    dataDf.reset_index(drop=True, inplace=True)
    StocksData = dict(zip(dataDf["Ticker"], dataDf["Piece"]))
    print(dataDf)

    CreatePortfolioDB("Portfolio.db", StocksData)

    newPortfolio = PD.Portfolio(StocksData, "Portfolio.db")
    newPortfolio.SetupPortfolio()
    
    newPortfolio.FillPortfolioValue(typeofdata, date, dataDf)
    # newPortfolio.PortfoliValuefunc()
    # newPortfolio.GetGrowthValue()
    # htmlData = newPortfolio.HTMLData()

   
    # SendEmail("Stock Growth", htmlData)


def CreatePortfolioDB(filename: str, StockList: dict):

    conn = None
    try:
        conn = sqlite3.connect(filename)
        tableQueryPortfolio = CreateTable(StockList, "PortfolioValue")
        cursorObj = conn.cursor()
        # try:
        #     cursorObj.execute(tableQueryDividend)
        # except sqlite3.Error as e:
        #     print(e)
        try:
            cursorObj.execute(tableQueryPortfolio)
        except sqlite3.Error as e:
            print(e)
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def CreateTable(StockList: dict, tableName: str):
    table = f"CREATE TABLE {tableName} ([LogDate] TEXT NOT NULL PRIMARY KEY, "
    
    for i in StockList.keys():
        table = table + f"[{i}] FLOAT,"
    table = table + "[SUM] FLOAT);"
    return table


def SendEmail(Subject: str, htmlData: str):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = os.environ['GMAIL_USERNAME']
    smtp_password = os.environ['GMAIL_PASSWORD'] 
    from_email = os.environ['GMAIL_USERNAME']
    to_email = os.environ['TO_USERNAME']
    subject = Subject

    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    part = MIMEText(htmlData, 'html')

    # Attach parts into message container
    msg.attach(part)

    # Send the message via SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()
    print("Email sent Successfully!")


if __name__ == "__main__":
    main()

