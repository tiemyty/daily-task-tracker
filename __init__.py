#The following comments are reminders for when I work on this to activate enviroment. Disregard
#cd C:\Users\tysch\OneDrive\Documents\GitHub\Capstone>
#.\venv\Scripts\activate.bat to activate venv (activate venv)
#python __init__.py (run flask)


#Import Flask, SQLAlchemy, Bcrypt, and LoginManager. SQLAlchemy for database, Bcrypt for password hashing, and Login Manager for user session management.
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS #new necessity for site loading

#Initialize Flask application
app = Flask(__name__)
CORS(app)
#Configure SQLAlchemy part of instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db' #databse name using sqlite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY'] = 'your_secret_key' #placeholder for secret key

#initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  #redirect to login page if not logged in

#import routes and models to register
from backend import routes, models

#run flask in debug
if __name__ == '__main__':
    app.run(debug=True, port=8080)
