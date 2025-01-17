from Portfolio import Class_StockData as CS
from Analize import Multiples as M
import sqlite3
import pandas  as pd
import seaborn as sns
import matplotlib.pyplot as plt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from email.mime.image import MIMEImage
import osenv
import smtplib, glob
import base64
import sys

def main():

    dividendchoser = 1
    
    match dividendchoser:
        case 0:
            Table = 'PortfolioValue'
            Subject = "Portfolio Value"
            func = Portfoliofunc
        case 1:
            Table = "Dividend"
            Subject = "Dividend Value"
            func = dividendfunc
        case _:
            print("Wrong input number")
            sys.exit()
    

    SqlCursor, SQLConn = ConnectToSQL("Portfolio.db")
    StocksDf = pd.read_sql(f"SELECT * FROM {Table} Order by LogDate asc",SQLConn)
    StocksDf.set_index("LogDate", inplace=True)
    StocksDf = StocksDf.loc[:, ~StocksDf.iloc[-1].isna()]

    func(StocksDf)
    #SendEmail(Subject)
     
def dividendfunc(Stocks: pd.DataFrame):
    MonthlydivDF = Stocks[["All Dividend", "Tax", "Ticker"]]
    MonthlydivDF.index = pd.to_datetime(MonthlydivDF.index)
    MonthlySummary = MonthlydivDF.resample('M').sum()
    print(MonthlySummary)


    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(MonthlySummary.index, MonthlySummary['All Dividend'], label="All Dividend", marker='o')
    plt.plot(MonthlySummary.index, MonthlySummary['Tax'], label="Tax", marker='o')

    # Add labels, legend, and title
    plt.title("Monthly Totals of All Dividend and Tax", fontsize=16)
    plt.xlabel("Log Date", fontsize=12)
    plt.ylabel("Amount", fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.legend(title="Category", fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Show plot
    plt.tight_layout()
    plt.show()
    


def Portfoliofunc(StocksDf :pd.DataFrame):
    StockTickers = StocksDf.columns.to_list()
    MakePortfolioPlots(StocksDf, StockTickers)



def MakePortfolioPlots(Df: pd.DataFrame, ListOfData: list):
    
    for i in ListOfData:
        ax = sns.barplot(Df, x=Df.index, y=i)
        ax.bar_label(ax.containers[0], fontsize=10)
        plt.title(f"Value of {i} ($) ")
        fig = ax.get_figure()
        plt.show()
        fig.savefig(f"Images/{i.replace('.', '_')}.jpg")
        plt.close()
    

    palette_color = sns.color_palette("crest") 
    DfWOSum = Df.drop("SUM", axis=1)
    PriceValues = DfWOSum.values[-1].tolist()
    ListOfData.remove("SUM")
    plt.pie(PriceValues, labels=ListOfData,colors=palette_color, autopct='%.0f%%')
    plt.title("Pie Chart of Portfolio Percent")
    #plt.show()
    plt.savefig(f"Images/PieChart.jpg")
    plt.close()



def SendEmail(Subject: str):
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
    pngfiles = glob.glob( os.path.join(path, "*.jpg") )
    for file in pngfiles:
        tickerFile = file.title()[7:-4]
        # Open the files in binary mode.  Let the MIMEImage class automatically
        # guess the specific image type.
        fp = open(file, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        img.add_header('Content-Disposition', f'attachment; filename={tickerFile.upper()}')
        msg.attach(img)


    # Send the message via SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()
    print("Email sent Successfully!")

def ConnectToSQL(filename: str):
    try:
        conn = sqlite3.connect(filename)
        return conn.cursor(), conn
    except sqlite3.Error as e:
            print(e)
if __name__ == "__main__":
    main()