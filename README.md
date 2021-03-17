# FlexpoolBot
Simple python bot to check earnings in Flexpool mining pool.

## How to use
In order to use the bot you need to create 3 environment variables:
   ETHERSCAN_APIKEY: an apikey from etherscan.io (check: https://etherscan.io/apis), 
   ETH_WALLET: your etherium wallet address used with flexpool (check: https://ethereum.org/en/wallets/),
   ETHGASSTATION_APIKEY: an apikey from eth gas station (check: https://docs.ethgasstation.info/).
   
after that just run:
```
python app.py
```
press h for help about what the bot does, but for now the bot you can:
  Press 1 for current profits,
  Press 2 for expected earnings,
  Press 3 for profits history,
  Press 4 for gas price,
  Press 5 for daily stats.

##What it does
the bot will create a database with two tables, balance and profit, in balance it will record your balance everyday at 09:00 am and calculate your profit (today's balance - yesterday's balance).
So you can check your profits from the past week, with an average per day, calculate expected earnings, also retrieve expected earning according to flexpool and calculate the expected earning per week and per month (30 days).
