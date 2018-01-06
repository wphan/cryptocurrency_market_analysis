"""
Python2.7 only.

Usage:
    source activate catalyst
    python portfolio_optimization.py
"""

import pytz
import datetime
import json
import global_vars

from catalyst.api import record, symbol, symbols, order_target_percent
from catalyst.utils.run_algo import run_algorithm


def initialize(context):
    many_assets = []
    with open('sectors.json', 'r') as f:
        sectors = json.load(f)

    for sector in sectors:
        many_assets += sectors[sector]

    a_many_assets = []
    # find the ones taht dont go back far enough!
    for asset in many_assets:
        asset = asset.replace('/', '_')
        if asset not in global_vars.ignored_assets:
            a_many_assets.append(asset)

    a_many_assets.remove("BCH_BTC")
    a_many_assets.append("BCC_BTC")

    context.assets = symbols(*a_many_assets)


def handle_data(context, data):
    print("HEY")
    dates = data.history(context.assets,
                         fields="price",
                         bar_count=15 + 1,
                         frequency='1d')
    print(dates)

    exit()


def analyze(context=None, results=None):
    pass

if __name__ == '__main__':
    start = datetime.datetime(2017, 10, 26, 0, 0, 0, 0, pytz.utc)
    end = datetime.datetime(2018, 1, 4, 0, 0, 0, 0, pytz.utc)
    results = run_algorithm(initialize=initialize,
                            handle_data=handle_data,
                            analyze=analyze,
                            start=start,
                            end=end,
                            exchange_name='bittrex',
                            capital_base=100000, )
