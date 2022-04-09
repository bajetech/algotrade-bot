import os
import sys
import time
import mariadb
from algosdk import mnemonic
from tinyman.v1.client import TinymanTestnetClient, TinymanMainnetClient
from utils import get_db_connection, Account, get_supported_algo_assets
from dotenv import load_dotenv
load_dotenv()

# Connect to off-chain DB.
conn = get_db_connection()
if conn is None:
    print("Abandoning this run of the bot since connection to the off-chain DB failed")
    sys.exit(1)

cursor = conn.cursor()


def run_bot(network: str):
    key = mnemonic.to_private_key(os.getenv("acct_mnemonic"))
    account = Account(os.getenv("acct_address"), key)
    token_network = network.lower()
    supported_assets = get_supported_algo_assets(token_network, cursor)

    if supported_assets is None:
        print("Unable to retrieve information on supported assets. Abandoning bot run.")
        sys.exit(1)

    # Declare two lists that will be used to keep track of the trades that are completed
    # in this run and the reverse trades that are to be setup, if any.
    swaps_completed = []
    reverse_trades = []

    while (True):
        # Query for swaps that need to be carried out.
        try:
            cursor.execute("SELECT id, asset1_id, asset2_id, asset_in_id, asset_in_amt, slippage, min_price_for_sell, do_redeem, do_reverse FROM trades WHERE wallet_address=? AND token_network=? AND is_active=? AND is_completed=?", (account.address, token_network, 1, 0))
        except mariadb.Error as e:
            print(f"Error attempting to query for desired trades: {e}")
            sys.exit(1)

        # Create Tinyman client on behalf of the trading wallet address.
        if token_network == "testnet":
            client = TinymanTestnetClient(user_address=account.address)
        else:
            client = TinymanMainnetClient(user_address=account.address)

        # Check if the account is opted into Tinyman and optin if necessary.
        if (not client.is_opted_in()):
            print('Account not opted into app, opting in now..')
            transaction_group = client.prepare_app_optin_transactions()
            transaction_group.sign_with_private_key(
                account.address, account.private_key)
            result = client.submit(transaction_group, wait=True)

        # Loop through the swaps to be carried out.
        for (id, asset1_id, asset2_id, asset_in_id, asset_in_amt, slippage, min_price_for_sell, do_redeem, do_reverse) in cursor:
            # Fetch the assets of interest.
            asset1 = client.fetch_asset(
                supported_assets[asset1_id].token_asset_id)
            asset2 = client.fetch_asset(
                supported_assets[asset2_id].token_asset_id)

            # Fetch the pool we will work with.
            pool = client.fetch_pool(asset1, asset2)

            # Get a quote for a swap of asset_in amt to asset_out with the configured slippage tolerance.
            if asset_in_id != asset2_id:
                quote = pool.fetch_fixed_input_swap_quote(
                    asset1(asset_in_amt), float(slippage))
                print(quote)
                print(
                    f'{supported_assets[asset2_id].token_code} per {supported_assets[asset1_id].token_code}: {quote.price}')
                print(
                    f'{supported_assets[asset2_id].token_code} per {supported_assets[asset1_id].token_code} (worst case): {quote.price_with_slippage}')
            else:
                quote = pool.fetch_fixed_input_swap_quote(
                    asset2(asset_in_amt), float(slippage))
                print(quote)
                print(
                    f'{supported_assets[asset1_id].token_code} per {supported_assets[asset2_id].token_code}: {quote.price}')
                print(
                    f'{supported_assets[asset1_id].token_code} per {supported_assets[asset2_id].token_code} (worst case): {quote.price_with_slippage}')

            # We only want to sell if asset_in unit price is > min_price_for_sell asset_out.
            if quote.price_with_slippage > float(min_price_for_sell):
                total_asset_out_received = quote.amount_out_with_slippage.amount
                print(
                    f'Swapping {quote.amount_in} to {quote.amount_out_with_slippage}')

                # Prepare a transaction group.
                transaction_group = pool.prepare_swap_transactions_from_quote(
                    quote)

                # Sign the group with the wallet's key.
                transaction_group.sign_with_private_key(
                    account.address, account.private_key)

                # Submit transactions to the network and wait for confirmation.
                result = client.submit(transaction_group, wait=True)

                # Check if any excess remains after the swap.
                excess = pool.fetch_excess_amounts()
                if asset_in_id != asset2_id:
                    if asset2 in excess:
                        amount = excess[asset2]
                        total_asset_out_received += amount.amount
                        print(f'Excess: {amount}')

                        if do_redeem != 0:
                            transaction_group = pool.prepare_redeem_transactions(
                                amount)
                            transaction_group.sign_with_private_key(
                                account.address, account.private_key)
                            result = client.submit(
                                transaction_group, wait=True)
                        else:
                            print(
                                f'Excess {supported_assets[asset2_id].token_code} remains from the trade but the configuration is set to ignore redeeming the excess at this time.')
                else:
                    if asset1 in excess:
                        amount = excess[asset1]
                        total_asset_out_received += amount.amount
                        print(f'Excess: {amount}')

                        if do_redeem != 0:
                            transaction_group = pool.prepare_redeem_transactions(
                                amount)
                            transaction_group.sign_with_private_key(
                                account.address, account.private_key)
                            result = client.submit(
                                transaction_group, wait=True)
                        else:
                            print(
                                f'Excess {supported_assets[asset1_id].token_code} remains from the trade but the configuration is set to ignore redeeming the excess at this time.')

                # Swap will be marked as completed in the off-chain DB.
                swaps_completed.append(int(id))

                if do_reverse != 0:
                    if asset_in_id != asset2_id:
                        asset_out_id = asset2_id
                    else:
                        asset_out_id = asset1_id

                    if int(supported_assets[asset_in_id].token_asset_id) == 0:
                        # If we reach here then Algo is the asset_in token. Note that Algo amounts
                        # carry 6 demical places, while there are some ASAs that have a higher no.
                        # of decimal places so we need to account for this in our calculations.
                        NUM_DECIMAL_PLACES_NATIVE = 6
                        asset_in_amt = int(asset_in_amt) + 14000

                        if supported_assets[asset_out_id].num_decimal_places > NUM_DECIMAL_PLACES_NATIVE:
                            # diff = int(
                            #     supported_assets[asset_out_id].num_decimal_places) - NUM_DECIMAL_PLACES_NATIVE
                            reverse_min_price = (
                                float(asset_in_amt) / float(total_asset_out_received)) + 0.2
                        else:
                            reverse_min_price = (float(asset_in_amt) / float(total_asset_out_received)) + float(
                                os.getenv("reverse_trade_min_profit_margin"))
                    else:
                        # TODO: This else branch needs fixing to support a difference in decimal places!!
                        reverse_min_price = (float(asset_in_amt) / float(total_asset_out_received + 14000)) + float(
                            os.getenv("reverse_trade_min_profit_margin"))

                    reverse_trades.append((account.address, asset2_id, asset1_id, asset2_id, total_asset_out_received, float(
                        slippage), reverse_min_price, 1, 0, 0, token_network, int(id)))

        # Update completed flag for the completed swaps.
        for swap_id in swaps_completed:
            cursor.execute(
                "UPDATE trades SET is_completed=1 WHERE id=?", (swap_id,))

        # Setup reverse trades.
        for trade in reverse_trades:
            cursor.execute("INSERT INTO trades (wallet_address, asset1_id, asset2_id, asset_in_id, asset_in_amt, slippage, min_price_for_sell, do_redeem, is_completed, do_reverse, token_network, origin_trade) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", trade)

        swaps_completed.clear()
        reverse_trades.clear()

        time.sleep(float(os.getenv("bot_interval")))
