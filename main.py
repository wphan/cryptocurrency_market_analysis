import os

import plotly.graph_objs as go
from plotly.offline import plot
from grab_marketcap_data import get_market_data

START_DATE = "20170601"
END_DATE = "20180126"

def analyze():
    colors = [
        "rgb(244, 67, 54)",
        "rgb(233, 30, 99)",
        "rgb(156, 39, 176)",
        "rgb(63, 81, 181)",
        "rgb(33, 150, 243)",
        "rgb(0, 188, 212)",
        "rgb(0, 150, 136)",
        "rgb(76, 175, 80)",
        "rgb(205, 220, 57)",
        "rgb(255, 193, 7)",
        "rgb(255, 87, 34)",
        "rgb(96, 125, 139)",
        "rgb(121, 85, 72)"
    ]

    # gets a bunch of markets, normalize, and plot
    coin_sets= [['bitcoin', 'ethereum', 'ripple', 'bitcoin-cash', 'cardano'],
                ['bitcoin', 'stellar', 'litecoin', 'eos', 'neo'],
                ['bitcoin', 'nem', 'iota', 'dash', 'monero'],
                ['bitcoin', 'tron', 'vechain', 'bitcoin-gold', 'icon'],
                ['bitcoin', 'qtum', 'ethereum-classic', 'lisk', 'raiblocks'],
                ['bitcoin', 'populous', 'omisego', 'tether', 'steem'],
                ['bitcoin', 'zcash', 'stratis', 'bytecoin-bcn', 'binance-coin'],
                ['bitcoin', 'verge', 'siacoin', 'bitshares', '0x'],
                ['bitcoin', 'status', 'ardor', 'walton', 'augur'],
                ['bitcoin', 'maker', 'waves', 'dogecoin', 'veritaseum']]
    col_to_plot = ["close", "volume", "market cap"]
    line_style = ["line", "dash", "dot"]
    for coin_set in coin_sets:
        traces = []
        for coin_idx, coin in enumerate(coin_set):
            # normalize all numeric columns:
            cols_to_norm = ['open', 'high', 'low', 'close', 'volume', 'market cap']
            df = get_market_data(coin, START_DATE, END_DATE)
            df = df.sort_index(ascending=False)
            df[cols_to_norm] = df[cols_to_norm].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

            # create traces for each interesting column
            for idx, col in enumerate(col_to_plot):
                # create a noramlized trace
                traces.append(go.Scatter(
                    x=df['date'],
                    y=df[col],
                    mode="lines",
                    name='_'.join([coin, col]),
                    line=dict(
                        color=colors[coin_idx],
                        dash=line_style[idx],
                        smoothing=1.2
                    ),
                    visible='legendonly'
                ))

        # plot
        title = "Comparing Price, Volume, and Market Cap"
        layout = go.Layout(
            title=title,
            xaxis=dict(
                title='Date',
                showticklabels=True,
                tickangle=45
            ),
            yaxis=dict(
                title='USD Value (normalized)',
                showticklabels=True,
                tickangle=45
            )
        )
        fig = go.Figure(data=traces, layout=layout)
        name = '_'.join(coin_set) + ".html"
        plot(fig, filename=os.path.join("plots", name))


def generate_index_html():
    plots = os.listdir('plots')
    with open("index.html", 'w') as f:
        f.write("<!DOCTYPE HTML>\n")
        f.write("<html>\n")
        f.write("  <body>\n")
        f.write("    <H1>Market Cap compared with Price and Volume</H1>\n")
        for plot in plots:
            link_name = plot.split('.')[0].replace('_', ' ')
            f.write("    <a href='plots/{0}'>{1}</a><br>\n".format(plot, link_name))
        f.write("  </body>\n")
        f.write("</html>\n")


if __name__ == "__main__":
    analyze()
    generate_index_html()
