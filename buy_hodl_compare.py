"""
Python2.7 only.

Usage:
    source activate catalyst
    python buy_hold_compare.py
"""
import os
import pytz
import datetime
import global_vars

from catalyst import run_algorithm
from catalyst.api import order_target_percent, symbol, record

# defined in parent
# global SECTOR_NAME
# global TARGET_ASSET


def initialize(context):
    context.ASSET_NAME = global_vars.TARGET_ASSET
    if context.ASSET_NAME == "BCH_BTC":
        context.ASSET_NAME = "BCC_BTC"

    context.is_buying = True
    context.asset = symbol(context.ASSET_NAME)

    context.i = 0


def handle_data(context, data):
    # order once. at the beginning
    if context.i == 0:
        order_target_percent(context.asset, 1.0)

    record(
        price=data.current(context.asset, 'price'),
        volume=data.current(context.asset, 'volume'),
    )

    context.i += 1


def analyze(context=None, results=None):
    # Form DataFrame with selected data
    data = results[['portfolio_value']]

    # Save results in CSV file
    if not os.path.exists(os.path.join("comparisons", global_vars.SECTOR_NAME)):
        os.mkdir(os.path.join("comparisons", global_vars.SECTOR_NAME))

    filename = "hodl_" + context.ASSET_NAME
    data.to_csv(os.path.join("comparisons", global_vars.SECTOR_NAME, filename + ".csv"))


if __name__ == '__main__':
    # SECTOR_NAME = "gambling"
    # TARGET_ASSET = "fun_btc"
    start = datetime.datetime(2017, 11, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime.datetime(2018, 1, 5, 0, 0, 0, 0, pytz.utc)
    run_algorithm(initialize=initialize,
                  handle_data=handle_data,
                  analyze=analyze,
                  start=start,
                  end=end,
                  exchange_name='bittrex',
                  capital_base=100000, )
