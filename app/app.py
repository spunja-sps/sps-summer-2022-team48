from flask import Flask, render_template, request
import json
import urllib

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template("index.html")

@app.route('/config')
def config_page():
    return render_template("config.html")

@app.route('/data-summary/', methods=['POST'])
def data_summary_page():
    watchlist = request.form.getlist("itemDropdown")
    # print(watchlist)
    get_prices(watchlist)
    return render_template("data_summary.html")
def get_prices(list):
    api_codes = {
        "Corn": "TFGRAIN/CORN",
        "Dairy": "CHRIS/CME_DA1",
    }
    for item in list:
        url = "https://data.nasdaq.com/api/v3/datasets/" + api_codes[item] + "?api_key=7PvJ27fqD-s1fgvKWZgk"
        response =  urllib.urlopen(url)
        data = response.read()
        dict = json.loads(data)
        print(dict["dataset"]["data"][0][1])


if __name__ == '__main__':
    app.run(debug=True)
