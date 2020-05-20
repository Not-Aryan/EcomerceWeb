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


app = Flask("Aryans-Ecomerce-Site")
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/aryan-ecom-db"
app.config['SECRET_KEY'] = 'plzwork'

Bootstrap(app)
mongo = PyMongo(app)

@app.route('/')
def index():
    global word
    if 'user-info' in session:
        word = session['user-info']['firstName']
    else:
        word = "Sign In"
    print("WORD: ", word)
    return render_template('home.html', placeholder=word)


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
        if request.method == 'GET':
            session['cart-items'] = {}
            found_products = mongo.db.products.find({})
            lst = [x for x in found_products]
            a = lst
            k = int(len(lst))
            return render_template('buy.html', products=lst)
        elif request.method == 'POST':
            doc = {}
            for item in request.form:
                # print(type(item))
                # print(item['_id'])
                # print(request.form[item])
                if int(request.form[item]) != 0:
                    doc[item] = request.form[item]
                else:
                    print("NOTHING")
            print(request.form)
            session['cart-items'] = doc
            return redirect('/checkout')
    else:
        flash("You need to login first!")
        return redirect('/login')


@app.route('/checkout')
def checkout():
    if 'user-info' in session:
        total = 0
        cart_items = []
        # print(type(session['cart-items']))
        stored_info = session['cart-items']
        #print(type(stored_info))
        # print(type(stored_info), stored_info)
        # print(stored_info['_id'])
        for ID in stored_info:
            # print(type(ID))
            found_item = mongo.db.products.find_one({'_id': ObjectId(ID)})
            found_item['bought'] = stored_info[ID]
            found_item['item-total'] = int(found_item['price']) * int(found_item['bought'])
            bob = found_item['item-total']
            print("THIS ONE", found_item['item-total'])
            cart_items.append(found_item)
            total += bob
        print(cart_items)
        return render_template('checkout.html', products=cart_items, total=total)
    else:
        flash("You need to login first!")
        return redirect('/login')


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
