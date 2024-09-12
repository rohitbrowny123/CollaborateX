from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from application import app
from application.model import db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///influnce.sqlite3'
app.secret_key="allset"
db.init_app(app)


# from application import controller
# with app.app_context():
#     db.create_all()

from application.controller import *
# Initialize the database
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=8000)

