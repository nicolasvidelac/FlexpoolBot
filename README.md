# FlexpoolBot
Simple python bot to check earnings in Flexpool mining pool.

## What it does
The bot will create a database with two tables, balance and profit, in balance it will record your balance everyday at 09:00 am and calculate your profit (today's balance - yesterday's balance).

So you can check your profits from the past week, with an average per day, calculate expected earnings, also retrieve expected earning according to flexpool and calculate the expected earning per week and per month (30 days).

## How to use
In order to use the bot you need to create an environment variable:
   * ETH_WALLET: the value is your etherium wallet address used with flexpool.

Also, the program uses python and sqlite, so you need to install those as well:
   * python: https://www.python.org/downloads/.
   * sqlite: https://sqlite.org/download.html.

After that just run:
```
python app.py
```
You can press h for help about what the bot does, but for now the bot you can:
 * Press 1 for current profits.
 * Press 2 for expected earnings.
 * Press 3 for profits history.
 * Press 4 for gas price.
 * Press 5 for daily stats.

