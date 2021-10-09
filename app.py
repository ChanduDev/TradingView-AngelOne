import json, config, logging
from flask import Flask, request, jsonify, render_template
 
# package import statement
# from smartapi import SmartConnect
# from smartapi.smartExceptions import *
from smartapi.smartConnect import *

app = Flask(__name__)

#create object of call
#obj=SmartConnect(api_key="your api key",
                #optional
                #access_token = "your access token",
                #refresh_token = "your refresh_token")

#create object of call
obj=SmartConnect(api_key=config.API_KEY,access_token=config.API_SECRET)

#login api call
data=obj.generateSession(config.API_Client_ID,config.API_Password)
refreshToken=data['data']['refreshToken']

#fetch the feedtoken
feedToken=obj.getfeedToken()

#fetch User Profile
userProfile=obj.getProfile(refreshToken)

#place order
def order(symbol,symboltoken,transactiontype,quantity):
    try:
        print("sending order parameters as {symbol} , {symboltoken} , {transactiontype} , {quantity}")
        orderparams = {
                        "variety": "NORMAL",
                        "tradingsymbol": "{symbol}",
                        "symboltoken": "{symboltoken}",
                        "transactiontype": "{transactiontype}",
                        "exchange": "NSE",
                        "ordertype": "MARKET",
                        "producttype": "DELIVERY",
                        "duration": "DAY",
                        "price": "0",
                        "squareoff": "0",
                        "stoploss": "0",
                        "quantity": "{quantity}"
                        }
        orderId=obj.placeOrder(orderparams)
        print("The order id is: {}".format(orderId))
    except Exception as e:
        print("Order placement failed: {}".format(e.message))
        return False
    
    return order

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route("/webhook", methods=['POST'])
def webhook():

    requestData = json.loads(request.data)

    if requestData['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            "code": "error",
            "message": "Nice try, invalid passphrase"
        }

    symbol = requestData['orderDetails']['symbol'].upper()
    symboltoken = requestData['orderDetails']['symboltoken']
    transactiontype = requestData['orderDetails']['transactiontype'].upper()
    quantity = requestData['orderDetails']['quantity']

    order_response = order(symbol,symboltoken,transactiontype,quantity)

    if order_response:
        print("order success")
        return {
            "code": "success",
            "message": "New Order Executed Successfully"
        }
    else:
        print("order failed")
        return {
            "code": "error",
            "message": "New Order Failed - Check Logs"
        }