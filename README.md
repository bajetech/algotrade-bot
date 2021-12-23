# Algorand Trading Bot

> Simple automated bot for executing trades on supported DEXs that allow swaps between supported Algo/ASA trading pairs.

## Disclaimer

I started developing this bot because I wanted to automate trades of the Algo/ASA cryptocurrency tokens I hold as part of my business assets. After some consideration I've decided to build it in the open. Any and ALL use of this bot may involve various risks, including, but not limited to, losses during an automated swap due to the fluctuation of prices of tokens in a trading pair. Before using this bot, you should review it's code and any accompanying documentation to understand how the bot works.

No part of this repository is intended to provide or suggest any financial advice, strategy or any promise that use of the code within this repository will guarantee any financial gain. This project is for educational purposes and demonstrates what is possible in the world of decentralized finance (DeFi) and decentralized trading. Should you choose to make use of this bot, remember that you are responsible for doing your due diligence on the risks involved.

## License

This bot is licensed under the [Apache License 2.0](https://github.com/bajetech/algotrade-bot/blob/main/LICENSE). Please be guided accordingly.

## Purpose

This is a simple bot, written in Python 3, that allows price points to be configured for the bot to send trading requests to supported DEXs to swap between any supported Algo/ASA trading pair.

**The supported pairs are:**

- Algo/USDt
- Algo/USDC

At the moment this bot integrates with the following DEXs:

- [Tinyman](https://tinyman.org/)

## Development Status

This bot is currently under active early development and has not yet been audited. It should therefore not be considered stable.

## Development Setup

This repo requires Python 3.7 or higher. We recommend you use a Python virtual environment to install the required dependencies.

Set up venv (one time):

- `python3 -m venv venv`

Active venv:

- `. venv/bin/activate` (if your shell is bash/zsh)
- `. venv/bin/activate.fish` (if your shell is fish)

Install dependencies:

- `pip install -r requirements.txt`

The `tinyman-py-sdk` package is also needed but it is not yet released on PYPI. It can be installed directly from the tinyman-py-sdk repository with pip:

`pip install git+https://github.com/tinymanorg/tinyman-py-sdk.git`

## Off-chain DB

This bot is implemented to make use of an off-chain MariaDB database that currently contains two tables:

- The `assets` table holds token identification details of the Algorand native token and Algorand Standard Assets (ASAs) that can be traded with the bot.
- The `trades` table is where the bot looks for trade requests you want performed on behalf of your Algorand wallet.

Schema definitions for these tables can be found in the file [db/schema.sql](./db/schema.sql).

The file [db/init.sql](./db/init.sql) contains SQL statements to initialize the `assets` table with the details of the tokens supported so far by this bot. Details for the tokens on both Algorand's testnet and mainnet are included. Support for additional tokens can easily be integrated of course by adding their details to this table. However there MUST be liquidity pools available for any token pairs that you want to set up trades for on the DEXs that this bot integrates with.

## Environment Variables

There are environment variables that need to be properly configured for the bot to work. Create a file named `.env` in the ptoject root folder and copy the contents of `.env.example` to it, then set the variables in **.env** to appropriate values.

## Launching the bot (to run every X seconds)

There are multiple ways that one can go about setting up a bot to run every some number of seconds. Since I wanted to keep this simple I decided to go the route of using the python Time module to keep the bot running indefinitely so all you need to do is run the appropriate python script (`bot-mainnet.py` for Algorand mainnet, `bot-testnet.py` for Algorand testnet).

By default the bot will run in _5 second intervals_. To customise this interval change the `bot_interval` .env variable to the desired number of seconds.
