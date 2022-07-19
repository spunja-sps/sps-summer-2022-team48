
from flask import Flask, render_template, request
import json
import requests
import datetime
import dateutil.relativedelta


app = Flask(__name__)


@app.route('/')
def welcome():
    return render_template("index.html")


@app.route('/config')
def config_page():
    return render_template("config.html")


@app.route('/data-summary', methods=['POST'])
def data_summary_page():
    watchlist = request.form.getlist("itemDropdown")
    prices_dict = get_prices(watchlist)
    return render_template("data_summary.html", prices_dict=prices_dict)


def get_prices(list):
    api_codes = {
        # "Corn": "CHRIS/CME_C1",
        # "Oats": "CHRIS/CME_O1",
        # "Wheat": "CHRIS/CME_W1",
        # "Soybean": "CHRIS/CME_S1",
        # "Dairy": "CHRIS/CME_DA1",
        "Arabica Coffee": "COFFEE",
        "Brent Crude Oil": "BRENTOIL",
        "Cocoa": "COCOA",
        "Corn": "CORN",
        "Natural Gas": "NG",
    }
    prices_dict = {}

    for item in list:
        url = "https://commodities-api.com/api/timeseries?access_key=cqmirudsx2mdaprj2o1s2ftv838j8n3ra5q8cge1s195uxsk8sv3jw4bddfo&base=USD" + \
            api_codes[item]
        # url = "https://data.nasdaq.com/api/v3/datasets/" + \
        #     api_codes[item] + "?api_key=7PvJ27fqD-s1fgvKWZgk"
        response = requests.get(url)
        jsonResponse = response.json()
        today = datetime.datetime.now().date()
        date = get_date(today)
        print(date)
        price_today = 1/jsonResponse["data"]["rates"][today][api_codes[item]]
        price_at_date = 1/jsonResponse["data"]["rates"][date][api_codes[item]]
        prices_dict[item] = [price_today,
                             get_change(price_today, price_at_date)]
        print(prices_dict[item])
        # prices_dict[item] = [jsonResponse["dataset"]["data"]
        #                      [0][1], jsonResponse["dataset"]["data"][0][5]]
        # use dict["dataset"]["data"][0][5] for change in price - change not present for all items though
    return prices_dict


def get_date(today):
    # gets last month's date for now
    return today + dateutil.relativedelta.relativedelta(months=-1)


def get_change(price_today, price_at_date):
    #returns % change
    return ((price_today - price_at_date)/price_at_date) * 100


if __name__ == '__main__':
    app.run(debug=True)
