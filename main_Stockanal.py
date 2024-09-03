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

def main():

    SqlCursor, SQLConn = ConnectToSQL("Portfolio.db")

    StocksDf = pd.read_sql("SELECT * FROM PortfolioValue",SQLConn)
    StocksDf.set_index("LogDate", inplace=True)


    #It will be used to Analize certain Stocks
    StockTickers = StocksDf.columns.to_list()

    MakePortfolioPlots(StocksDf, StockTickers)
    SendEmail("Portfolió Value")

     

    # newStock = CS.StockData("XOM")
    # newStock.SetupStock()
    # M.MultipleAnal(newStock)

def MakePortfolioPlots(Df: pd.DataFrame, ListOfData: list):
    
    for i in ListOfData:
        ax = sns.barplot(Df, x=Df.index, y=i)
        ax.bar_label(ax.containers[0], fontsize=10)
        plt.title(f"Value of {i} ($) ")
        fig = ax.get_figure()
        fig.savefig(f"Images/{i}.jpg")
        plt.close()
    

    palette_color = sns.color_palette("crest") 
    DfWOSum = Df.drop("SUM", axis=1)
    PriceValues = DfWOSum.values[-1].tolist()
    ListOfData.remove("SUM")
    plt.pie(PriceValues, labels=ListOfData,colors=palette_color, autopct='%.0f%%')
    plt.title("Pie Chart of Portfolio Percent")
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