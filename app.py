import os
from flask import Flask,render_template,request,flash
from flask_pymongo import PyMongo

from flask_admin import Admin,AdminIndexView
from flask_admin.contrib.pymongo import ModelView

from flask_wtf import FlaskForm
from wtforms import form, fields

from forms import *

app = Flask(__name__)

# make sure to update the username and password
app.config['MONGO_URI'] = "mongodb+srv://username:password@cluster0.kdszu.mongodb.net/penroselearning2021?retryWrites=true&w=majority"
app.secret_key = "MongoDB"

mongo = PyMongo(app)

class ProductView(ModelView):
    column_list = ('name', 'description','price')
    form = ProductForm

admin = Admin(app,template_mode='bootstrap3')
admin.add_view(ProductView(mongo.db.products))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/view")
def view():

    myproducts = mongo.db.products
    
    return render_template("view.html",products = myproducts.find())

@app.route("/create",methods=["GET","POST"])
def create():

    if request.method == "POST":

        name = request.form["name"]
        desc = request.form["desc"]
        price = int(request.form["price"])

        myproducts = mongo.db.products
        myproducts.insert({'name':name,"description":desc,"price":price})

        flash(f'{name} has been successfully saved')
        
    return render_template("create.html")


if __name__ == "__main__":
    app.run(debug=True)