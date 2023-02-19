import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Usage export API_KEY=value
# https://iexcloud.io/ register and get your API token, it starts with pk 
# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # get the user id
    user_id = session["user_id"]
    # get the stock_name, stock_symbol, share of that user
    # SQL note: When Sum is used in group by, the fields that are grouped data is summed.
    portfolio = db.execute(
        "SELECT stock_name, stock_symbol, SUM(share) AS n FROM purchases WHERE purchases_id = ? GROUP BY stock_symbol", user_id)
    # get the current cash of user
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    # now i need to put each stock symbol into lookup function, but i need to get the each symbol from the user owns
    # lets create an empty list
    assets = []
    total = 0
    for asset in portfolio:
        #get the symbol put it in lookup function to get a list of dictionary of that symbol so that i can achieve its name, price, and symbol
        lookedup = lookup(asset["stock_symbol"])
        assets.append({
            "name": lookedup["name"],
            "symbol": lookedup["symbol"],
            "share": asset["n"],
            "current_price": usd(lookedup["price"]),
            "total": usd(asset["n"] * lookedup["price"])
        })
        # add the total worth of each stock into total variable declined above for
        total += asset["n"] * lookedup["price"]
    # add users cash to total
    total = total + cash
    # return portfolio
    return render_template("index.html", assets=assets, cash=usd(cash), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    # POST method
    symbol = request.form.get("symbol").upper()
    shares = request.form.get("shares")
    # check the entered symbol, share
    lookedup = lookup(symbol)
    if not symbol:
        return apology("Missing Symbol", 400)
    if not shares:
        return apology("Missing Share", 400)
    if lookedup == None:
        return apology("Invalid Symbol", 400)
    if shares.isdigit() == False:
        return apology("Can only buy integer value", 400)
    # check the price of stock
    price = lookedup["price"]
    # calculate the cost of purchase
    cost = price * float(shares)
    # check if the user has enough money
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?",user_id)
    # data stored as a list of dict, which's only first row has data. Then get the value of cash key
    budget = user[0]["cash"]
    # log the transaction
    # get the name of stock
    stock_name = lookedup["name"]
    # get the current date (import datetime)
    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    # create a table in DB to keep track of:
    # --->who purchased(username), what is purchased(stock_name) and (stock_symbol), how many (shares), how much the 1 share's price was(price_payed), when(transacted)
    db.execute(
        "CREATE TABLE IF NOT EXISTS purchases (id INTEGER PRIMARY KEY AUTOINCREMENT, purchases_id INTEGER,stock_name TEXT, stock_symbol TEXT, share NUMERIC, price_payed, time TEXT, FOREIGN KEY(purchases_id) REFERENCES users(id));")
    db.execute(
        "CREATE INDEX IF NOT EXISTS purchases_id ON purchases (purchases_id);")
    if cost <= budget:
        updated_budget = budget - cost
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?", updated_budget, user_id)
        db.execute(
            "INSERT INTO purchases (purchases_id, stock_name, stock_symbol, share, price_payed, time) VALUES (?,?,?,?,?,?)",
                user_id, stock_name, symbol, shares, price, today)
    else:
        return apology("Can't afford", 400)
    flash(f"{shares} share(s) of {stock_name} ({symbol}) has been succefully bought!")
    return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    portfolio = db.execute("SELECT * FROM purchases WHERE purchases_id = ?", user_id)
    return render_template("history.html", portfolios=portfolio)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    # if request.method is post
    # get the symbol from the form
    symbol = request.form.get("symbol")
    # get the JSON
    lookedup = lookup(symbol)
    # check the symbol
    if lookup(symbol) == None:
        return apology("Invalid symbol", 400)
    return render_template("quoted.html", quotes=lookedup)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # check if the name is entered
        if not name or len(name) == 0:
            return apology("Username must be entered", 400)
        # check if the password is entered
        if not password or len(password) == 0:
            return apology("Password must be entered", 400)
        # check if the paswords match
        if password != confirmation:
            return apology("Passwords do not match", 400)

        # get the name of registered users: SELECT returns list of (zero or more) dict objects PER DOCUMENT
        registered = db.execute("SELECT * FROM users WHERE username = ?", name)
        if registered:
            return apology("Username is taken", 400)
        # generate hash
        hash = generate_password_hash(password)
        # insert the name into DB
        db.execute("INSERT INTO users (username, hash) VALUES (?,?)", name, hash)
        # assign session to the user
        session["name"] = name
        return redirect("/login")
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # find the user, get their stocks (if any)
    user_id = session["user_id"]
    portfolio = db.execute(
        "SELECT stock_name, stock_symbol,SUM(share) as n FROM purchases WHERE purchases_id = ? GROUP BY stock_symbol", user_id)
    if request.method == "GET":
        return render_template("sell.html", portfolios=portfolio)
    # POST
    # get the symbol of what user sold
    symbol = request.form.get("symbol").upper()
    # if symbol is not selected,raise an error
    if not symbol:
        return apology("missing symbol", 400)
    # check the share amount that user want to sell
    share = int(request.form.get("shares"))
    if share < 0:
        return apology("can't buy negative shares :(", 400)
    # check if user has enough shares
    shares = int(portfolio[0]["n"])
    if share > shares:
        return apology("You can't sell more shares than you have", 400)
    # check the price of symbol
    price = lookup(symbol)["price"]
    # get the name of the stock
    stock = lookup(symbol)["name"]
    # the total value of stock *share
    earned = float(share * price)
    # get the user's current cash
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    # updated user balance
    updated_cash = earned + cash
    # get the current date (import datetime)
    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    # insert it negative share to purchases
    db.execute(
        "INSERT INTO purchases (purchases_id, stock_name, stock_symbol, share, price_payed, time) VALUES (?,?,?,?,?,?)",
            user_id, stock, symbol, -abs(share), price, today)
    # update user's cash
    db.execute("UPDATE users SET cash = ?",updated_cash)
    flash(f"{share} share(s) of {stock} ({symbol}) has been succefully sold")
    return redirect("/")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "GET":
        return render_template("settings.html")
    # post
    user_id = session["user_id"]
    # get the current passwordn entered pw, check if it's indeed thier pw
    current_pw = db.execute("SELECT hash FROM users WHERE id = ?", user_id)[0]["hash"]
    old_pw = request.form.get("old_pw")
    if not check_password_hash(current_pw, old_pw):
        return apology("Wrong Current Password", 400)
    # get the new pw twice, check if entered correctly
    new_pw = request.form.get("new_pw")
    confirm_pw = request.form.get("confirm_pw")
    if new_pw!= confirm_pw:
        return apology("New Passwords does not match", 400)
    # check if user enters an empty input
    if not old_pw or not new_pw or not confirm_pw:
        return apology("Missing fields", 400)
    # update the pw with the new pw
    new_hash = generate_password_hash(new_pw)
    db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, user_id)
    flash("Password has been succcesfully changed!")
    return redirect("/")