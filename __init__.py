#The following comments are reminders for when I work on this to activate enviroment. Disregard
#cd C:\Users\tysch\OneDrive\Documents\GitHub\Capstone>
#.\venv\Scripts\activate.bat to activate venv (activate venv)
#python __init__.py (run flask)
#ONLY WORKS IN VSCODE TERMINAL PORT 5000


#Import Flask, SQLAlchemy, Bcrypt, and LoginManager. SQLAlchemy for database, Bcrypt for password hashing, and Login Manager for user session management.
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS #needed for cross data sharing

#Initialize Flask application
app = Flask(__name__, template_folder='templates')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db' #databse name using sqlite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY'] = 'your_secret_key' #placeholder for secret key

#initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  #redirect to login page if not logged in
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from backend.models import User #avoid circular import
    return User.query.get(int(user_id))

#home page
@app.route('/')
def index():
    return render_template('index.html')

#create database tables
with app.app_context():
    print("Creating the database and tables...")
    db.create_all()
    print("Database and tables created successfully.")

    
#import routes
from backend.routes import *

#run flask in debug
if __name__ == '__main__':
    app.run(debug=True, port=5000)