# Importing necessary libraries
from flask import current_app as app
from .database import db

# Defining the User model
class User(db.Model):
    id=db.column(db.Integer, primary_key=True)
    name=db.column(db.String(80), nullable=False)
    username=db.Column(db.String(80), unique=True, nullable=False)
    password=db.Column(db.String(80), nullable=False)
    type=db.Column(db.String(80), nullable=False)
    birthyear=db.Column(db.Integer(4), nullable=False)

