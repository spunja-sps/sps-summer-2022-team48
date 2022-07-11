from flask import Flask, render_template
import json
import urllib

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template("index.html")

@app.route('/config')
def config_page():
    return render_template("config.html")

@app.route('/data-summary/')
def data_summary_page():
    return render_template("data_summary.html")

@app.route("/prices")
def get_prices_list():
    url = "https://data.nasdaq.com/api/v3/datasets/ODA/PSHRI_USD"
    response =  urllib.urlopen(url)
    prices = response.read()
    dict = json.loads(prices)
    print(dict["dataset"]["data"][0])
    return render_template ("prices.html", prices=dict["dataset"]["data"])

    # prices = []
    # for prices in dict["results"]:
    #     price = {
    #         "value": price["value"],
    #         "data": price["data"],
    #     }
        
    #     prices.append(prices)

    # return {"results": prices}