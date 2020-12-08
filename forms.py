from flask_wtf import FlaskForm
from wtforms import form, fields

class ProductForm(form.Form):
    name = fields.StringField('Name')
    description = fields.StringField('Description')
    price = fields.StringField('Price')