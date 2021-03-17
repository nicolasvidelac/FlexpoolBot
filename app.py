from datetime import datetime
import schedule
import requests
import sqlite3
import math
import keyboard
import os
import time
from colorama import Fore, init

connection = sqlite3.connect('flexpool.db')
cursor = connection.cursor();
init(convert=True)

apiKeyEther = str(os.environ.get('ETHERSCAN_APIKEY'))
apiKeyGasStation = str(os.environ.get('ETHGASSTATION_APIKEY'))

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

    minutosActual = datetime.now().minute + datetime.now().hour * 60 #la cantidad de minutos de hoy

    minedMinutes = 0;
    if minutosActual >= 9 * 60:
        minedMinutes = minutosActual - 9 * 60
    else:
        minedMinutes = minutosActual + 15 * 60

    expectedTodaysEarnings = todaysProfit / minedMinutes * (24 * 60)

    print(
        "ganancias hasta ahora: ", str(truncate(todaysProfit,6)), "eth / $", "{0:0>5}".format(truncate(todaysProfit * ethPrice,2)), "usd",
        "\nganancias esperadas:   ", str(truncate(expectedTodaysEarnings, 6)), "eth / $", "{:0>5}".format(truncate(expectedTodaysEarnings * ethPrice,2)), "usd",
        "\n\nganancias totales:", str(truncate(todaysBalance,6)), "eth / $", truncate(todaysBalance * ethPrice,2), "usd",
        "\nprecio de eth:   $", ethPrice, "usd"
    )

    return;

def expectedEarnings():
    url = 'https://flexpool.io/api/v1/miner/%s/estimatedDailyRevenue'%wallet
    response = requests.get(url)
    ethPrice = getEthPrice();
    earnings = gweiToEth( response.json()['result'])
    
    print("ganancias por dia:   ",truncate(earnings,4), "eth / $",    truncate(earnings * ethPrice,2))
    print("ganancias por semana:",truncate(earnings*7,4), "eth / $",  truncate(earnings * 7 * ethPrice,2))
    print("ganancias por mes:   ", truncate(earnings*30,4), "eth / $",truncate(earnings * 30 * ethPrice,2))
    return;

def getGastPrice():
    url = 'https://www.ethgasstation.info/https://ethgasstation.info/api/ethgasAPI.json?api-key=%s'%apiKeyGasStation
    response = (requests.get(url)).json()

    gasPrice = float(response['safeLow'] / 10)
    transactionFee = 21000
    usdPrice = getEthPrice()

    print(
        int(gasPrice), "gwei\n" +
        str(gasPrice / 1000000000 * transactionFee * usdPrice)[:4], "usd"
    )

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

    profit = cursor.fetchall()[-7:]
    #Que solo me muestre el historial de la ultima semana

    cursor.execute("SELECT TOTAL FROM BALANCE")
    balance = cursor.fetchall()[-1][0]

    ethPrice = getEthPrice()

    total = 0

    for item in reversed(profit):
        total += item[1]
        print("generado:", format(truncate(item[1],4),'.4f'),"eth / $", format(truncate(item[1] * ethPrice,2),'.2f') , "// fecha:", item[0][5:10])
    
    print("\nganancias ultima semana:", truncate(total,4), "eth / $", format(truncate(total * ethPrice,2),'.2f'))
    promedio = truncate(total / 7,4)
    print("promedio  ultima semana:", promedio, "eth / $", format(truncate(promedio * ethPrice,2),'.2f'))

def getEthPrice():
    url = 'https://api.etherscan.io/api?module=stats&action=ethprice&apikey=%s'%apiKeyEther
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
    if keyboard.is_pressed('1'):
        print(f"\n{Fore.LIGHTGREEN_EX}Current profits at", str(datetime.now().time())[:5] + ":")
        profitCalculator(False)

    elif keyboard.is_pressed('2'):
        print(f"\n{Fore.LIGHTYELLOW_EX}Expected earnings at", str(datetime.now().time())[:5] + ":")
        expectedEarnings()

    elif keyboard.is_pressed('3'):
        print(f"\n{Fore.LIGHTCYAN_EX}Profit history at", str(datetime.now().time())[:5] + ":\n")
        getHistory();

    elif keyboard.is_pressed('4'):
        print(f"\n{Fore.MAGENTA}Gas price at", str(datetime.now().time())[:5] + ":")
        getGastPrice()

    elif keyboard.is_pressed('5'):
        print(f"\n{Fore.LIGHTWHITE_EX}Daily report at", str(datetime.now().time())[:5] + ":")
        dailyReport()

    elif keyboard.is_pressed('h'):
        print(
            f"\n{Fore.LIGHTGREEN_EX}Press 1 for current profits",
            f"\n{Fore.LIGHTYELLOW_EX}Press 2 for expected earnings",
            f"\n{Fore.LIGHTCYAN_EX}Press 3 for profits history",
            f"\n{Fore.LIGHTMAGENTA_EX}Press 4 for gas price",
            f"\n{Fore.LIGHTWHITE_EX}Press 5 for daily profits",
        )

    schedule.run_pending()
    time.sleep(0.1)