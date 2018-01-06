"""
this should go through directory tree comparison/* and plot the optimized
portfolio performance versus the hodl performances
"""

import os
import pandas as pd
import global_vars

import plotly.graph_objs as go
from plotly.offline import plot


# discover results csv
sampled_sectors_dir = os.listdir("comparisons")
for sector_dir in sampled_sectors_dir:
    csv_files = os.listdir(os.path.join("comparisons", sector_dir))
    print("Plotting for {}".format(sector_dir))

    # extract the optimized file
    # optimized = "optimized_" + sector_dir + ".csv"
    # equal_weights = "equal_weights" + sector_dir + ".csv"
    # csv_files.remove(optimized)
    # csv_files.remove(equal_weights)

    traces = []
    for idx, csv in enumerate(csv_files):
        # figure out what type of csv this is
        if "optimized_" in csv:
            trace_name = "optimized_portfolio"
            dash = "longdash"
        elif "equal_weights_" in csv:
            trace_name = "equal_weights"
            dash = "dash"
        else:
            # it's a hodl trace
            trace_name = csv.split('.')[0]
            dash = "solid"

        df = pd.read_csv(os.path.join("comparisons", sector_dir, csv),
                         header=None,
                         names=["date", "portfolio_value"])
        traces.append(go.Scatter(
            x=df['date'],
            y=df['portfolio_value'],
            mode="lines",
            name=trace_name,
            line=dict(
                color=global_vars.colors[idx],
                dash=dash,
                smoothing=1.2
            )
        ))

    # plot each sector
    trace_filename = sector_dir + "_portfolios_compared.html"
    sector_title = sector_dir.replace('_', ' ').title()
    layout = go.Layout(
        title=sector_title,
        xaxis=dict(
            title='Date',
            showticklabels=True,
            tickangle=45
        ),
        yaxis=dict(
            title='Portfolio Value (BTC)',
            showticklabels=True,
            tickangle=45
        )
    )
    fig = go.Figure(data=traces, layout=layout)
    print("Plot for {0} saved to {1}".format(sector_title, trace_filename))
    plot(fig, filename=trace_filename)
