"""
Python2.7 only.

Usage:
    source activate catalyst
    python portfolio_optimization.py
"""
import os
import json
import pytz
import global_vars
from tabulate import tabulate

import numpy as np
import pandas as pd
from datetime import datetime

from catalyst.api import record, symbol, symbols, order_target_percent
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
    if context.i == 0 or context.i % context.rebalance_period == 0:
        n = context.window

        prices = data.history(context.assets, fields='price',
                              bar_count=n + 1, frequency='1d')
        pr = np.asmatrix(prices)
        t_prices = prices.iloc[1:n + 1]
        t_val = t_prices.values
        tminus_prices = prices.iloc[0:n]
        tminus_val = tminus_prices.values

        # Compute daily returns (r)
        r = np.asmatrix(t_val / tminus_val - 1)

        # Compute the expected returns of each asset with the average
        # daily return for the selected time window
        m = np.asmatrix(np.mean(r, axis=0))
        stds = np.std(r, axis=0)

        # Compute excess returns matrix (xr)
        xr = r - m

        # Matrix algebra to get variance-covariance matrix
        cov_m = np.dot(np.transpose(xr), xr) / n

        # Compute asset correlation matrix (informative only)
        corr_m = cov_m / np.dot(np.transpose(stds), stds)

        # Define portfolio optimization parameters
        n_portfolios = 50000
        results_array = np.zeros((3 + context.nassets, n_portfolios))
        for p in xrange(n_portfolios):
            weights = np.random.random(context.nassets)
            weights /= np.sum(weights)
            w = np.asmatrix(weights)
            p_r = np.sum(np.dot(w, np.transpose(m))) * 365
            p_std = np.sqrt(np.dot(np.dot(w, cov_m),
                                   np.transpose(w))) * np.sqrt(365)

            # store results in results array
            results_array[0, p] = p_r
            results_array[1, p] = p_std
            # store Sharpe Ratio (return / volatility) - risk free rate element
            # excluded for simplicity
            results_array[2, p] = results_array[0, p] / results_array[1, p]
            i = 0
            for iw in weights:
                results_array[3 + i, p] = weights[i]
                i += 1

        # convert results array to Pandas DataFrame
        results_frame = pd.DataFrame(np.transpose(results_array),
                                     columns=['r', 'stdev', 'sharpe'] + context.assets)
        # locate position of portfolio with highest Sharpe Ratio
        max_sharpe_port = results_frame.iloc[results_frame['sharpe'].idxmax()]

        # locate positon of portfolio with minimum standard deviation
        # min_vol_port = results_frame.iloc[results_frame['stdev'].idxmin()]

        # order optimal weights for each asset
        print(max_sharpe_port)
        try:
            for asset in context.assets:
                if data.can_trade(asset):
                    order_target_percent(asset, max_sharpe_port[asset])
        except Exception as e:
            print("===============================")
            print("Error optimizing {}".format(global_vars.SECTOR_NAME))
            print("Assets: {}".format(context.assets))
            print("{}".format(e))
            print("===============================")

        print("Iteraction: {}".format(context.i))
        # print("Simulation date: {}".format(data.current(context.assets, 'last_traded')))

        # create scatter plot coloured by Sharpe Ratio
        '''
        plt.scatter(results_frame.stdev,
                    results_frame.r,
                    c=results_frame.sharpe,
                    cmap='RdYlGn')
        plt.xlabel('Volatility')
        plt.ylabel('Returns')
        plt.colorbar()
        # plot red star to highlight position of portfolio
        # with highest Sharpe Ratio
        plt.scatter(max_sharpe_port[1],
                    max_sharpe_port[0],
                    marker='o',
                    color='b',
                    s=200)
        # plot green star to highlight position of minimum variance portfolio
        plt.show()
        '''
        record(pr=pr,
               r=r,
               m=m,
               stds=stds,
               max_sharpe_port=max_sharpe_port,
               corr_m=corr_m)
    context.i += 1


def analyze(context=None, results=None):
    # Form DataFrame with selected data
    data = results[['portfolio_value']]

    # Save results in CSV file
    if not os.path.exists(os.path.join("comparisons", global_vars.SECTOR_NAME)):
        os.mkdir(os.path.join("comparisons", global_vars.SECTOR_NAME))

    filename = "optimized_" + global_vars.SECTOR_NAME
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
