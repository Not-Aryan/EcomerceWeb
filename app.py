import bson
from flask import *
import flask
import bson.objectid
import flask_bootstrap
import flask_pymongo
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import random
import paypalrestsdk

paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "Af5ECaCqQW2VHU6PmM_de64TD8yVoinERdmDf5JAr-vmfvnH-g-w6dOPu2f0rfO97VNoKEHyg5QrpZ6s",
  "client_secret": "EDHsS6dlXNhwAOv5hh00L-epf-fEz0bYi8jPaIxsbvDCP7Dp_dumnyHnLCAWYXgs2kCH42YtWVz0z0iH" })

app = Flask("Aryans-Ecomerce-Site")
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/aryan-ecom-db"
app.config['SECRET_KEY'] = 'plzwork'

Bootstrap(app)
mongo = PyMongo(app)


global cartThings
cartThings = 0
global tprice
tprice = 0.0

@app.route('/')
def index():
    global word
    global cartThings
    if 'user-info' in session:
        word = session['user-info']['firstName']
    else:
        word = "Sign In"
    print("WORD: ", word)
    return render_template('home.html', placeholder=word, number=cartThings)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('sign-up.html')
    elif request.method == 'POST':
        doc = {}
        for item in request.form:
            doc[item] = request.form[item]
        mongo.db.users.insert_one(doc)
        flash('Account created successfully!')
        return redirect('/login')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == 'POST':
        docc = {'Email': request.form['login-email'], 'Password': request.form['login-password']}
        found = mongo.db.users.find_one(docc)
        if found is None:
            flash("The email/password doesn't work. Try again")
            return redirect("/login")
        else:
            print("CORRECT")
            print(found)
            first, last = found['Name'].split(" ", 1)
            session['user-info'] = {'firstName': first, 'lastName': last,'email': found['Email']}
            global cartThings
            cartThings = 0
            return redirect("/")

@app.route('/logout')
def logout():
    session.pop('user-info')
    return redirect('/')



@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user-info' in session:
        if request.method == 'GET':
            return render_template('add.html')
        elif request.method == 'POST':
            doc = {}
            data = request.form
            for item in request.form:
                doc[item] = request.form[item]
            mongo.db.products.insert_one(doc)
            return redirect('/')
    else:
        flash("You need to login first")
        return redirect('/login')




@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if 'user-info' in session:
        global cartThings
        if request.method == 'GET':
            cartThings = 0
            session['cart-items'] = {}
            found_products = mongo.db.products.find({})
            lst = [x for x in found_products]
            a = lst
            k = int(len(lst))
            return render_template('buy.html', products=lst, number=cartThings)
        elif request.method == 'POST':
            doc = {}
            for item in request.form:
                # print(type(item))
                # print(item['_id'])
                # print(request.form[item])
                if int(request.form[item]) != 0:
                    cartThings = cartThings+1
                    doc[item] = request.form[item]
                else:
                    print("NOTHING")
            print(request.form)
            session['cart-items'] = doc
            return redirect('/checkout')
    else:
        flash("You need to login first!")
        return redirect('/login')


@app.route('/checkout',  methods=['GET', 'POST'])
def checkout():
    if 'user-info' in session:
        global cartThings
        if request.method == 'POST':
            cartThings = 0
            session['cart-items'] = {}
            print("ARYAN JAIN IS HERE")
            resp = Response("Data received")
            resp.headers['Access-Control-Allow-Origin']='*'
            return resp
        else:
            total = 0
            cart_items = []
            # print(type(session['cart-items']))
            stored_info = session['cart-items']
            # print((stored_info))
            # print(type(stoed_info), stored_info)
            # print(stored_info['_id'])
            for ID in stored_info:
                # print(type(ID))
                found_item = mongo.db.products.find_one({'_id': ObjectId(ID)})
                found_item['bought'] = stored_info[ID]
                found_item['item-total'] = int(found_item['price']) * int(found_item['bought'])
                bob = found_item['item-total']
                print("THIS ONE", found_item['item-total'])
                cart_items.append(found_item)
                global tprice
                total += bob
                tprice = total
                tprice = '${:,.2f}'.format(tprice)
                tprice = tprice.replace("$", "")
            print(cart_items)
            return render_template('checkout.html', products=cart_items, total=total, number=cartThings)
    else:
        flash("You need to login first!")
        return redirect('/login')


@app.route('/payment', methods=['POST'])
def payment():
    global tprice
    print(tprice)
    print("HI")
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",
            "cancel_url": "http://localhost:3000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "testitem",
                    "sku": "12345",
                    "price": tprice,
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": tprice,
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        flash('Payment success!')
    else:
        flash(payment.error)

    return jsonify({'paymentID' : payment.id})

@app.route('/execute', methods=['POST'])
def execute():
    success = False
    payment = paypalrestsdk.Payment.find(request.form['paymentID'])
    if payment.execute({'payer_id' : request.form['payerID']}):
        print('Execute success!')
        success = True
    else:
        print(payment.error)

    return jsonify({'success' : success})

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


app.run(debug=True)
