#!/usr/bin/python3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

username="override_user"
password="uQonfQmQqec9WcCf"

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@localhost:3306/override' % (username,password)
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

##Define tables in database
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key = True, nullable=False)
    name = db.Column(db.String(24),nullable=False,unique=True)
    email = db.Column(db.String(1024),nullable=False,unique=True)
    password = db.Column(db.String(64),nullable=False)

if(__name__=="__main__"):
    db.drop_all()
    db.create_all()
