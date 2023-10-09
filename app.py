import os
import sqlalchemy
# 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

# from library50 import cs50
# to clear terminal use cls command.
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
# To get the date and time of buying/selling of shares
import datetime

from helpers import apology, login_required, lookup, usd

#history means to show at what price u bought the stocks so dont't change the the of price to latest price.
# # added later
# import urlparse
# import psycopg2
# urlparse.uses_netloc.append("postgres")
# url = urlparse.urlparse(os.environ["DATABASE_URL"])
# conn = psycopg2.connect(
#  database=url.path[1:],
#  user=url.username,
#  password=url.password,
#  host=url.hostname,
#  port=url.port
# )
# till here

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
# db = SQL("postgres://ufjsfevhqhfgnp:670931fd29c0d5a908b3e78a6b0bfe85f52de901f06e8f2e3f08bb732335a058@ec2-52-71-23-11.compute-1.amazonaws.com:5432/d4qmbdoq8c1ihv")

# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# the answer is coming wrong since this function is executing at the start of the webapp and thus updating the values which are already stored is sql. But recent add values are not accessible by this route..   so here we need to change the path of the this route.
@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # current user's ID
    user_id = session.get("user_id")

    # symbol of each shares the user is holding
    total_symbol = db.execute("SELECT symbol FROM shares GROUP BY symbol HAVING id = ?", user_id)
    # looping over all the values of list of dict in total_symbol to get symbol and its current value
    # Create new column to store the latest price of product and then updating its values.
    for i in range(len(total_symbol)):
        for key, value in total_symbol[i].items():
            db.execute("UPDATE shares SET latest_price = ?, name = ? WHERE symbol = ?", lookup(value)["price"], lookup(value)["name"], value)

    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    shares = db.execute("SELECT SUM(share), latest_price, name, price, symbol FROM shares GROUP BY symbol HAVING ID = ?", user_id)
    # stocks owned, number of shares, current price of each stock, name, full name.

    sum = cash[0]["cash"]
    # finding grand sum
    for share in shares:
        sum += share["SUM(share)"] * share["latest_price"]

    # HAVING is used with GROUP BY, whereas WHERE is used without GROUP BY
    return render_template("index.html", cash = cash, shares = shares, sum = sum)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # If the path is post
    if request.method == "POST":

        # Variables storing data
        symbol = request.form.get("symbol")
        # shares = int(request.form.get("shares")) # this step is very necessary. to type cast the value obtained into integer. --1)

        # Checking whether user typed symbol
        if not request.form.get("symbol"):
            return apology("Missing Symbol", 400)

        # Checking whether symbol is valid
        elif lookup(symbol) == None:
            return apology("Invalid Symbol", 400)

        # even though you think that the form can handle the case of submitting non negative integer value but the hacker can hack this so it is best to handle such cases ....so if hacker even wants to hack he can't.
        # elif type(request.form.get("shares")) != int:
        #     return apology("Invalid shares", 400)

        # ---------------------------------------------------------- THIS IS THE STEP WHERE I STUCK ------------------------------------------------------------
        # checking whether shares is int or not using try and except case
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Invalid Shares", 400)

        if shares <= 0:
            return apology("Invalid shares", 400)

        # Checking whether user typed number of shares
        elif not request.form.get("shares"):
            return apology("Missing Shares", 400)

        # elif type(request.form.get("shares")) != int: # this line of code is doint something bad
        #     return apology("Invalid shares", 400)

        elif shares <= 0:
            return apology("Invalid shares", 400)

        # Variables storing data In table about the shares
        user_id = session.get("user_id")
        # easy to eccess user_id then the name of the person since different person can have different name
        price = lookup(symbol)["price"]
        day = datetime.datetime.now()
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        # '>' not supported between instances of 'list' and 'float'
        # If str is a SELECT, then execute returns a list of zero or more dict objects, inside of which are keys and values representing a table’s fields and cells, respectively.
        # db.execute("CREATE TABLE shares (id INTEGER NOT NULL, day NUMERIC NOT NULL, symbol TEXT NOT NULL, share NUMERIC NOT NULL, price NUMERIC NOT NULL, FOREIGN KEY(id) REFERENCES users(id))")
        current_cash = float(cash[0]["cash"]) - (float(price) * float(shares))
        if current_cash >= 0:
            db.execute("UPDATE users SET cash = ? WHERE id = ?", current_cash, user_id)
            db.execute("INSERT INTO shares(id, day, symbol, share, price, latest_price) VALUES(?, ?, ?, ?, ?, ?)", user_id, day, symbol, shares, price, price) # price here means price per share and is in dollars.

        else:
            return apology("Can't Afford", 400)

        flash("Bought!")     # -------------------function to flash on the top that you bought the stocks!!!---------------------------------------
        # return render_template(" ", lookup = lookup(symbol), shares = shares)
        return index()

    # If the path is get
    # return render_template("index.html", lookup = lookup(symbol), shares = shares)

    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session.get("user_id")
    shares = db.execute("SELECT symbol, share, price, day FROM shares WHERE id = ?", user_id)

    return render_template("history.html", shares = shares)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

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

    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not request.form.get("symbol"):
            return apology("Missing Symbol", 400)
        elif lookup(symbol) == None:
            return apology("Invalid Symbol", 400)
        return render_template("quoted.html", lookup = lookup(symbol))

    # symbol = request.form.get("symbol")
    return render_template("quote.html")

    # check staffs solution
    # also check staffs solution for hash function lecture 5

@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """Add cash."""

    if request.method == "POST":

        new_cash = int(request.form.get("add_cash"))
        user_id = session.get("user_id")
        if not request.form.get("add_cash"):
            return apology("Missing Cash", 400)

        elif new_cash < 0:
            return apology("Invalid Cash", 400)

        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        current_cash = float(cash[0]["cash"]) + float(new_cash)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", current_cash, user_id)
        return redirect("/")

    # symbol = request.form.get("symbol")
    return render_template("Add_cash.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure unique password
        user = db.execute("SELECT username FROM users WHERE username = ?", request.form.get("username"))
        # if not user: it will give wrong answer -- every data query will pass this condition
        if len(user) != 0:
            return apology("Username already exists", 400)

        elif len(request.form.get("password")) < 3:
            return apology("Please enter password having 3 or more characters", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure both password matches
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Please enter same password", 400)

        # Remember which user has registered
        session["user_id"] = request.form.get("id")

        # Inserting new data in table
        db.execute("INSERT INTO users(username, hash) values(?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html") # if I directly get to this via changing the URL then Page register.html will open.



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # shares = db.execute("SELECT SUM(share) FROM shares WHERE id = ? GROUP BY symbol HAVING symbol = ?", user_id, symbol) -- THIS WON"T work here cause this statement required values that are submitted later via post query.
    user_id = session.get("user_id")
    symbols = db.execute("SELECT symbol FROM shares GROUP BY symbol HAVING id = ?", user_id)

    # POST
    if request.method == "POST":

        symbol = request.form.get("symbol")
        share = request.form.get("shares")
        shares = db.execute("SELECT SUM(share) FROM shares WHERE id = ? GROUP BY symbol HAVING symbol = ?", user_id, symbol)
        share_sell = -1 * int(share)
        price = lookup(symbol)["price"]
        day = datetime.datetime.now()
        name = lookup(symbol)["name"]

        if not request.form.get("symbol"):
            return apology("Missing Symbol", 400)

        elif int(share) - shares[0]["SUM(share)"] > 0:
            return apology("Too many shares", 400)

        # sell_share = db.execute("SELECT SUM(share), latest_price, name, symbol FROM shares GROUP BY symbol HAVING ID = ?", user_id)
        # inserting new row to update the values
        db.execute("INSERT INTO shares(id, day, symbol, share, latest_price, price, name) VALUES(?, ?, ?, ?, ?, ?, ?)", user_id, day, symbol, share_sell, price, price, name)
        sell_share = db.execute("SELECT SUM(share), latest_price, name, symbol, price FROM shares GROUP BY symbol HAVING ID = ?", user_id)

        # current cash
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        current_cash = cash[0]["cash"] - (share_sell * price)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", current_cash, user_id)
        new_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        # shortcut -- would have just updated the cash and redirect it to index or ("/")
        sum = current_cash
        # finding grand sum
        for shar_e in sell_share:
            sum += shar_e["SUM(share)"] * shar_e["latest_price"]

        flash("Sold!")   # --------------------------------function to flash a strip written on it sold that you sold the stock!!!------------------------------
        return render_template("index.html", shares = sell_share, sum = sum, cash = new_cash)

    # GET
    return render_template("sell.html", symbols = symbols)
    # if request.method == "POST":

# pk_1e93acf137424a61bc559476a2ca046e -- API Token
# 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 -- github

if __name__ == '__main__':
 app.debug = True
 port = int(os.environ.get("PORT", 5000))
 app.run(host='0.0.0.0', port=port)