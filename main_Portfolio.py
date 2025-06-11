from Portfolio import Class_PortfolioData as PD
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3
import os
import osenv
import sys
import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt 
from email.mime.image import MIMEImage



def main():

    
    StocksData = {
        "BRK-B" :3,
        "BLK": 2,
        "KO":29,
        "XOM": 10,
        "FRT": 8,
        "VUSA.AS": 46,
        "IS0R.DE": 20,
        "ZPRG.DE": 42
    }


    # CreatePortfolioDB("Portfolio.db", StocksData)

    newPortfolio = PD.Portfolio(StocksData, "Portfolio.db")
    newPortfolio.SetupPortfolio()
    newPortfolio.FillSQL("PortfolioValue")
    newPortfolio.PortfoliValuefunc()
    newPortfolio.GetGrowthValue()
    htmlData = newPortfolio.HTMLData()
    

    stocklist = list(StocksData.keys())
    endDate = dt.datetime.now()
    startDate = endDate - dt.timedelta(days=300)

    meanReturns, covMatrix = get_data(stocklist, startDate, endDate)
    print(meanReturns)
    print(covMatrix)


    number_of_stocks = sum(StocksData.values())
    values = np.array(list(StocksData.values()))
    weights = values/number_of_stocks


    #Monte Carlo
    #Nember of Simulation
    mc_sims = 100
    T = 100 #timeFrame in days

    meanM = np.full(shape=(T, len(weights)), fill_value=meanReturns)
    meanM = meanM.T

    Portfolio_sims = np.full(shape=(T, mc_sims), fill_value=0.0)
    initialPortfolio = 15000 #ezt majd dinamikussá kell tenni, hogy azt az összeg legyen benne, ami ténylegesen a portfolio értéke.

    for m in range(0, mc_sims):
        Z = np.random.normal(size=(T, len(weights)))
        L = np.linalg.cholesky(covMatrix)
        dailyReturns = meanM + np.inner(L, Z)
        Portfolio_sims[:,m] = np.cumprod(np.inner(weights, dailyReturns.T)+1)*initialPortfolio


    plt.plot(Portfolio_sims)
    plt.ylabel("Portfolio Value ($)")
    plt.xlabel("Days")
    plt.title("MC Simulation of a Stock Portfolio")
    plt.savefig(f"Images/MCSim.jpg")
    

   
    SendEmail("Stock Growth", htmlData)

def get_data(stocks, start, end):
    stock_data = yf.download(stocks, start=start, end=end)['Close']
    if isinstance(stock_data, pd.Series):
        stock_data = stock_data.to_frame()

    returns = stock_data.pct_change()
    meanReturns = returns.mean()
    covMatrix = returns.cov()

    return meanReturns, covMatrix


def CreatePortfolioDB(filename: str, StockList: dict):

    conn = None
    try:
        conn = sqlite3.connect(filename)
        tableQueryDividend = CreateTable(StockList, "Dividend")
        tableQueryPortfolio = CreateTable(StockList, "PortfolioValue")
        cursorObj = conn.cursor()
        try:
            cursorObj.execute(tableQueryDividend)
        except sqlite3.Error as e:
            print(e)
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


    path = "Images/"
    pngfilepath = os.path.join(path, "MCSim.jpg")
    fp = open(pngfilepath, 'rb')
    img = MIMEImage(fp.read())
    img.add_header('Content-Disposition', f'attachment; filename=MonteCarloSimulations')
    fp.close()
    msg.attach(img)
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

