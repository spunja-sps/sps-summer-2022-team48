from flask import Flask, render_template, request

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

    print(watchlist)

    return render_template("data_summary.html")

if __name__ == '__main__':
    app.run(debug=True)