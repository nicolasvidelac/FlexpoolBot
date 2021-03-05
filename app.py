from datetime import datetime
import schedule
import requests
import sqlite3
import math
import keyboard
import os
import time
from colorama import Fore, Style, init

connection = sqlite3.connect('flexpool.db')
cursor = connection.cursor();
init(convert=True)

apiKey = str(os.environ.get('ETHERSCAN_APIKEY'))
wallet = str(os.environ.get('ETH_WALLET'))

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

def profitCalculator(save = True):
    url = 'https://flexpool.io/api/v1/miner/%s/balance'%wallet
    response = requests.get(url)

    todaysBalance = gweiToEth(response.json()['result'])

    cursor.execute("SELECT * FROM BALANCE")
    yesterdaysBalance = 0

    try:
        yesterdaysBalance = cursor.fetchall()[-1][1];
    except :
        pass
 
    todaysProfit = todaysBalance - yesterdaysBalance

    if save == True:
        cursor.execute("INSERT INTO PROFIT VALUES (?,?)", [datetime.today(), todaysProfit])
        cursor.execute("INSERT INTO BALANCE VALUES (?,?)", [datetime.today(), todaysBalance])
        connection.commit()

    ethPrice = getEthPrice()

    print(
        "ganancias de hoy: ", str(truncate(todaysProfit,6)), "eth / $", truncate(todaysProfit * ethPrice,3), "usd",
        "\nganancias totales:", str(truncate(todaysBalance,6)), "eth / $", truncate(todaysBalance * ethPrice,3), "usd",
        "\nprecio de eth: $", ethPrice, "usd"
    )

    return;

def expectedEarnings():
    url = 'https://flexpool.io/api/v1/miner/%s/estimatedDailyRevenue'%wallet
    response = requests.get(url)
    earnings = gweiToEth( response.json()['result'])
    
    print("ganancias esperadas:",str(earnings), "eth /", truncate(earnings * getEthPrice(),3), "usd")
    return;

def dailyReport():
    url = 'https://flexpool.io/api/v1/miner/%s/daily'%wallet
    response = (requests.get(url)).json()['result']

    validShares = int(response['valid_shares'])
    staleShares = int(response['stale_shares'])
    invalidShares = int(response['invalid_shares'])
    totalShares = validShares + staleShares + invalidShares

    print(
        "hashrate reportado:", str(hashToMegaHash(response['reported_hashrate'])) , 'MH/s',
        "\nhashrate efectivo: " , str(hashToMegaHash(response['effective_hashrate'])), 'MH/s',
        "\n\nshares validas:    "    , str(validShares), "/"  , truncate(validShares/totalShares * 100,2) , "%"
        "\nshares caducadas:  "  , str(staleShares), "/"  , truncate(staleShares/totalShares * 100,2) , "%"
        "\nshares invalidas:  "  , str(invalidShares), "/", truncate(invalidShares/totalShares * 100,2) , "%"
    )

def getHistory():
    cursor.execute("SELECT * FROM PROFIT")
    profit = cursor.fetchall()

    cursor.execute("SELECT TOTAL FROM BALANCE")
    balance = cursor.fetchall()[-1][0]

    ethPrice = getEthPrice()

    print("ganancias totales:", str(truncate(balance,6)), "eth / $", truncate(balance * ethPrice,3), "usd\n")
    
    for item in reversed(profit):
        print("generado:", truncate(item[1],4), "fecha:", item[0][5:10])
        
def getEthPrice():
    url = 'https://api.etherscan.io/api?module=stats&action=ethprice&apikey=%s'%apiKey
    response = requests.get(url).json()['result']
    return float(response['ethusd']) 

def hashToMegaHash(hashrate):
    return truncate(hashrate / 1000000, 1)

def gweiToEth(gwei):
    return  truncate(gwei / 1000000000000000000, 6)  
  
def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

schedule.every().day.at("09:00").do(profitCalculator)

while True:
    if keyboard.is_pressed('2'):
        print(f"\n{Fore.LIGHTYELLOW_EX}Expected earnings:")
        expectedEarnings()

    elif keyboard.is_pressed('3'):
        print(f"\n{Fore.LIGHTCYAN_EX}Daily report:")
        dailyReport()

    elif keyboard.is_pressed('1'):
        print(f"\n{Fore.LIGHTGREEN_EX}Current profits:")
        profitCalculator(False)

    elif keyboard.is_pressed('h'):
        print(
            f"\n{Fore.LIGHTGREEN_EX}Press 1 for current profits",
            f"\n{Fore.LIGHTYELLOW_EX}Press 2 for expected earnings",
            f"\n{Fore.LIGHTCYAN_EX}Press 3 for daily profits",
            f"\n{Fore.LIGHTMAGENTA_EX}Press 4 for profits history",
        )

    elif keyboard.is_pressed('4'):
        print(f"\n{Fore.LIGHTMAGENTA_EX}Profit history...")
        getHistory();

    schedule.run_pending()
    time.sleep(0.1)