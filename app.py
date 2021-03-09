import os
import json
from jinja2 import Markup
from flask import Flask,render_template,request,flash,session,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy

# Libary for Sending Emails
from flask_mail import Mail,Message

from datetime import timedelta

app = Flask(__name__)

app.permanent_session_lifetime = timedelta(days=1)

# Email Settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'youremail@gmail.com'
app.config['MAIL_PASSWORD'] = 'email_password'
app.config['MAIL_DEFAULT_SENDER'] = 'youremail@gmail.com'

mail = Mail(app)

# Database Location
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "products.db"))

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from models import *


# Load the products data from json to a dictionary
with open('products.json') as file:
    products = json.load(file)

# Check the Session status, create new if does not exist
def session_check():
    session.permanent = True
    if not 'cart' in session:
        session['cart'] = []

def show_cart(cart):
    final_cart = []

    for item in cart:
        c = [(id,qty) for id,qty in item.items()]
        id,qty = c[0][0],c[0][1]
        
        selected_product = [product for product in products["products"] if product["id"]== str(id)][0]
        selected_product['qty'] = qty
        
        final_cart.append(selected_product)

    return final_cart

@app.route("/")
def index():
    session_check()

    return render_template("index.html")

@app.route("/view")
def view():
    session_check()

    cart = session['cart']
   
    return render_template("view.html",products=products["products"],cart=cart)

@app.route("/add_to_cart/<int:id>",methods=['GET','POST'])
def add_to_cart(id):
    session_check()

    product = [product for product in products["products"] if product["id"]== str(id)][0]
    
    # if product id does not exist, add it to the cart
    if not any(str(product["id"]) in d for d in session['cart']):
        session['cart'].append({str(product["id"]):1})

    # if product id already exists, increment the cart qty by 1
    elif any(str(product["id"]) in d for d in session['cart']):
        for d in session['cart']:
            qty = [(k,q) for k,q in d.items() if k == str(product["id"])]
            if qty:
                qty = qty[0][1] + 1
            d.update((k, qty) for k, v in d.items() if k == str(product["id"]))

    cart = session['cart']
    
    return render_template("view.html",products=products["products"],cart=cart)


@app.route("/cart",methods=['GET','POST'])
def cart():
    
    session_check()
    
    final_cart = show_cart(session["cart"])
    
    return render_template("cart.html",final_cart=final_cart)


@app.route("/remove_from_cart/<int:id>",methods=['GET','POST'])
def remove_from_cart(id):
    session_check()
   
    for x,d in enumerate(session['cart'],start=0):
        if [k for k in d if k==str(id)]:
            break

    session["cart"].pop(x)

    return redirect(url_for('cart'))


@app.route("/empty_cart",methods=['GET','POST'])
def empty_cart():
    session.pop("cart",None)

    return redirect(url_for('cart'))


@app.route("/send_order_confirmation",methods=['GET','POST'])
def send_order_confirmation():

    if request.method == 'POST':
        name = request.form["customername"]
        phone = request.form["customerphone"]
        email = request.form["customeremail"]
        address = request.form["customeraddress"]

    final_cart = show_cart(session["cart"])

    msg = Message("Order Confirmation",recipients=[email])
    msg.html = 'Your Final Order <br/> <ul>'
    
    for product in final_cart:
        for p,qty in product.items():
            msg.html += f"<li>{ p.name } | { qty } | { p.price * qty}</li>"

    msg.html += '</ul>'

    # Enable below command to send the message
    # mail.send(msg)

    return redirect(url_for('cart'))

if __name__ == "__main__":
    app.run(debug=True)
