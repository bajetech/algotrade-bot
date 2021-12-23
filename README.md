# Algorand Trading Bot

> Simple automated bot for executing trades on supported DEXs that allow swaps between supported Algo/ASA trading pairs.

## Purpose

This is a simple bot, written in Python 3, that allows price points to be configured for the bot to send trading requests to supported DEXs to swap between any supported Algo/ASA trading pair.

**The supported pairs are:**

- Algo/USDt
- Algo/USDC

At the moment this bot integrates with the following DEXs:

- [Tinyman](https://tinyman.org/)

## Development Status

This bot is currently under active early development and has not yet been audited. It should therefore not be considered stable.

## Off-chain DB

This bot is implemented to make use of an off-chain MariaDB database that currently contains two tables:

- The `assets` table holds token identification details of the Algorand native token and Algorand Standard Assets (ASAs) that can be traded with the bot.
- The `trades` table is where the bot looks for trade requests you want performed on behalf of your Algorand wallet.

Schema definitions for these tables can be found in the file [db/schema.sql](./db/schema.sql).

The file [db/init.sql](./db/init.sql) contains SQL statements to initialize the `assets` table with the details of the tokens supported so far by this bot. Details for the tokens on both Algorand's testnet and mainnet are included. Support for additional tokens can easily be integrated of course by adding their details to this table. However there MUST be liquidity pools available for any token pairs that you want to set up trades for on the DEXs that this bot integrates with.

## Environment Variables

There are environment variables that need to be properly configured for the bot to work. Create a file named `.env` in the ptoject root folder and copy the contents of `.env.example` to it, then set the variables in .env to appropriate values.

## Dislaimer

I started developing this bot because I wanted to automate trades of the Algo/ASA cryptocurrency tokens I hold as part of my business assets. After some consideration I've decided to build it in the open. Any and ALL use of this bot may involve various risks, including, but not limited to, losses during an automated swap due to the fluctuation of prices of tokens in a trading pair. Before using this bot, you should review it's code and any accompanying documentation to understand how the bot works. You are responsible for doing your diligence on the risks involved.

## License

This bot is licensed under the [Apache License 2.0](https://github.com/bajetech/algotrade-bot/blob/main/LICENSE). Please be guided accordingly.
