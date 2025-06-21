import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def StockRiports_main():
    Table = "PortfolioValue"

    SqlCursor, SQLConn = ConnectToSQL("Portfolio.db")
    SumValueRiport(SQLConn, Table)
    StockRatio(SQLConn, Table)



def SumValueRiport(SQLConn, Table):
    StocksDf = pd.read_sql(f"SELECT LogDate, SUM FROM {Table}  Order by LogDate asc",SQLConn)
    ax = sns.barplot(StocksDf, x=StocksDf["LogDate"], y=StocksDf["SUM"])
    ax.bar_label(ax.containers[0], fontsize=10)
    plt.title("Value of SUM ($) ")
    fig = ax.get_figure()
    plt.savefig("Images/SumBar.jpg")
    plt.close()


def StockRatio(SQLConn, Table):
    StocksDf = pd.read_sql(f"SELECT * FROM {Table}  Order by LogDate desc LIMIT 1",SQLConn)
    StocksDf.dropna(axis=1, inplace=True)
    StocksDf.drop("SUM", axis=1, inplace=True)
    StocksDf.set_index("LogDate", inplace=True)
    
    #Setup the values for graphs
    data = StocksDf.to_numpy()[0]
    labels = StocksDf.columns
    colors = sns.color_palette("crest")

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        data,
        labels=labels,
        colors=colors,
        startangle=90,
        autopct='%.0f%%',
        wedgeprops=dict(width=0.5)
        )
    plt.title("Pie Chart of Portfolio Percent")
    ax.legend(wedges, labels, title="Classes", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.savefig("Images/PieChart.jpg")
    plt.close()

def ConnectToSQL(filename: str):
    try:
        conn = sqlite3.connect(filename)
        return conn.cursor(), conn
    except sqlite3.Error as e:
            print(e)



StockRiports_main()