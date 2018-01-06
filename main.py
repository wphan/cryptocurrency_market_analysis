"""
Python2.7 only.

Usage:
    source activate catalyst
    python buy_hold_compare.py
"""
import json
import pytz
import datetime

import portfolio_optimization
import buy_hodl_compare
import portfolio_equal_weights

from catalyst.utils.run_algo import run_algorithm

import global_vars


def main():
    with open("sectors.json", "r") as f:
        sectors = json.load(f)
    start = datetime.datetime(2017, 10, 26, 0, 0, 0, 0, pytz.utc)
    end = datetime.datetime(2018, 1, 4, 0, 0, 0, 0, pytz.utc)

    for sector in sectors:
        # only run sectors with sufficient info
        if sector in global_vars.ignored_sectors:
            print("skipping {}".format(sector))
            continue

        # first run an optimized sector
        global_vars.SECTOR_NAME = sector
        print("\nRunning optimized portfolio for: {}".format(global_vars.SECTOR_NAME))
        run_algorithm(initialize=portfolio_optimization.initialize,
                      handle_data=portfolio_optimization.handle_data,
                      analyze=portfolio_optimization.analyze,
                      start=start,
                      end=end,
                      exchange_name='bittrex',
                      capital_base=100000, )
        print("\nDone optimized portfolio for: {}".format(global_vars.SECTOR_NAME))

        # try with equal weights
        global_vars.SECTOR_NAME = sector
        print("\nRunning portfolio with equal weights for: {}".format(global_vars.SECTOR_NAME))
        run_algorithm(initialize=portfolio_equal_weights.initialize,
                      handle_data=portfolio_equal_weights.handle_data,
                      analyze=portfolio_equal_weights.analyze,
                      start=start,
                      end=end,
                      exchange_name='bittrex',
                      capital_base=100000, )
        print("\nDone portfolio with equal weights for: {}".format(global_vars.SECTOR_NAME))

        # then run a buy and hodl for each asset in the sector
        for asset in sectors[sector]:
            global_vars.TARGET_ASSET = asset.replace("/", "_")
            if global_vars.TARGET_ASSET in global_vars.ignored_assets:
                print("{} ignored, too new?".format(global_vars.TARGET_ASSET))
                continue

            print("\n    Running buy and hodl comparisons for: {}".format(global_vars.TARGET_ASSET))
            run_algorithm(initialize=buy_hodl_compare.initialize,
                          handle_data=buy_hodl_compare.handle_data,
                          analyze=buy_hodl_compare.analyze,
                          start=start,
                          end=end,
                          exchange_name='bittrex',
                          capital_base=100000, )


def eq_only():
    with open("sectors.json", "r") as f:
        sectors = json.load(f)
    start = datetime.datetime(2017, 10, 26, 0, 0, 0, 0, pytz.utc)
    end = datetime.datetime(2018, 1, 4, 0, 0, 0, 0, pytz.utc)

    for sector in sectors:
        # only run sectors with sufficient info
        if sector in global_vars.ignored_sectors:
            print("skipping {}".format(sector))
            continue

        # first run an optimized sector
        global_vars.SECTOR_NAME = sector
        # try with equal weights
        global_vars.SECTOR_NAME = sector
        print("\nRunning portfolio with equal weights for: {}".format(global_vars.SECTOR_NAME))
        run_algorithm(initialize=portfolio_equal_weights.initialize,
                      handle_data=portfolio_equal_weights.handle_data,
                      analyze=portfolio_equal_weights.analyze,
                      start=start,
                      end=end,
                      exchange_name='bittrex',
                      capital_base=100000, )
        print("\nDone portfolio with equal weights for: {}".format(global_vars.SECTOR_NAME))


if __name__ == "__main__":
    main()
    # eq_only()
    # check_price_history()
