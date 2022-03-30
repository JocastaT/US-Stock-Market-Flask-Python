
from locale import currency
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import plotly.graph_objects as go
import pandas
import requests, json, csv
import yfinance as yf
import pandas as pd
import plotly
import plotly.express as px
from flaskext.mysql import MySQL
import pymysql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField
from passlib.hash import sha256_crypt
from datetime import datetime
from flask_mail import Message
from flask_mail import Mail
from functools import wraps
import uuid

app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'testing46011@gmail.com'
app.config['MAIL_PASSWORD'] = 'TESTING46011'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'e61e60d76ad720cfac820eec8774a84a'

# client_id and client_secret detmails are from the FIDOR portal.
client_id = "e97c1f5cd767f0da"
client_secret = "e61e60d76ad720cfac820eec8774a84a"

authorization_base_url = 'https://apm.tp.sandbox.fidorfzco.com/oauth/authorize'
token_url = 'https://apm.tp.sandbox.fidorfzco.com/oauth/token'
redirect_uri = 'http://localhost:5000/callback'

# MySQL configurations
mysql = MySQL() 
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'test'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)



# Article Form Class
class ArticleForm(Form):
    symbol = StringField('Symbol', [validators.Length(min=1, max=200)])
    stocksNo = IntegerField('No. of Stocks', [validators.Length(min=1)])
    marketPrice = IntegerField('Market Price', [validators.Length(min=1, max=200)])
    totalAmt = IntegerField('Total Amount', [validators.Length(min=1)])
    date = StringField('Date', [validators.Length(min=1)])

# Article Form Class
class Fav(Form):
    symbol = StringField('Symbol', [validators.Length(min=1, max=200)])

# home page
@app.route('/', methods=["GET"])
@app.route('/index', methods=["GET"])
def default():

    try:
        #Step 1: User Application Authorization    
        #sending authorization client ID and client Secret to Fidor for authorization
        fidor = OAuth2Session(client_id,redirect_uri=redirect_uri)
        authorization_url, state = fidor.authorization_url(authorization_base_url)
        # State is used to prevent CSRF, keep this for later.
        session['oauth_state'] = state
        print("authorization URL is =" +authorization_url)
        return redirect(authorization_url)
    except KeyError:
        print("Key error in default-to return back to index")
        return redirect(authorization_url)

@app.route("/callback", methods=["GET"])
def callback():
    
        #Step 2: Retrieving an access token.
        #The user has been redirected back from the provider to your registered
        #callback URL. With this redirection comes an authorization code included
        #in the redirect URL. We will use that to obtain an access token.
        fidor = OAuth2Session(state=session['oauth_state'])
        authorizationCode = request.args.get('code')
        body = 'grant_type="authorization_code&code='+authorizationCode+ \
        '&redirect_uri='+redirect_uri+'&client_id='+client_id
        auth = HTTPBasicAuth(client_id, client_secret)
        token = fidor.fetch_token(token_url,auth=auth,code=authorizationCode,body=body,method='POST')

        # At this point you can fetch protected resources but lets save
        # the token and show how this is done from a persisted token
        session['oauth_token'] = token
        return redirect(url_for('.services'))

#get user
@app.route("/home", methods=["GET"])
def services():
    #Fetching a protected resource using an OAuth 2 token.
    try:
        token =  session['oauth_token']  
        url = "https://api.tp.sandbox.fidorfzco.com/accounts"

        payload = ""
        headers = {
            'Accept': "application/vnd.fidor.de;version=1;text/json",
            'Authorization': "Bearer "+token["access_token"]
            }

        response = requests.request("GET", url, data=payload, headers=headers)
        print("services=" + response.text)
        customersAccount = json.loads(response.text)
        customerDetails = customersAccount['data'][0]
        customerInformation = customerDetails['customers'][0] 
        session['fidor_customer'] = customersAccount

        return render_template('menu.html',fID=customerInformation["id"],
                fFirstName=customerInformation["first_name"],fLastName=customerInformation["last_name"],
                fAccountNo=customerDetails["account_number"],fBalance=(customerDetails["balance"]/100))
    except KeyError:
            print("Key error in services-to return back to index")
            return redirect(url_for('default'))

#profile page
@app.route("/profile", methods=["GET"])
def profile():
    
        token =  session['oauth_token']  
        url = "https://api.tp.sandbox.fidorfzco.com/accounts"

        payload = "https://api.tp.sandbox.fidorfzco.com/accounts"
        headers = {
            'Accept': "application/vnd.fidor.de;version=1;text/json",
            'Authorization': "Bearer "+token["access_token"]
            }

        response = requests.request("GET", url, data=payload, headers=headers)
        print("services=" + response.text)
        customerData = json.loads(response.text)
        accountInformation = customerData['data'][0]
        customerInformation = accountInformation['customers'][0] 
        fFirstName=customerInformation['first_name']
        fLastName=customerInformation['last_name']


        return render_template('profile.html',fFirstName=fFirstName,
                fLastName=fLastName,accountInformation=accountInformation, customerInformation=customerInformation)
    
#get historys
@app.route("/transactions", methods=["GET"])
def transactions():
    #Fetching a protected resource using an OAuth 2 token.
    try:
        token =  session['oauth_token']  
        url = "https://api.tp.sandbox.fidorfzco.com/transactions"

        payload = ""
        headers = {
            'Accept': "application/vnd.fidor.de;version=1;text/json",
            'Authorization': "Bearer "+token["access_token"]
            }

        response = requests.request("GET", url, data=payload, headers=headers)
        print("transactions=" + response.text)
        customersAccount = json.loads(response.text)
        
        customerDetails = customersAccount['data']
        #customerInformation = customerDetails['transaction_type_details']["remote_name"] 
        customersItem = session['fidor_customer'] 
        customersItem = customersItem['data'][0]
        fFirstName = customersItem['customers'][0]['first_name']
        fLastName = customersItem['customers'][0]['last_name']

        
        return render_template('history.html',customerDetails= customerDetails,fFirstName=fFirstName,fLastName=fLastName)

    except KeyError:
        print("Key error in services-to return back to index")
        return redirect(url_for('default'))

@app.route("/rsi/<string:symbol>/transfer", methods=["GET"])
def transfer(symbol):
    try:

        customersAccount = session['fidor_customer']
        customerDetails = customersAccount['data'][0]
        refNo = str(uuid.uuid4())
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        # Get article
        result = cur.execute("SELECT * FROM stocklist WHERE symbol = %s", [symbol])
        stock = cur.fetchone()
        return render_template('internal_trf.html',fFIDORID=customerDetails["id"],
            fAccountNo=customerDetails["account_number"],fBalance=(customerDetails["balance"]/100),stock=stock,refNo=refNo)

    except KeyError:
        print("Key error in bank_transfer-to return back to index")
        return redirect(url_for('.index'))

#making trf from user acc
@app.route("/rsi/<string:symbol>/process", methods=["POST"])
def process(symbol):
    if request.method == "POST":
        token =  session['oauth_token']         
        customersAccount = session['fidor_customer']
        customerDetails = customersAccount['data'][0]
        customerInformation = customerDetails['customers'][0]

        fidorID = customerDetails['id']
        custEmail = 'studentC05@email.com'
        totalAmt = int(float(request.form['totalAmt'])*100)
        symbol = request.form['stock']
        subject = request.form['subject']
        currency = request.form['currency']
        transactionID = request.form['transactionID']
        stockNo = request.form['stockNo']
        sendEmail = request.form['email']
        marketPrice = request.form['regularMarketPrice']
        date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        url = "https://api.tp.sandbox.fidorfzco.com/internal_transfers"

        payload = "{\n\t\"account_id\": \""+fidorID+"\",\n\t\"receiver\": \""+ \
                custEmail+"\",\n\t\"external_uid\": \""+transactionID+"\",\n\t\"amount\": "+ \
                str(totalAmt)+",\n\t\"subject\": \""+subject+"\",\n\t\"currency\": \""+currency+"\"\n}\n"

        headers = {
            'Accept': "application/vnd.fidor.de; version=1,text/json",
            'Authorization': "Bearer "+token["access_token"],
            'Content-Type': "application/json"
            }

        response = requests.request("POST", url, data=payload, headers=headers)

        print("process="+response.text)

        transactionDetails = json.loads(response.text)
          
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        result = cur.execute("SELECT * FROM stocklist WHERE symbol = %s", [symbol])
        stock = cur.fetchone()
        # Execute
        cur.execute("INSERT INTO stocks(symbol, stocksNo, marketPrice, totalAmt, date, user) VALUES(%s, %s, %s,%s, %s, %s)",(symbol, stockNo, marketPrice, totalAmt, date, session['email']))
        # Commit to DB
        conn.commit()
        #Close connection
        msg = Message('Purchase of US Stocks', sender = 'testing46011@gmail.com', recipients = [sendEmail])
        msg.html = render_template('sent.html',fTransactionID=transactionDetails["id"],createdTime = transactionDetails['created_at'],famount=(float(transactionDetails["amount"])/100))
        mail.send(msg)

        
        cur.close()

        flash('Receipt has been sent to your email', 'success')
    
        return redirect(url_for('dashboard'))

   

# Stocks
@app.route('/stocks')
def stocks():
    
    # Create cursor
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
  
    # Get articles
    result = cur.execute("SELECT * FROM stocklist ")
    stocks = cur.fetchall()
    if result > 0:
        return render_template('stocks.html', stocks=stocks)
    else:
        msg = 'No stocks Found'
        return render_template('stocks.html', msg=msg)
    # Close connection
    cur.close()
    return render_template('stocks.html')

#Single Article
@app.route('/rsi/<string:symbol>/')
def stock(symbol):
    # Create cursor
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
  
    # Get article
    result = cur.execute("SELECT * FROM stocklist WHERE symbol = %s", [symbol])
    stock = cur.fetchone()

   
    

    return render_template('rsi.html', stock=stock)



@app.route('/rsi')
def index():

    return render_template('rsi.html')

@app.route('/callback/<endpoint>')
def cb(endpoint):   
    if endpoint == "getStock":
        return gm(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
    elif endpoint == "getInfo":
        stock = request.args.get('data')
        st = yf.Ticker(stock)
        return json.dumps(st.info)
    else:
        return "Bad endpoint", 400

# Return the JSON data for the Plotly graph
def gm(stock,period, interval):
    st = yf.Ticker(stock)
  
    # Create a line graph
    df = st.history(period=(period), interval=interval)
    df=df.reset_index()
    df.columns = ['Date-Time']+list(df.columns[1:])
    max = (df['Open'].max())
    min = (df['Open'].min())
    range = max - min
    margin = range * 0.05
    max = max + margin
    min = min - margin
    fig = px.area(df, x='Date-Time', y="Open",
        hover_data=("Open","Close","Volume"), 
        range_y=(min,max), template="seaborn" )

    # Create a JSON representation of the graph
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
#news
@app.route('/news', methods=['GET', 'POST'])
def news():

        url = "https://api.polygon.io/v2/reference/news?limit=10&order=descending&sort=published_utc&apiKey=IEYEgwYV9L8HiDg1NkhaUIwSsPdzG9J1"

        payload = ""
        headers = {
            'cache-control': "no-cache",
            'Postman-Token': "10b636d3-6e76-4352-ba6d-2601169694da"
        }

        response = requests.request("GET", url, data=payload, headers=headers)
        stockData = json.loads(response.text)
        #To retrieve the latest date from Meta Data
        title1 = stockData["results"][0]["title"]
        author1 = stockData["results"][0]["author"]
        article1=stockData["results"][0]["article_url"]

        title2 = stockData["results"][1]["title"]
        author2 = stockData["results"][1]["author"]
        article2=stockData["results"][1]["article_url"]

        title3 = stockData["results"][2]["title"]
        author3 = stockData["results"][2]["author"]
        article3=stockData["results"][2]["article_url"]

        title4 = stockData["results"][3]["title"]
        author4 = stockData["results"][3]["author"]
        article4=stockData["results"][3]["article_url"]

        title5 = stockData["results"][4]["title"]
        author5 = stockData["results"][4]["author"]
        image5=stockData["results"][4]["image_url"]
        article5=stockData["results"][4]["article_url"]

        title6 = stockData["results"][5]["title"]
        author6 = stockData["results"][5]["author"]
        image6=stockData["results"][5]["image_url"]
        article6=stockData["results"][5]["article_url"]

        title7 = stockData["results"][6]["title"]
        author7 = stockData["results"][6]["author"]
        image7=stockData["results"][6]["image_url"]
        article7=stockData["results"][6]["article_url"]

        title8 = stockData["results"][7]["title"]
        author8 = stockData["results"][7]["author"]
        image8=stockData["results"][7]["image_url"]
        article8=stockData["results"][7]["article_url"]

        title9 = stockData["results"][8]["title"]
        author9 = stockData["results"][8]["author"]
        image9=stockData["results"][8]["image_url"]
        article9=stockData["results"][8]["article_url"]

        title10 = stockData["results"][9]["title"]
        author10 = stockData["results"][9]["author"]
        image10=stockData["results"][9]["image_url"]
        article10=stockData["results"][9]["article_url"]

        #To retrieve lastest stock price

        return render_template('news.html',
                title1=title1,title2=title2,title3=title3,title4=title4,title5=title5,title6=title6,title7=title7,title8=title8,title9=title9,title10=title10,
                author1=author1,author2=author2,author3=author3,author4=author4,author5=author5,author6=author6,author7=author7,author8=author8,author9=author9,author10=author10,
                image5=image5,image6=image6,image7=image7,image8=image8 , image9=image9, image10=image10,
                article1=article1,article2=article2,article3=article3,article4=article4,article5=article5,article6=article6,article7=article7,article8=article8,article9=article9,article10=article10,
               )

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    app.secret_key = "OBKDAPP"
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
  
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
  
        # Get user by email
        result = cur.execute("SELECT * FROM user_flask WHERE email = %s", [email])
  
        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            session['logged_in'] = True
            session['email'] = email
  
            flash('You are now logged in', 'success')
            return redirect(url_for('dashboard'))
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
  
    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    app.secret_key = "OBKDAPP"

    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap
 
# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))




# Dashboard(stocks owned)
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
  
    # Get articles
    #result = cur.execute("SELECT * FROM articles")
    # Show articles only from the user logged in 
    result = cur.execute("SELECT * FROM stocks WHERE user = %s", [session['email']])
  
    stocks = cur.fetchall()
  
    if result > 0:
        return render_template('dashboard.html', stocks=stocks)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()


# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST':
        symbol = form.symbol.data
        stocksNo = form.stocksNo.data
        marketPrice = form.marketPrice.data
        totalAmt = form.totalAmt.data
        date = form.date.data

        # Create Cursor
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
  
        # Execute
        cur.execute("INSERT INTO stocks(symbol, stocksNo, marketPrice, totalAmt, date, user) VALUES(%s, %s, %s,%s, %s, %s)",(symbol, stocksNo, marketPrice, totalAmt, date, session['email']))
        # Commit to DB
        conn.commit()
        #Close connection
        cur.close()
        flash('Stocks Bought', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)


#Ranking
@app.route('/stock', methods=['GET', 'POST'])
def rank():

        url = "https://financialmodelingprep.com/api/v3/stock-screener?marketCapMoreThan=1000000000&betaMoreThan=1&volumeMoreThan=10000&country=US&dividendMoreThan=0&limit=100&apikey=9405b4982642aadbf3d27eb8a06b13fa"
        aapl = "https://api.finage.co.uk/last/stock/changes/aapl?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        googl = "https://api.finage.co.uk/last/stock/changes/googl?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        goog = "https://api.finage.co.uk/last/stock/changes/goog?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        amzn = "https://api.finage.co.uk/last/stock/changes/amzn?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        tsla = "https://api.finage.co.uk/last/stock/changes/tsla?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        nvda = "https://api.finage.co.uk/last/stock/changes/nvda?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        fb = "https://api.finage.co.uk/last/stock/changes/fb?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        vti = "https://api.finage.co.uk/last/stock/changes/vti?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        jpm = "https://api.finage.co.uk/last/stock/changes/jpm?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        spy = "https://api.finage.co.uk/last/stock/changes/spy?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        payload = ""
        headers = {
            'cache-control': "no-cache",
            'Postman-Token': "10b636d3-6e76-4352-ba6d-2601169694da"
        }

        response = requests.request("GET", url, data=payload, headers=headers)
        stockData = json.loads(response.text)
        #To retrieve the latest date from Meta Data
        symbol1 = stockData[0]["symbol"]
        company1 = stockData[0]["companyName"]
        marketcap1=stockData[0]["marketCap"]
        volume1=stockData[0]["volume"]

        symbol2 = stockData[1]["symbol"]
        company2 = stockData[1]["companyName"]
        marketcap2=stockData[1]["marketCap"]
        volume2=stockData[1]["volume"]

        symbol3 = stockData[2]["symbol"]
        company3 = stockData[2]["companyName"]
        marketcap3=stockData[2]["marketCap"]
        volume3=stockData[2]["volume"]

        symbol4 = stockData[3]["symbol"]
        company4 = stockData[3]["companyName"]
        marketcap4=stockData[3]["marketCap"]
        volume4=stockData[3]["volume"]

        symbol5 = stockData[4]["symbol"]
        company5 = stockData[4]["companyName"]
        marketcap5=stockData[4]["marketCap"]
        volume5=stockData[4]["volume"]


        symbol6 = stockData[5]["symbol"]
        company6 = stockData[5]["companyName"]
        marketcap6=stockData[5]["marketCap"]
        volume6=stockData[5]["volume"]

        symbol7 = stockData[6]["symbol"]
        company7 = stockData[6]["companyName"]
        marketcap7=stockData[6]["marketCap"]
        volume7=stockData[6]["volume"]

        symbol8 = stockData[7]["symbol"]
        company8 = stockData[7]["companyName"]
        marketcap8=stockData[7]["marketCap"]
        volume8=stockData[7]["volume"]

        symbol9 = stockData[8]["symbol"]
        company9 = stockData[8]["companyName"]
        marketcap9=stockData[8]["marketCap"]
        volume9=stockData[8]["volume"]

        symbol10 = stockData[9]["symbol"]
        company10 = stockData[9]["companyName"]
        marketcap10=stockData[9]["marketCap"]
        volume10=stockData[9]["volume"]

        symbol11 = stockData[10]["symbol"]
        company11 = stockData[10]["companyName"]
        marketcap11=stockData[10]["marketCap"]
        volume11=stockData[10]["volume"]

        symbol12 = stockData[11]["symbol"]
        company12 = stockData[11]["companyName"]
        marketcap12=stockData[11]["marketCap"]
        volume12=stockData[11]["volume"]

        symbol13 = stockData[12]["symbol"]
        company13 = stockData[12]["companyName"]
        marketcap13=stockData[12]["marketCap"]
        volume13=stockData[12]["volume"]

        symbol14 = stockData[13]["symbol"]
        company14 = stockData[13]["companyName"]
        marketcap14=stockData[13]["marketCap"]
        volume14=stockData[13]["volume"]

        symbol15 = stockData[14]["symbol"]
        company15 = stockData[14]["companyName"]
        marketcap15=stockData[14]["marketCap"]
        volume15=stockData[14]["volume"]

        aaplresponse = requests.request("GET", aapl, data=payload, headers=headers)
        googlresponse = requests.request("GET", googl, data=payload, headers=headers)
        googresponse = requests.request("GET", goog, data=payload, headers=headers)
        amznresponse = requests.request("GET", amzn, data=payload, headers=headers)
        tslaresponse = requests.request("GET", tsla, data=payload, headers=headers)
        nvdaresponse = requests.request("GET", nvda, data=payload, headers=headers)
        fbresponse = requests.request("GET", fb, data=payload, headers=headers)
        vtiresponse = requests.request("GET", vti, data=payload, headers=headers)
        jpmresponse = requests.request("GET", jpm, data=payload, headers=headers)
        spyresponse = requests.request("GET", spy, data=payload, headers=headers)

        aaplData = json.loads(aaplresponse.text)
        googlData = json.loads(googlresponse.text)
        googData = json.loads(googresponse.text)
        amznData = json.loads(amznresponse.text)
        tslaData = json.loads(tslaresponse.text)
        nvdaData = json.loads(nvdaresponse.text)
        fbData = json.loads(fbresponse.text)
        vtiData = json.loads(vtiresponse.text)
        jpmData = json.loads(jpmresponse.text)
        spyData = json.loads(spyresponse.text)

        #To retrieve the latest date from Meta Data
        changesAAPL = aaplData["cpd"]
        changesGOOGL = googlData["cpd"]
        changesGOOG = googData["cpd"]
        changesAMZN = amznData["cpd"]
        changesTSLA = tslaData["cpd"]
        changesNVDA = nvdaData["cpd"]
        changesFB = fbData["cpd"]
        changesVTI = vtiData["cpd"]
        changesJPM = jpmData["cpd"]
        changesSPY = spyData["cpd"]


        #To retrieve lastest stock price
        return render_template('stock.html',
                symbol1=symbol1,symbol2=symbol2,symbol3=symbol3,symbol4=symbol4,symbol5=symbol5,symbol6=symbol6,symbol7=symbol7,symbol8=symbol8,symbol9=symbol9,symbol10=symbol10,symbol11=symbol11,symbol12=symbol12,symbol13=symbol13,symbol14=symbol14,symbol15=symbol15,
                company1=company1,company2=company2,company3=company3,company4=company4,company5=company5,company6=company6,company7=company7,company8=company8,company9=company9,company10=company10,company11=company11,company12=company12,company13=company13,company14=company14,company15=company15,
                marketcap1=marketcap1,marketcap2=marketcap2,marketcap3=marketcap3,marketcap4=marketcap4,marketcap5=marketcap5,marketcap6=marketcap6,marketcap7=marketcap7,marketcap8=marketcap8,marketcap9=marketcap9,marketcap10=marketcap10,marketcap11=marketcap11,marketcap12=marketcap12,marketcap13=marketcap13,marketcap14=marketcap14,marketcap15=marketcap15,
                volume1=volume1,volume2=volume2,volume3=volume3,volume4=volume4,volume5=volume5,volume6=volume6,volume7=volume7,volume8=volume8,volume9=volume9,volume10=volume10,volume11=volume11,volume12=volume12,volume13=volume13,volume14=volume14,volume15=volume15,
                 changesAAPL=changesAAPL,changesGOOGL=changesGOOGL,changesGOOG=changesGOOG,changesAMZN=changesAMZN,changesTSLA=changesTSLA,
                changesNVDA=changesNVDA,changesFB=changesFB,changesVTI=changesVTI,changesJPM=changesJPM,changesSPY=changesSPY
                )

#Cndle Graph
@app.route('/rsi',methods=['GET', 'POST'])
def rsi():
    if request.method == 'POST':  
        TOKEN  = "9405b4982642aadbf3d27eb8a06b13fa"
      
        SYMBOL = request.form['stock']

        r = requests.get("https://financialmodelingprep.com/api/v3/historical-chart/1min/{}?apikey={}".format(SYMBOL, TOKEN))


        items = json.loads(r.content)

        csv_file = open('stock.csv', 'w')
        csv_writer = csv.writer(csv_file)

        csv_writer.writerow(['date', 'open', 'high', 'low', 'close'])

        for item in items:
            csv_writer.writerow([item['date'], item['open'], item['high'], item['low'], item['close']])

        csv_file.close()

        df = pandas.read_csv('stock.csv')

        candlestick = go.Candlestick(x=df['date'], 
                            open=df['open'],
                            high=df['high'],
                            low=df['low'],
                            close=df['close'])

        fig = go.Figure(data=[candlestick])

            # ignore weekends
        fig.layout.xaxis.type = 'category'

        shapes = [
                dict(x0='2019-01-02', x1='2019-01-02', y0=0, y1=1, xref='x', yref='paper'),
                dict(x0='2019-05-05', x1='2019-05-05', y0=0, y1=1, xref='x', yref='paper'),
                dict(x0='2019-07-30', x1='2019-07-30', y0=0, y1=1, xref='x', yref='paper'),
                dict(x0='2019-10-30', x1='2019-10-30', y0=0, y1=1, xref='x', yref='paper'),
            ]

        annotations=[
                dict(x='2019-01-03', y=0.01, xref='x', yref='paper', showarrow=False, xanchor='left', text=''),
                dict(x='2019-05-05', y=0.5, xref='x', yref='paper', showarrow=False, xanchor='left', text=''),
                dict(x='2019-07-30', y=0.3, xref='x', yref='paper', showarrow=False, xanchor='left', text=''),
                dict(x='2019-10-30', y=0.3, xref='x', yref='paper', showarrow=False, xanchor='left', text=''),
            ]

        fig.update_layout(title='Candlestick Stock Screener', annotations=annotations, shapes=shapes)

        

        fig.write_html('templates/aapl.html', auto_open=False)

    return render_template('rsi.html')

#changes
@app.route('/stock', methods=['GET', 'POST'])
def changes():

        aapl = "https://api.finage.co.uk/last/stock/changes/aapl?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        googl = "https://api.finage.co.uk/last/stock/changes/googl?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        goog = "https://api.finage.co.uk/last/stock/changes/goog?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        amzn = "https://api.finage.co.uk/last/stock/changes/amzn?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        tsla = "https://api.finage.co.uk/last/stock/changes/tsla?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        nvda = "https://api.finage.co.uk/last/stock/changes/nvda?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        fb = "https://api.finage.co.uk/last/stock/changes/fb?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        vti = "https://api.finage.co.uk/last/stock/changes/vti?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        jpm = "https://api.finage.co.uk/last/stock/changes/jpm?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"
        spy = "https://api.finage.co.uk/last/stock/changes/spy?apikey=API_KEY335SFJNAC4IS87EVHYQ2JBE1P7UUFWKU"

        payload = ""
        headers = {
            'cache-control': "no-cache",
            'Postman-Token': "10b636d3-6e76-4352-ba6d-2601169694da"
        }

        aaplresponse = requests.request("GET", aapl, data=payload, headers=headers)
        googlresponse = requests.request("GET", googl, data=payload, headers=headers)
        googresponse = requests.request("GET", goog, data=payload, headers=headers)
        amznresponse = requests.request("GET", amzn, data=payload, headers=headers)
        tslaresponse = requests.request("GET", tsla, data=payload, headers=headers)
        nvdaresponse = requests.request("GET", nvda, data=payload, headers=headers)
        fbresponse = requests.request("GET", fb, data=payload, headers=headers)
        vtiresponse = requests.request("GET", vti, data=payload, headers=headers)
        jpmresponse = requests.request("GET", jpm, data=payload, headers=headers)
        spyresponse = requests.request("GET", spy, data=payload, headers=headers)

        aaplData = json.loads(aaplresponse.text)
        googlData = json.loads(googlresponse.text)
        googData = json.loads(googresponse.text)
        amznData = json.loads(amznresponse.text)
        tslaData = json.loads(tslaresponse.text)
        nvdaData = json.loads(nvdaresponse.text)
        fbData = json.loads(fbresponse.text)
        vtiData = json.loads(vtiresponse.text)
        jpmData = json.loads(jpmresponse.text)
        spyData = json.loads(spyresponse.text)

        #To retrieve the latest date from Meta Data
        changesAAPL = aaplData["cpd"]
        changesGOOGL = googlData[0]["cpd"]
        changesGOOG = googData[0]["cpd"]
        changesAMZN = amznData[0]["cpd"]
        changesTSLA = tslaData[0]["cpd"]
        changesNVDA = nvdaData[0]["cpd"]
        changesFB = fbData[0]["cpd"]
        changesVTI = vtiData[0]["cpd"]
        changesJPM = jpmData[0]["cpd"]
        changesSPY = spyData[0]["cpd"]


        return render_template('stock.html',
                changesAAPL=changesAAPL,changesGOOGL=changesGOOGL,changesGOOG=changesGOOG,changesAMZN=changesAMZN,changesTSLA=changesTSLA,
                changesNVDA=changesNVDA,changesFB=changesFB,changesVTI=changesVTI,changesJPM=changesJPM,changesSPY=changesSPY
                )

#active
@app.route('/actives', methods=['GET', 'POST'])
def actives():

    url1="https://financialmodelingprep.com/api/v3/stock_market/actives?apikey=9405b4982642aadbf3d27eb8a06b13fa"

    payload = ""
    headers = {
            'cache-control': "no-cache",
            'Postman-Token': "10b636d3-6e76-4352-ba6d-2601169694da"
        }

    response1 = requests.request("GET", url1, data=payload, headers=headers)

    stockData = json.loads(response1.text)
        #To retrieve the latest date from Meta Data
    symbol1 = stockData[0]["symbol"]
    company1 = stockData[0]["name"]
    change1=stockData[0]["change"]
    price1=stockData[0]["price"]
    changePercent1=stockData[0]["changesPercentage"]

    symbol2 = stockData[1]["symbol"]
    company2 = stockData[1]["name"]
    change2=stockData[1]["change"]
    price2=stockData[1]["price"]
    changePercent2=stockData[1]["changesPercentage"]

    symbol3 = stockData[2]["symbol"]
    company3 = stockData[2]["name"]
    change3=stockData[2]["change"]
    price3=stockData[2]["price"]
    changePercent3=stockData[2]["changesPercentage"]

    symbol4 = stockData[3]["symbol"]
    company4 = stockData[3]["name"]
    change4=stockData[3]["change"]
    price4=stockData[3]["price"]
    changePercent4=stockData[3]["changesPercentage"]

    symbol5 = stockData[4]["symbol"]
    company5 = stockData[4]["name"]
    change5=stockData[4]["change"]
    price5=stockData[4]["price"]
    changePercent5=stockData[4]["changesPercentage"]

    symbol6 = stockData[5]["symbol"]
    company6 = stockData[5]["name"]
    change6=stockData[5]["change"]
    price6=stockData[5]["price"]
    changePercent6=stockData[5]["changesPercentage"]

    symbol7 = stockData[6]["symbol"]
    company7 = stockData[6]["name"]
    change7=stockData[6]["change"]
    price7=stockData[6]["price"]
    changePercent7=stockData[6]["changesPercentage"]

    symbol8 = stockData[7]["symbol"]
    company8 = stockData[7]["name"]
    change8=stockData[7]["change"]
    price8=stockData[7]["price"]
    changePercent8=stockData[7]["changesPercentage"]

    symbol9 = stockData[8]["symbol"]
    company9 = stockData[8]["name"]
    change9=stockData[8]["change"]
    price9=stockData[8]["price"]
    changePercent9=stockData[8]["changesPercentage"]

    symbol10 = stockData[9]["symbol"]
    company10 = stockData[9]["name"]
    change10=stockData[9]["change"]
    price10=stockData[9]["price"]
    changePercent10=stockData[9]["changesPercentage"]

        #To retrieve lastest stock price

    if request.method == "POST":
        SYMBOL = request.form['stocks']
        TOKEN  = "9405b4982642aadbf3d27eb8a06b13fa"
        r = requests.get("https://financialmodelingprep.com/api/v3/historical-chart/1min/{}?apikey={}".format(SYMBOL, TOKEN))

        url = "https://financialmodelingprep.com/api/v3/earnings-surprises/{}?apikey=9405b4982642aadbf3d27eb8a06b13fa".format(SYMBOL)
        url2="https://finnhub.io/api/v1/stock/insider-transactions?symbol={}&token=c88dchqad3iet0qjgg50".format(SYMBOL)

        payload = ""
        headers = {
            'cache-control': "no-cache",
            'Postman-Token': "10b636d3-6e76-4352-ba6d-2601169694da"
        }

        response = requests.request("GET", url, data=payload, headers=headers)
        response2 = requests.request("GET", url2, data=payload, headers=headers)

        stockData3 = json.loads(response.text)
        stockData2 = json.loads(response2.text)


            #To retrieve the latest date from Meta Data
        date1 = stockData3[0]["date"]
        symbol1e = stockData3[0]["symbol"]
        actualEarning1=stockData3[0]["actualEarningResult"]
        estEarning1=stockData3[0]["estimatedEarning"]

        date2 = stockData3[1]["date"]
        symbol2e = stockData3[1]["symbol"]
        actualEarning2=stockData3[1]["actualEarningResult"]
        estEarning2=stockData3[1]["estimatedEarning"]

        date3 = stockData3[2]["date"]
        symbol3e = stockData3[2]["symbol"]
        actualEarning3=stockData3[2]["actualEarningResult"]
        estEarning3=stockData3[2]["estimatedEarning"]

        date4 = stockData3[3]["date"]
        symbol4e = stockData3[3]["symbol"]
        actualEarning4=stockData3[3]["actualEarningResult"]
        estEarning4=stockData3[3]["estimatedEarning"]

        symbols1 = stockData2['data'][0]["symbol"]
        companys1 = stockData2['data'][0]["name"]
        shares1=stockData2['data'][0]["share"]
        changes1=stockData2['data'][0]["change"]
        transaction1=stockData2['data'][0]["transactionPrice"]

        symbols2 = stockData2['data'][1]["symbol"]
        companys2 = stockData2['data'][1]["name"]
        shares2=stockData2['data'][1]["share"]
        changes2=stockData2['data'][1]["change"]
        transaction2=stockData2['data'][1]["transactionPrice"]

        symbols3 = stockData2['data'][2]["symbol"]
        companys3 = stockData2['data'][2]["name"]
        shares3=stockData2['data'][2]["share"]
        changes3=stockData2['data'][2]["change"]
        transaction3=stockData2['data'][2]["transactionPrice"]

        symbols4 = stockData2['data'][3]["symbol"]
        companys4 = stockData2['data'][3]["name"]
        shares4=stockData2['data'][3]["share"]
        changes4=stockData2['data'][3]["change"]
        transaction4=stockData2['data'][3]["transactionPrice"]

        symbols5 = stockData2['data'][4]["symbol"]
        companys5 = stockData2['data'][4]["name"]
        shares5=stockData2['data'][4]["share"]
        changes5=stockData2['data'][4]["change"]
        transaction5=stockData2['data'][4]["transactionPrice"]

        symbols6 = stockData2['data'][5]["symbol"]
        companys6 = stockData2['data'][5]["name"]
        shares6=stockData2['data'][5]["share"]
        changes6=stockData2['data'][5]["change"]
        transaction6=stockData2['data'][5]["transactionPrice"]

        symbols7 = stockData2['data'][6]["symbol"]
        companys7 = stockData2['data'][6]["name"]
        shares7=stockData2['data'][6]["share"]
        changes7=stockData2['data'][6]["change"]
        transaction7=stockData2['data'][6]["transactionPrice"]

        symbols8 = stockData2['data'][7]["symbol"]
        companys8 = stockData2['data'][7]["name"]
        shares8=stockData2['data'][7]["share"]
        changes8=stockData2['data'][7]["change"]
        transaction8=stockData2['data'][7]["transactionPrice"]

        symbols9 = stockData2['data'][8]["symbol"]
        companys9 = stockData2['data'][8]["name"]
        shares9=stockData2['data'][8]["share"]
        changes9=stockData2['data'][8]["change"]
        transaction9=stockData2['data'][8]["transactionPrice"]

        symbols10 = stockData2['data'][9]["symbol"]
        companys10 = stockData2['data'][9]["name"]
        shares10=stockData2['data'][9]["share"]
        changes10=stockData2['data'][9]["change"]
        transaction10=stockData2['data'][9]["transactionPrice"]


        items = json.loads(r.content)

        csv_file = open('stock.csv', 'w')
        csv_writer = csv.writer(csv_file)

        csv_writer.writerow(['date', 'open', 'high', 'low', 'close'])

        for item in items:
            csv_writer.writerow([item['date'], item['open'], item['high'], item['low'], item['close']])

        csv_file.close()

        df = pandas.read_csv('stock.csv')

        candlestick = go.Candlestick(x=df['date'], 
                            open=df['open'],
                            high=df['high'],
                            low=df['low'],
                            close=df['close'])

        fig = go.Figure(data=[candlestick])

            # ignore weekends
        fig.layout.xaxis.type = 'category'

        shapes = [
                dict(x0='2019-01-02', x1='2019-01-02', y0=0, y1=1, xref='x', yref='paper'),
                dict(x0='2019-05-05', x1='2019-05-05', y0=0, y1=1, xref='x', yref='paper'),
                dict(x0='2019-07-30', x1='2019-07-30', y0=0, y1=1, xref='x', yref='paper'),
                dict(x0='2019-10-30', x1='2019-10-30', y0=0, y1=1, xref='x', yref='paper'),
            ]

        annotations=[
                dict(x='2019-01-03', y=0.01, xref='x', yref='paper', showarrow=False, xanchor='left', text=''),
                dict(x='2019-05-05', y=0.5, xref='x', yref='paper', showarrow=False, xanchor='left', text=''),
                dict(x='2019-07-30', y=0.3, xref='x', yref='paper', showarrow=False, xanchor='left', text=''),
                dict(x='2019-10-30', y=0.3, xref='x', yref='paper', showarrow=False, xanchor='left', text=''),
            ]

        fig.update_layout(title='Candlestick Stock Screener', annotations=annotations, shapes=shapes)

        

        fig.write_html('templates/aapl.html', auto_open=False)


        return render_template('active.html',
 symbol1=symbol1,symbol2=symbol2,symbol3=symbol3,symbol4=symbol4,symbol5=symbol5,symbol6=symbol6,symbol7=symbol7,symbol8=symbol8,symbol9=symbol9,symbol10=symbol10,
                company1=company1,company2=company2,company3=company3,company4=company4,company5=company5,company6=company6,company7=company7,company8=company8,company9=company9,company10=company10,
                change1=change1,change2=change2,change3=change3,change4=change4,change5=change5,change6=change6,change7=change7,change8=change8,change9=change9,change10=change10,
                price1=price1,price2=price2,price3=price3,price4=price4,price5=price5,price6=price6,price7=price7,price8=price8,price9=price9,price10=price10,
                changePercent1=changePercent1,changePercent2=changePercent2,changePercent3=changePercent3,changePercent4=changePercent4,changePercent5=changePercent5,changePercent6=changePercent6,changePercent7=changePercent7,changePercent8=changePercent8,changePercent9=changePercent9,changePercent10=changePercent10,
                 symbols1=symbols1,symbols2=symbols2,symbols3=symbols3,symbols4=symbols4,symbols5=symbols5,symbols6=symbols6,symbols7=symbols7,symbols8=symbols8,symbols9=symbols9,symbols10=symbols10,
                companys1=companys1,companys2=companys2,companys3=companys3,companys4=companys4,companys5=companys5,companys6=companys6,companys7=companys7,companys8=companys8,companys9=companys9,companys10=companys10,
                shares1=shares1,shares2=shares2,shares3=shares3,shares4=shares4,shares5=shares5,shares6=shares6,shares7=shares7,shares8=shares8,shares9=shares9,shares10=shares10,
                changes1=changes1,changes2=changes2,changes3=changes3,changes4=changes4,changes5=changes5,changes6=changes6,changes7=changes7,changes8=changes8,changes9=changes9,changes10=changes10,
                                transaction1=transaction1,transaction2=transaction2,transaction3=transaction3,transaction4=transaction4,transaction5=transaction5,transaction6=transaction6,transaction7=transaction7,transaction8=transaction8,transaction9=transaction9,transaction10=transaction10,
                                                date1=date1,date2=date2,date3=date3,date4=date4,
                symbol1e=symbol1e,symbol2e=symbol2e,symbol3e=symbol3e,symbol4e=symbol4e,
                actualEarning1=actualEarning1,actualEarning2=actualEarning2,actualEarning3=actualEarning3,actualEarning4=actualEarning4,
                estEarning1=estEarning1,estEarning2=estEarning2,estEarning3=estEarning3,estEarning4=estEarning4
)



    return render_template('active.html',
 symbol1=symbol1,symbol2=symbol2,symbol3=symbol3,symbol4=symbol4,symbol5=symbol5,symbol6=symbol6,symbol7=symbol7,symbol8=symbol8,symbol9=symbol9,symbol10=symbol10,
                company1=company1,company2=company2,company3=company3,company4=company4,company5=company5,company6=company6,company7=company7,company8=company8,company9=company9,company10=company10,
                change1=change1,change2=change2,change3=change3,change4=change4,change5=change5,change6=change6,change7=change7,change8=change8,change9=change9,change10=change10,
                price1=price1,price2=price2,price3=price3,price4=price4,price5=price5,price6=price6,price7=price7,price8=price8,price9=price9,price10=price10,
                changePercent1=changePercent1,changePercent2=changePercent2,changePercent3=changePercent3,changePercent4=changePercent4,changePercent5=changePercent5,changePercent6=changePercent6,changePercent7=changePercent7,changePercent8=changePercent8,changePercent9=changePercent9,changePercent10=changePercent10,
)


#earnings
@app.route('/active', methods=['GET', 'POST'])
def active():
    if request.method == "POST":
        SYMBOL = request.form['stocks']

        url = "https://financialmodelingprep.com/api/v3/earnings-surprises/{}?apikey=9405b4982642aadbf3d27eb8a06b13fa".format(SYMBOL)

        payload = ""
        headers = {
            'cache-control': "no-cache",
            'Postman-Token': "10b636d3-6e76-4352-ba6d-2601169694da"
        }

        response = requests.request("GET", url, data=payload, headers=headers)
        stockData = json.loads(response.text)
        #To retrieve the latest date from Meta Data
        date1 = stockData[0]["date"]
        symbol1e = stockData[0]["symbol"]
        


        return render_template('active.html',
                date1=date1,
                symbol1e=symbol1e,
               )

