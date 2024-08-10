from Portfolio import Class_PortfolioData as PD
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3
import os
import osenv
import sys


def main():

    
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


    CreatePortfolioDB("Portfolio.db", StocksData)

    newPortfolio = PD.Portfolio(StocksData, "Portfolio.db")
    newPortfolio.SetupPortfolio()
    newPortfolio.FillSQL("PortfolioValue")
    newPortfolio.PortfoliValuefunc()
    newPortfolio.GetGrowthValue()
    htmlData = newPortfolio.HTMLData()
    
    print(newPortfolio.PortfolioValue)
    
   
    SendEmail("Stock Growth", htmlData)


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

