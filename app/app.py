
from cgi import print_exception
from flask import Flask, render_template, request, session,url_for, redirect
from flask_session import Session
import json
import requests
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import json
import urllib


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '123'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

Session(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

###################################
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')
###################################


@app.route('/')
def welcome():
    session["is_logged_in"] = False
    return render_template("index.html")


@app.route('/info')
def info():
    return render_template("info.html")

@app.route('/error')
def error():
    return render_template("error.html")

@app.route('/config')
def config_page():
    is_logged_in = session.get("is_logged_in")
        
    return render_template("config.html", is_logged_in=is_logged_in)


@app.route('/data-summary', methods=['GET', 'POST'])
def data_summary_page():
    watchlist = request.form.getlist("itemDropdown")

    # if coming from configuration, save dropdown items to session
    if watchlist:
        session["watchlist"] = watchlist
    # if coming from graphing page, reset watchlist var from session
    else:
        watchlist = session.get("watchlist")

    prices_dict = get_monthly_price_change(watchlist)

    return render_template("data_summary.html", prices_dict=prices_dict)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                session["is_logged_in"] = True
                print("hello")
                return render_template("config.html", is_logged_in=True)
            else:
                return redirect(url_for("error"))
        else:
            return  redirect(url_for("error"))
    return render_template('login.html', form=form)



@app.route('/logout', methods=['GET', 'POST']) # add this s
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/graphing', methods=['GET', 'POST'])
def detailed_data_page():
    selected_item = request.args.get('item')
    print(selected_item)

    watchlist = session.get("watchlist")
    print(watchlist)

    prices_dict, api_code = get_time_series_prices(selected_item)
    labels, data = parse_data_for_graph(prices_dict, api_code)

    print(labels)
    print(data)

    return render_template("data_detailed.html", item=selected_item, labels=labels, values=data)

    # Keep for now just in case
    # dummy_data = [
    #     (1, 5),
    #     (2, 7),
    #     (3, 2),
    #     (4, 4),
    #     (5, 10)
    # ]

    # dummy_labels = [row[0] for row in dummy_data]
    # dummy_values = [row[1] for row in dummy_data]

    # return render_template("data_detailed.html", item=selected_item, labels=dummy_labels, values=dummy_values)


def make_call(url):
    response = requests.get(url)
    return response.json()


def get_monthly_price_change(list):
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
    lastMonthDate = get_date(today, 30)
    for item in list:
        url = "https://commodities-api.com/api/timeseries?access_key=aieqnpp3ftiys55nfp4c469m6h16tvlxfa3qpjy9m310pm0be64mo54k6pro&start_date=" + str(lastMonthDate) + "&end_date=" + str(yesterday) + "&symbols=" + \
            api_codes[item]
        response = requests.get(url)
        jsonResponse = response.json()
        print(jsonResponse)
        price_yesterday = 1 / \
            jsonResponse["data"]["rates"][str(yesterday)][api_codes[item]]
        price_at_date = 1 / \
            jsonResponse["data"]["rates"][str(lastMonthDate)][api_codes[item]]
        price_units = jsonResponse["data"]["unit"]

        prices_dict[item] = [round(price_yesterday, 3),
                             round(get_change(price_yesterday, price_at_date), 3), price_units]
    return prices_dict


def get_time_series_prices(item):
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
    lastMonthDate = get_date(today, 30)

    url = "https://commodities-api.com/api/timeseries?access_key=aieqnpp3ftiys55nfp4c469m6h16tvlxfa3qpjy9m310pm0be64mo54k6pro&start_date=" + str(lastMonthDate) + "&end_date=" + str(yesterday) + "&symbols=" + \
        api_codes[item]
    response = requests.get(url)
    jsonResponse = response.json()
    print(jsonResponse)
    prices_dict = jsonResponse["data"]["rates"]

    return prices_dict, api_codes[item]


def parse_data_for_graph(prices_dict, api_code):
    labels = []
    data = []

    for date in prices_dict:
        labels.append(date)
        data.append(1 / prices_dict[date][api_code])

    return labels, data


def get_date(today, numberOfDays):
    # returns the date at numberOfDays going back from today
    # ex) if numberOfDays = 7, returns last week's date
    return (today - timedelta(numberOfDays)).date()


def get_change(price_today, price_at_date):
    # returns % change
    return ((price_today - price_at_date)/price_at_date) * 100


if __name__ == '__main__':
    app.run(debug=True)
