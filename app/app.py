
from flask import Flask, render_template, request, session
from flask_session import Session
import json
import requests


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def welcome():
    return render_template("index.html")


@app.route('/config')
def config_page():
    return render_template("config.html")


@app.route('/data-summary', methods=['POST'])
def data_summary_page():
    watchlist = request.form.getlist("itemDropdown")
    session["watchlist"] = watchlist

    prices_dict = get_prices(watchlist)

    return render_template("data_summary.html", prices_dict=prices_dict)

@app.route('/graphing')
def detailed_data_page():
    watchlist = session.get("watchlist")
    print(watchlist)

    return render_template("data_detailed.html")


def get_prices(list):
    api_codes = {
        "Corn": "CHRIS/CME_C1",
        "Oats": "CHRIS/CME_O1",
        "Wheat": "CHRIS/CME_W1",
        "Soybean": "CHRIS/CME_S1",
        "Dairy": "CHRIS/CME_DA1",
    }
    prices_dict = {}

    for item in list:
        url = "https://data.nasdaq.com/api/v3/datasets/" + \
            api_codes[item] + "?api_key=7PvJ27fqD-s1fgvKWZgk"
        response = requests.get(url)
        jsonResponse = response.json()
        prices_dict[item] = [jsonResponse["dataset"]["data"]
                             [0][1], jsonResponse["dataset"]["data"][0][5]]
        # use dict["dataset"]["data"][0][5] for change in price - change not present for all items though
    return prices_dict


if __name__ == '__main__':
    app.run(debug=True)
