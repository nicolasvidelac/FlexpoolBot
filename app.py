from datetime import datetime
import schedule
import requests
import sqlite3
import time

connection = sqlite3.connect('flexpool.db')
cursor = connection.cursor();

cursor.execute('''CREATE TABLE IF NOT EXISTS PROFIT
    (
        FECHA DATETIME PRIMARY KEY,
        GANANCIA REAL NOT NULL
    )
  ;''')

cursor.execute('''CREATE TABLE IF NOT EXISTS BALANCE
    (
        FECHA DATETIME PRIMARY KEY,
        TOTAL REAL NOT NULL
    )
  ;''')


def profitCalculator():
    url = 'https://flexpool.io/api/v1/miner/0x4ceAa7a6148a4a31512B8DA18376987AD2ECc4A3/balance'
    response = requests.get(url)

    todaysBalance = gweiToEth(response.json()['result'])

    cursor.execute("SELECT * FROM BALANCE")
    yesterdaysBalance = 0

    try:
        yesterdaysBalance = cursor.fetchall()[-1][1];
    except :
        pass
 
    todaysProfit = todaysBalance - yesterdaysBalance

    cursor.execute("INSERT INTO PROFIT VALUES (?,?)", [datetime.today(), todaysProfit])
    cursor.execute("INSERT INTO BALANCE VALUES (?,?)", [datetime.today(), todaysBalance])
    connection.commit()
    print("ganancias de hoy: " + str(todaysProfit))
    print("ganancias totales: " + str(todaysBalance))

def expectedEarnings():
    url = 'https://flexpool.io/api/v1/miner/0x4ceAa7a6148a4a31512B8DA18376987AD2ECc4A3/estimatedDailyRevenue'
    response = requests.get(url)

    print("ganancias esperadas: " + str(gweiToEth(response.json()['result'])))




def gweiToEth(gwei):
    return gwei / 1000000000000000000

schedule.every().day.at("09:00").do(profitCalculator)
schedule.every(1).hour.do(expectedEarnings)

while True:
    schedule.run_pending()
    time.sleep(59)