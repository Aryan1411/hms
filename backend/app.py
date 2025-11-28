# Importing necessary libraries
from flask import Flask
from application.database import db


# Initializing the Flask application
app= Flask(__name__)

# Configuring the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
app.app_context().push()
db.create_all()

from application.models import *
from application.controllers import *

if __name__ == '__main__':
    app.run(debug=True)