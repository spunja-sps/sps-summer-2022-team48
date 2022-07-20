
from flask import Flask, render_template, request, session
from flask_session import Session
import json
import requests
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def welcome():
    return render_template("index.html")


@app.route('/info')
def info():
    return render_template("info.html")


@app.route('/config')
def config_page():
    return render_template("config.html")


@app.route('/data-summary', methods=['POST'])
def data_summary_page():
    watchlist = request.form.getlist("itemDropdown")
    session["watchlist"] = watchlist

    prices_dict = get_prices(watchlist)

    return render_template("data_summary.html", prices_dict=prices_dict)


@app.route('/graphing', methods=['GET', 'POST'])
def detailed_data_page():
    selected_item = request.args.get('item')
    print(selected_item)

    watchlist = session.get("watchlist")
    print(watchlist)

    # to be added back in after API is implemented
    # prices_dict = get_prices([selected_item])
    # print(prices_dict)

    dummy_data = [
        (1, 5),
        (2, 7),
        (3, 2),
        (4, 4),
        (5, 10)
    ]

    dummy_labels = [row[0] for row in dummy_data]
    dummy_values = [row[1] for row in dummy_data]

    return render_template("data_detailed.html", item=selected_item, labels=dummy_labels, values=dummy_values)


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
        "Canola": "CANO",
        "Cotton": "COTTON",
        "Oat": "OAT",
        "Rice": "RICE",
        "Soybeans": "SOYBEAN",
        "Sugar": "SUGAR",
        "Wheat": "WHEAT",
        "Beef": "LCAT"

    }
    prices_dict = {}
    today = datetime.today()
    yesterday = (today - timedelta(days=1)).date()
    print(yesterday)
    print(list)
    lastMonthDate = get_date(today, 30)
    print(lastMonthDate)
    for item in list:
        url = "https://commodities-api.com/api/timeseries?access_key=0yw3m4s5g7fz8ialo49gqxtjnxbto11t59jg5qw4krdo15j48v37q06hgsnx&start_date=" + str(lastMonthDate) + "&end_date=" + str(yesterday) + "&symbols=" + \
            api_codes[item]
        response = requests.get(url)
        jsonResponse = response.json()
        price_yesterday = 1 / \
            jsonResponse["data"]["rates"][str(yesterday)][api_codes[item]]
        price_at_date = 1 / \
            jsonResponse["data"]["rates"][str(lastMonthDate)][api_codes[item]]
        prices_dict[item] = [price_yesterday,
                             get_change(price_yesterday, price_at_date)]
        print(prices_dict[item])
    return prices_dict


def get_date(today, numberOfDays):
    # returns the date at numberOfDays going back from today
    # ex) if numberOfDays = 7, returns last week's date
    return (today - timedelta(numberOfDays)).date()


def get_change(price_today, price_at_date):
    # returns % change
    return ((price_today - price_at_date)/price_at_date) * 100


if __name__ == '__main__':
    app.run(debug=True)
