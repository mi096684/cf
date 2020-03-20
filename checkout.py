from flask import Flask, request, render_template
import sys
import traceback
import random
import hashlib
import hmac
import base64

app = Flask(__name__)
# run_with_ngrok(app)

secretKey = "4124b635056c9a58f9da8d7b3ef1d7394b8b7448"

# random order ID
order_id_dummy = 50003



#product/start page
@app.route('/')
def index():
    #dumm order ID
    order_id_dummy = str(random.randint(6000, 10000))
    return render_template("index.html", order_id = order_id_dummy)

#Onclick call checkout
@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        #get form data
        order_id = request.form.get('order-id')
        order_details = get_order_details(order_id)
        customer_details = get_customer_details(order_id)
        #dummy order details
        postData = {
            "appId": "14265c089411025f6f0fdee9256241",
            "orderId": order_details['order_id'],
            "orderAmount": order_details['order_amount'],
            "orderCurrency": "INR",
            "orderNote": order_details['order_note'],
            "customerName": customer_details['name'],
            "customerEmail": customer_details['email'],
            "customerPhone":  customer_details['phone'],
            "returnUrl": "http://127.0.0.1:8000/response",
            "notifyUrl": "http://127.0.0.1:8000/notify",
        }

        postData['signature'] = generate_signature(postData)
        return render_template('checkout.html', postData=postData)

    except Exception as err:
        print(err)
        traceback.print_exc(file=sys.stdout)
        return {"message": "an exception occured"}, 500


@app.route('/response', methods=["POST"])
def response():

    postData = {
        "orderId": request.form['orderId'],
        "orderAmount": request.form['orderAmount'],
        "referenceId": request.form['referenceId'],
        "txStatus": request.form['txStatus'],
        "paymentMode": request.form['paymentMode'],
        "txMsg": request.form['txMsg'],
        "signature": request.form['signature'],
        "txTime": request.form['txTime']
    }

    signatureData = ""
    signatureData = postData['orderId'] + postData['orderAmount'] + postData['referenceId'] + \
        postData['txStatus'] + postData['paymentMode'] + \
        postData['txMsg'] + postData['txTime']

    message = signatureData.encode('utf-8')
    # get secret key from your config
    secret = secretKey.encode('utf-8')
    computedsignature = base64.b64encode(
        hmac.new(secret, message, digestmod=hashlib.sha256).digest()).decode('utf-8')
    if computedsignature == postData['signature']:
        return '<center><img src="https://i.stack.imgur.com/YbIni.png"/></center>'
    else:
        return '<center><img src="https://user-images.githubusercontent.com/11629214/35469831-ad288d00-0378-11e8-9019-dd1f5eb4bea3.png"/></center>'


@app.route('/notify', methods=["POST"])
def notify():

    postData = {
        "orderId": request.form['orderId'],
        "orderAmount": request.form['orderAmount'],
        "referenceId": request.form['referenceId'],
        "txStatus": request.form['txStatus'],
        "paymentMode": request.form['paymentMode'],
        "txMsg": request.form['txMsg'],
        "signature": request.form['signature'],
        "txTime": request.form['txTime']
    }

    signatureData = ""
    signatureData = postData['orderId'] + postData['orderAmount'] + postData['referenceId'] + \
        postData['txStatus'] + postData['paymentMode'] + \
        postData['txMsg'] + postData['txTime']

    message = signatureData.encode('utf-8')
    # get secret key from your config
    secret = secretKey.encode('utf-8')
    computedsignature = base64.b64encode(
        hmac.new(secret, message, digestmod=hashlib.sha256).digest()).decode('utf-8')
    if computedsignature == postData['signature']:
        pass # recordSuccesfullPayment()

    return "Successful"




def get_order_details(order_id):
    return {
        "order_id": order_id,
        "order_amount": "14800",
        "order_note": "nothing for now"
    }


def get_customer_details(order_id):
    return {

        "name": "Mohammed Ismail",
        "email": "primary.ismail@getvymo.com",
        "phone":  "9999911111"

    }


def generate_signature(postData):

    sortedKeys = sorted(postData)
    signatureData = ""
    for key in sortedKeys:
        signatureData += key+postData[key]

    message = signatureData.encode('utf-8')
    # get secret key from your config
    secret = secretKey.encode('utf-8')
    signature = base64.b64encode(
        hmac.new(secret, message, digestmod=hashlib.sha256).digest()).decode("utf-8")
    return signature


if __name__ == '__main__':
    # app.run()
    app.run(debug=True, port=8000)
