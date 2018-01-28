import pprint
import pandas as pd
import numpy as np
import urllib.request
from bs4 import BeautifulSoup


def get_market_data(coin_name, start_date, end_date):
    """Grabs market data(day) from coinmarketcap
    :param: str: coin_name: ie: bitcoin, ethereum
    :param: str: start_date: day to start grabbing data, of form YYYYMMDD, ie 20170601
    :param: str: end_date: day to end grabbing data, of form YYYYMMDD, ie 20180125
    :return: pandas.DataFrame: with headers: ['date', 'open', 'high', 'low', 'close', 'volume', 'market cap']
    """
    url = 'https://coinmarketcap.com/currencies/{0}/historical-data/?start={1}&end={2}'.format(coin_name, start_date, end_date)
    ret = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(ret, 'lxml')
    table = soup.find_all(class_="table-responsive")[0].find_all('tbody')[0].find_all('tr')

    columns=['date', 'open', 'high', 'low', 'close', 'volume', 'market cap']
    rows = []
    for row in table:
        new_row = []
        for cell in row:
            if cell != '\n':
                if cell.string == '-':
                    value = 0
                else:
                    try:
                        value = float(cell.string.replace(',', ''))
                    except ValueError:
                        # it's the date
                        value = cell.string
                    new_row.append(value)
        rows.append(new_row)

    df = pd.DataFrame(data=rows, columns=columns)
    return df
    #df.to_csv("market_cap.csv", index=False)
