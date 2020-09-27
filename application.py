import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd


import sys

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Set API key
os.environ["API_KEY"] = "pk_bb9e227ccfea42b190b016abc27f7996"

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Define variables for user entered values
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

        # Check if username exists
        if len(rows) != 0:
            return apology("username already exists", 403)

        # Check if username has required conditions
        if len(username) < 3:
            return apology("username must be at least 3 characters", 403)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 403)

        # Ensure confirmation was submitted
        if not confirmation:
            return apology("must re-enter password", 403)

        # Ensure password and confirmation match
        if password != confirmation:
            return apology("password must match", 403)

        # Check if password has required conditions
        if check_pswd(password):
            return apology("""password must be at least 8 characters with 1 lowercase letter,
                1 uppercase letter, and 1 digit/special character""", 403)

        # Hash password
        hashed_password = generate_password_hash(password)

        # Insert new user into users table in database
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)", username=username, password=hashed_password)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

def check_pswd(password):
    return len(password) < 8 or not has_lower(password) or not has_upper(password) or (not has_numbers(password) and not has_special_char(password))

def has_numbers(password):
    return any(char.isdigit() for char in password)

def has_special_char(password):
    return any(char.isalnum() for char in password)

def has_lower(password):
    return any(char.islower() for char in password)

def has_upper(password):
    return any(char.isupper() for char in password)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

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


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Get stocks data for user
    user_id = session["user_id"]
    user_stocks = db.execute("SELECT symbol, shares FROM holdings WHERE user_id=:user_id", user_id=user_id)

    print(user_stocks)

    stocks_data = []
    total = 0

    for stock in user_stocks:
        data = []
        symbol = stock.get("symbol")

        data.append(symbol)
        data.append(lookup(symbol).get("name"))

        shares = stock.get("shares")
        data.append(shares)

        price = lookup(symbol).get("price")
        data.append(usd(price))

        total_stock = price * shares
        data.append(usd(total_stock))
        total += total_stock

        stocks_data.append(data)

    # Get cash and total values for user
    cash = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=user_id)
    cash = cash[0].get("cash")
    total += cash
    cash = usd(cash)
    total = usd(total)

    # Display table
    return render_template("index_quote.html", stocks_data=stocks_data, cash=cash, total=total)


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Define variable for user entered value
        symbol = request.form.get("symbol")

        # Ensure symbol was submitted
        if not symbol:
            return apology("must provide symbol", 403)

        # Check if symbol is upper case
        if not symbol.isupper():
            return apology("symbol must be uppercase", 403)

        # Get quote using symbol
        quote = lookup(symbol)

        # Check if valid symbol
        if not quote:
            return apology("incorrect symbol", 403)

        # Display stock info to user
        price = usd(quote.get("price"))
        return render_template("quoted.html", quote=quote, price=price)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Define variables for user entered values
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Ensure symbol was submitted
        if not symbol:
            return apology("must provide symbol", 403)

        # Check if symbol is upper case
        if not symbol.isupper():
            return apology("symbol must be uppercase", 403)

        # Get quote using symbol
        quote = lookup(symbol)

        # Check if valid symbol
        if not quote:
            return apology("incorrect symbol", 403)

        # Ensure shares was submitted
        if not shares:
            return apology("must provide number of shares", 403)

        # Check if valid number of shares
        shares = int(shares)
        if shares <= 0:
            return apology("incorrect number of shares", 403)

        # Calculate remaining balance
        user_id = session["user_id"]
        price = float(quote.get("price"))
        amount = shares * price
        cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=user_id)
        cash = float(cash[0].get("cash"))
        balance = cash - amount
        if balance <= 0:
            return apology("not enough cash to buy shares", 403)

        # Update cash of user
        db.execute("UPDATE users SET cash = :balance WHERE id = :user_id", balance=balance, user_id=user_id)

        # Update transactions table with new buy user info
        price = usd(price)
        db.execute("""INSERT INTO transactions (user_id, symbol, shares, price)
            VALUES (:user_id, :symbol, :shares, :price)""",
            user_id=user_id, symbol=symbol, shares=shares, price=price)

        # Update holdings table with new buy user info
        holdings = db.execute("SELECT shares FROM holdings WHERE user_id=:user_id AND symbol=:symbol", user_id=user_id, symbol=symbol)
        if not holdings:
            db.execute("INSERT INTO holdings (user_id, symbol, shares) VALUES (:user_id, :symbol, :shares)",
                user_id=user_id, symbol=symbol, shares=shares)
        else:
            share_holdings = shares + holdings[0].get("shares")
            db.execute("UPDATE holdings SET shares=:share_holdings WHERE user_id=:user_id AND symbol=:symbol",
                share_holdings=share_holdings, user_id=user_id, symbol=symbol)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    user_id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Define variables for user entered values
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Ensure symbol was submitted
        if not symbol:
            return apology("must provide symbol", 403)

        # Check if symbol is upper case
        if not symbol.isupper():
            return apology("must provide symbol", 403)

        # Get quote using symbol
        quote = lookup(symbol)

        # Check if valid symbol
        if not quote:
            return apology("incorrect symbol", 403)

        # Ensure shares was submitted
        if not shares:
            return apology("must provide number of shares", 403)

        # Check if valid number of shares
        shares = int(shares)
        if shares <= 0:
            return apology("incorrect number of shares", 403)

        # Check if user has enough shares
        holdings = db.execute("SELECT shares FROM holdings WHERE user_id = :user_id AND symbol=:symbol", user_id=user_id, symbol=symbol)
        if not holdings:
            return apology("not enough share holdings", 403)
        share_holdings = holdings[0].get("shares")
        print("share_holdings = " + str(share_holdings))
        print("shares = " + str(shares))
        if share_holdings < shares:
            return apology("not enough share holdings", 403)

        # Calculate remaining balance
        price = float(quote.get("price"))
        amount = shares * price
        cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=user_id)
        cash = float(cash[0].get("cash"))
        balance = cash + amount

        # Update cash of user
        db.execute("UPDATE users SET cash = :balance WHERE id = :user_id", balance=balance, user_id=user_id)

        # Update transactions table with new sell user info
        price = usd(price)
        shares *= -1
        db.execute("""INSERT INTO transactions (user_id, symbol, shares, price)
            VALUES (:user_id, :symbol, :shares, :price)""",
            user_id=user_id, symbol=symbol, shares=shares, price=price)

        # Update holdings table with new sell user info
        share_holdings += shares
        if share_holdings == 0:
            db.execute("DELETE FROM holdings WHERE user_id=:user_id AND symbol=:symbol",user_id=user_id, symbol=symbol)
        else:
            db.execute("UPDATE holdings SET shares=:share_holdings WHERE user_id=:user_id AND symbol=:symbol",
                share_holdings=share_holdings, user_id=user_id, symbol=symbol)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get available sell options from database
        symbols = db.execute("SELECT symbol FROM transactions WHERE user_id=:user_id", user_id=user_id)
        symbols_list = []
        for symbol_dict in symbols:
            symbols_list.append(symbol_dict["symbol"])
        symbols = list(dict.fromkeys(symbols_list))

        return render_template("sell.html", symbols=symbols)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Get user data
    user_id = session["user_id"]
    stock_data = db.execute("SELECT timestamp, symbol, shares, price FROM transactions WHERE user_id=:user_id", user_id=user_id)
    user_data = []
    for stock in stock_data:
        data = []
        data.append(stock.get("timestamp"))
        data.append(stock.get("symbol"))
        data.append(lookup(stock.get("symbol")).get("name"))
        data.append(stock.get("shares"))
        data.append(stock.get("price"))
        user_data.append(data)

    # Display table to user
    return render_template("history.html", user_data=user_data)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)