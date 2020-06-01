from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager





app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://jrkxwjwgnxxenz:ff62ee491e09f976ca6ec2c7836fce836d8a1bbc24ee04737f6b3bfe7d48bcbb@ec2-23-23-173-30.compute-1.amazonaws.com:5432/dfufntauabctoa'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)




login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from twitterapi import routes