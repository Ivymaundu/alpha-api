from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key="secretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:12345@localhost:5432/alpha_products"

db = SQLAlchemy(app)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    sales=db.relationship("Sale",backref='products')
    # created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)


class Sale(db.Model):
    __tablename__='sales'
    id=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer,db.ForeignKey('products.id'),nullable=False)
    quantity=db.Column(db.Integer,nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow ,nullable=False)

class User(db.Model):
     __tablename__ = 'users'
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(100),unique=True, nullable=False)
     password = db.Column(db.String(255), nullable=False)
     