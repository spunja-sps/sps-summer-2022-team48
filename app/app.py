
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


def make_call(url):
    response = requests.get(url)
    return response.json()


def get_prices(list):
    api_codes = {
        "Arabica Coffee": "COFFEE",
        "Brent Crude Oil": "BRENTOIL",
        "Cocoa": "COCOA",
        "Corn": "CORN",
        "Natural Gas": "NG",
    }
    prices_dict = {}
    today = datetime.datetime.now().date()
    date = get_date(today)
    for item in list:
        url_today = "https://commodities-api.com/api/latest?access_key=cqmirudsx2mdaprj2o1s2ftv838j8n3ra5q8cge1s195uxsk8sv3jw4bddfo&symbols=" + \
            api_codes[item]
        url_past = "https://commodities-api.com/api/" + str(date) + "?access_key=cqmirudsx2mdaprj2o1s2ftv838j8n3ra5q8cge1s195uxsk8sv3jw4bddfo&&symbols=" + \
            api_codes[item]
        jsonResponseToday = make_call(url_today)
        jsonResponsePast = make_call(url_past)
        print(date)
        price_today = 1 / \
            jsonResponseToday["data"]["rates"][api_codes[item]]
        print(price_today)
        print(jsonResponsePast)
        price_at_date = 1 / \
            jsonResponsePast["data"]["rates"][api_codes[item]]
        prices_dict[item] = [price_today,
                             get_change(price_today, price_at_date)]
        print(prices_dict[item])
    return prices_dict


def get_date(today):
    # gets last month's date for now
    return today + dateutil.relativedelta.relativedelta(months=-1)


def get_change(price_today, price_at_date):
    #returns % change
    return ((price_today - price_at_date)/price_at_date) * 100


if __name__ == '__main__':
    app.run(debug=True)
