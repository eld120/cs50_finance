from functools import total_ordering
import os
from objects import Customer, Stock
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, usd, lookup
from functions import key_checker

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

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


#processes user's data from DB into memory for all pages


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    users = db.execute("SELECT * FROM users   WHERE id = :id", id=session["user_id"])
    data = db.execute("SELECT * FROM data WHERE userid = :id", id=session["user_id"])
    
    user_session = Customer(users[0]["id"] , users[0]["cash"] )
    today_stock = []
    external = {}
    
    #only attempt to parse if data is present
    if len(data) > 0:
        for row in data:
            user_session.add_symbol(Stock(row["symbol"], row["cost"], row["qty"]  ))
            if key_checker(external, row["symbol"]) == True:
                external[row['symbol']] = {
                    'qty': external[row['symbol']]['qty'] + int(row['qty']),
                    'cost': external[row['symbol']]["cost"] + row["cost"],
                    }
            else:
                external[row['symbol']] = {
                    'qty': row['qty'],
                    'cost': row['cost'],
                    }
        for stock in list(external):
            if external[stock]['qty'] == 0:
                del external[stock]
            else:
                external[stock]['today'] = lookup(stock)
            
    #handle cash in the server instead of reading from database
    cash_money = user_session.cash
        
    #iterate over stocks purchased in db, update cash on hand
    for stock in external:
        price_ea = float(external[stock]["cost"]) / int(external[stock]["qty"])
        cash_money = cash_money - external[stock]["cost"]
        
    #updated cash on hand with dollar sign
    cash_money = usd(cash_money)
    
            

    return render_template("portfolio.html", external = external , cash_money = cash_money, today_stock = today_stock)

@app.route("/bought", methods=["GET", "POST"])
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    users = db.execute("SELECT * FROM users   WHERE id = :id", id=session["user_id"])
    data = db.execute("SELECT * FROM data WHERE userid = :id", id=session["user_id"])
    
    user_session = Customer(users[0]["id"] , users[0]["cash"] )
    today_stock = []
    external = {}
    
    #only attempt to parse if data is present
    if len(data) > 0:
        for row in data:
            user_session.add_symbol(Stock(row["symbol"], row["cost"], row["qty"]  ))
                
            #check and add symbols to a dictionary for end user facing webpage
            if key_checker(external, row["symbol"]) == True:
                external[row['symbol']] = {
                    'qty': external[row['symbol']]['qty'] + int(row['qty']),
                    'cost': external[row['symbol']]["cost"] + row["cost"],
                    }
            else:
                external[row['symbol']] = {
                    'qty': row['qty'],
                    'cost': row['cost'],
                }
        #adds pricing to the dict - 
        for stock in list(external):
            if external[stock]['qty'] == 0:
                del external[stock]
            else:
                external[stock]['today'] = lookup(stock)
        #handle cash in the server instead of reading from database
        cash_money = user_session.cash
        
        #iterate over stocks purchased in db, update cash on hand
        for stock in external:
            price_ea = float(external[stock]["cost"]) / int(external[stock]["qty"])
            cash_money = cash_money - external[stock]["cost"]
        
        #updated cash on hand with dollar sign
        cash_money = usd(cash_money)

    
    if request.method == "POST":
        stock_symbol = lookup(request.form.get("symbol"))
        stock_price = stock_symbol["price"]
        stock_name = stock_symbol["name"]
        stock_qty = request.form.get("quantity")


        #checks for sufficient funds before database update
        #price = stock_price
        if (float(stock_price) * int(stock_qty)) > user_session.cash:
            return apology("FORBIDDEN! Insufficient Funds", 403)
        else:

            new_balance = user_session.get_balance() - (float(stock_price) * int(stock_qty))

        db.execute("INSERT INTO data (userid, symbol, qty, cost,  timestamp ) VALUES(:userid, :symbol, :qty, :cost, :timestamp  )", userid=session["user_id"], symbol = stock_symbol['symbol'], cost = stock_price, qty = stock_qty, timestamp = datetime.utcnow() )
   
        #let's keep the database static and simply calculate balance in the server
        
        #db.execute("UPDATE users SET (cash, WHERE, userid, equal, id) VALUES (:cash, :WHERE, :userid, :equal, :id)", cash = new_balance ,WHERE = 'WHERE', userid = 'id', equal = '=', id=session["user_id"])
        


        return render_template("bought.html", stock_symbol = stock_symbol, stock_price = stock_price, stock_qty = stock_qty )
    else:
        #return render_template("test.html", use_sess = use_sess, user_session = user_session, cash_money = cash_money )
        return render_template("buy.html", external = external , cash_money = cash_money )

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    users = db.execute("SELECT * FROM users   WHERE id = :id", id=session["user_id"])
    data = db.execute("SELECT * FROM data WHERE userid = :id", id=session["user_id"])
    

    history = []
    total_spent = 0
    user_session = Customer(users[0]["id"] , users[0]["cash"] )

    for line in data:
        stock_symbol = line['symbol']
        stock_qty = line['qty']
        stock_cost = line['cost']
        timestamp = line['timestamp']
        history.append(Stock(stock_symbol, stock_cost, stock_qty, timestamp))
        total_spent = total_spent + stock_cost

    cash_money = usd(float(user_session.cash) - float(total_spent))
    
    

    return render_template("history.html", history = history, cash_money = cash_money)


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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

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
@app.route("/quoted", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    users = db.execute("SELECT * FROM users   WHERE id = :id", id=session["user_id"])
    data = db.execute("SELECT * FROM data WHERE userid = :id", id=session["user_id"])
    
    user_session = Customer(users[0]["id"] , users[0]["cash"] )
    today_stock = []
    external = {}
    
    #only attempt to parse if data is present
    if len(data) > 0:
        for row in data:
                user_session.add_symbol(Stock(row["symbol"], row["cost"], row["qty"]  ))
                #today = lookup(row['symbol'])
                #today_stock.append(today)
                #check and add symbols to a dictionary for end user facing webpage
                
                if key_checker(external, row["symbol"]) == True:
                    external[row['symbol']] = {
                        'qty': external[row['symbol']]['qty'] + int(row['qty']),
                        'cost': external[row['symbol']]["cost"] + row["cost"],
                        
                        }
                else:
                    external[row['symbol']] = {
                        'qty': int(row['qty']),
                        'cost': row['cost'],
                        
                        }
        
        #handle cash in the server instead of reading from database
        cash_money = user_session.cash
        
        #iterate over stocks purchased in db, update cash on hand
        for stock in external:
            price_ea = float(external[stock]["cost"]) / int(external[stock]["qty"])
            cash_money = cash_money - external[stock]["cost"]
        
        #updated cash on hand with dollar sign
        cash_money = usd(cash_money)

    for stock in list(external):
        if external[stock]['qty'] == 0:
            del external[stock]
        else:
            external[stock]['today'] = lookup(stock)


    if request.method == "POST":
        stock_symbol = lookup(request.form.get("symbol"))
        stock_price = usd(stock_symbol["price"])
        stock_name = stock_symbol["name"]
        
        
        return render_template("quoted.html", stock_name = stock_symbol["name"], price = stock_price)
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    if request.method == "POST":
        
        username = request.form.get("username")
        #query database to see if username already exists
        rows = db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))

        #check if username is found in database
        if len(rows) == 1:
            if rows[0]["username"] == username:
                return apology("Username already exists LOL", 403)    
        elif len(rows) > 1:
            return apology("Duplicate usernames in database", 500)
        
        retype_password = request.form.get("confirmation")
        passswordss = request.form.get("password")
        usernamezzz = request.form.get("username")
        # Ensure username was submitted
        if not usernamezzz:
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not passswordss:
            return apology("must provide password", 403)       
        elif not passswordss == retype_password:
            return apology("your passwords must match", 403)
        
        #hash both passwords into a variable
        pw_hasher = generate_password_hash(passswordss, method='pbkdf2:sha256', salt_length=32)
        
        #submit new user into database
        db.execute("INSERT INTO users (username , hash , cash ) VALUES(:username, :hash, :cash)", username = request.form.get("username"), hash = pw_hasher, cash = 10000)

        #query for new user ID
        rows = db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))
        # set new user ID session
        session["user_id"] = rows[0]["id"]

        return render_template("portfolio.html")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    users = db.execute("SELECT * FROM users   WHERE id = :id", id=session["user_id"])
    data = db.execute("SELECT * FROM data WHERE userid = :id", id=session["user_id"])
    
    user_session = Customer(users[0]["id"] , users[0]["cash"] )
    #today_stock = []
    external = {}
    
    #only attempt to parse if data is present
    if len(data) > 0:
        for row in data:
            user_session.add_symbol(Stock(row["symbol"], row["cost"], row["qty"]  ))
            #today = lookup(row['symbol'])
            #today_stock.append(today)
            #check and add symbols to a dictionary for end user facing webpage
                
            if key_checker(external, row["symbol"]) == True:
                external[row['symbol']] = {
                    'qty': external[row['symbol']]['qty'] + int(row['qty']),
                    'cost': external[row['symbol']]["cost"] + row["cost"],
                    
                    }
            else:
                external[row['symbol']] = {
                    'qty': int(row['qty']),
                    'cost': row['cost'],
                    
                    }
        
    for stock in list(external):
        if external[stock]['qty'] == 0:
            del external[stock]
        else:
            external[stock]['today'] = lookup(stock)

    #handle cash in the server instead of reading from database
    cash_money = user_session.cash
        
    #iterate over stocks purchased in db, update cash on hand
    for stock in external:
        price_ea = float(external[stock]["cost"]) / int(external[stock]["qty"])
        cash_money = cash_money - external[stock]["cost"]
        
    #updated cash on hand with dollar sign
    cash_money = usd(cash_money)
    
    if request.method == "POST":
        stock_symbol = request.form.get("symbol")
        stock_qty = request.form.get("quantity")
        if key_checker(external, (stock_symbol) ) == False:
            return apology("you must hold this stock in your portfolio in order to sell", 403)
        elif int(stock_qty) > int(external[stock_symbol]['qty']):
            return apology("you can only sell as many holding as are in your portfolio", 403)


        stock_symbol = lookup(request.form.get("symbol"))
        stock_price = stock_symbol["price"]
        stock_name = stock_symbol["name"]
        

        
        db.execute("INSERT INTO data (userid, symbol, qty, cost, timestamp) VALUES (:userid, :symbol, :qty, :cost, :timestamp)", userid = session["user_id"], symbol = stock_symbol['symbol'], qty = (int(stock_qty) * -1), cost = (stock_price * -1), timestamp = datetime.utcnow() )

        #remove stocks that are qty 0
        


        return render_template("sell.html",  external = external, cash_money = cash_money )
    return render_template("sell.html",  external = external, cash_money = cash_money )


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
