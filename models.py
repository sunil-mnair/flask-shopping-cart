from app import db
from datetime import *
from flask_admin import Admin,AdminIndexView
from flask_admin.contrib.sqla import ModelView

from pytz import timezone
uae = timezone('Asia/Dubai')

class Products(db.Model):
 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100),nullable = True)
    description = db.Column(db.String,nullable = False)
    picture = db.Column(db.String,nullable = True)
    price = db.Column(db.Integer,nullable = False)

    created_dt = db.Column(db.DateTime, nullable = False,
    default = datetime.now(uae))
    modified_dt = db.Column(db.DateTime, nullable = False,
    default = datetime.now(uae))


    def __repr__(self):
        return self.name


class AllModelView(ModelView):

    can_delete = True
    page_size = 50