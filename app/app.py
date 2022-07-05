from flask import Flask, render_template

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