"""
Python2.7 only.

Usage:
    source activate catalyst
    python portfolio_equal_weights.py
"""
import os
import json
import pytz
import global_vars
from datetime import datetime

from catalyst.api import symbols, order_target_percent
from catalyst.utils.run_algo import run_algorithm


def initialize(context):
    # Portfolio assets list
    with open('sectors.json', 'r') as f:
        sectors = json.load(f)[global_vars.SECTOR_NAME]
        sectors = [sector.replace("/", "_") for sector in sectors]

    # stupid catalyst uses bittrex symbols for symbols
    if "BCH_BTC" in sectors:
        sectors.remove("BCH_BTC")
        sectors.append("BCC_BTC")
    # too new
    for asset in global_vars.ignored_assets:
        if asset in sectors:
            sectors.remove(asset)

    # uhh i think we need more than one asset
    if len(sectors) < 2:
        print("only 1 asset in bunch for sector: {}".format(global_vars.SECTOR_NAME))
        exit()

    context.assets = symbols(*sectors)
    context.nassets = len(context.assets)

    # Set the time window that will be used to compute expected return
    # and asset correlations
    context.window = 15

    # Set the number of days between each portfolio rebalancing
    context.rebalance_period = 5
    context.i = 0


def handle_data(context, data):
    # only rebalance at beginning of algo execution and every multiple of
    # rebalance period
    try:
        for asset in context.assets:
            if data.can_trade(asset):
                order_target_percent(asset, 1.0 / float(context.nassets))
    except Exception as e:
        print("===============================")
        print("Error optimizing {}".format(global_vars.SECTOR_NAME))
        print("Assets: {}".format(context.assets))
        print("{}".format(e))
        print("===============================")

    context.i += 1


def analyze(context=None, results=None):
    # Form DataFrame with selected data
    data = results[['portfolio_value']]

    # Save results in CSV file
    if not os.path.exists(os.path.join("comparisons", global_vars.SECTOR_NAME)):
        os.mkdir(os.path.join("comparisons", global_vars.SECTOR_NAME))

    filename = "equal_weights_" + global_vars.SECTOR_NAME
    data.to_csv(os.path.join("comparisons", global_vars.SECTOR_NAME, filename + ".csv"))


if __name__ == '__main__':
    start = datetime(2017, 10, 27, 0, 0, 0, 0, pytz.utc)
    end = datetime(2018, 1, 5, 0, 0, 0, 0, pytz.utc)
    results = run_algorithm(initialize=initialize,
                            handle_data=handle_data,
                            analyze=analyze,
                            start=start,
                            end=end,
                            exchange_name='bittrex',
                            capital_base=100000, )
