import os
from flask import Flask,render_template,request,flash,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy

# Libary for Sending Emails
from flask_mail import Mail,Message

# Enables the Admin View
from flask_admin import Admin,AdminIndexView
from flask_admin.contrib.sqla import ModelView

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

admin = Admin(app,template_mode='bootstrap3')

# creates an Admin View for the Products collection
admin.add_view(AllModelView(Products,db.session))


def session_check():
    session.permanent = True
    if not 'cart' in session:
        session['cart'] = []

def show_cart(cart):
    final_cart = []

    for item in cart:
        c = [(id,qty) for id,qty in item.items()]
        id,qty = c[0][0],c[0][1]
        final_cart.append({Products.query.get_or_404(int(id)):qty})

    return final_cart

@app.route("/")
def index():
    session_check()
    return render_template("index.html")

@app.route("/view")
def view():
    session_check()
    products = Products.query.all()
    cart = session['cart']
   
    return render_template("view.html",products=products,cart=cart)

@app.route("/add_to_cart/<int:id>",methods=['GET','POST'])
def add_to_cart(id):
    session_check()
    products = Products.query.all()

    product = Products.query.get_or_404(id)
    
    if not any(str(product.id) in d for d in session['cart']):
        session['cart'].append({str(product.id):1})
    
    elif any(str(product.id) in d for d in session['cart']):
        for d in session['cart']:
            qty = [(k,q) for k,q in d.items() if k == str(product.id)]
            if qty:
                qty = qty[0][1] + 1
            d.update((k, qty) for k, v in d.items() if k == str(product.id))

    cart = session['cart']
    
    return render_template("view.html",products=products,cart=cart)


@app.route("/cart",methods=['GET','POST'])
def cart():
    
    session_check()

    final_cart = show_cart(session["cart"])

    return render_template("cart.html",final_cart=final_cart)


@app.route("/remove_from_cart/<int:id>",methods=['GET','POST'])
def remove_from_cart(id):
    session_check()
    print(session["cart"])

    for x,d in enumerate(session['cart'],start=0):
        if [k for k in d if k==str(id)]:
            print(x)
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

    # mail.send(msg)

    return redirect(url_for('cart'))

if __name__ == "__main__":
    app.run(debug=True)