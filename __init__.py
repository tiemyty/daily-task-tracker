#The following comments are reminders for when I work on this to activate enviroment. Disregard
#cd C:\Users\tysch\OneDrive\Documents\GitHub\Capstone
#.\venv\Scripts\activate.bat to activate venv (activate venv)
#python __init__.py (run flask)
#ONLY WORKS IN VSCODE TERMINAL PORT 5000
#fix for missing db
#flask db init
#flask db migrate -m "Initial migration."
#flask db upgrade
#$env:FLASK_APP="Capstone"



#Import Flask, SQLAlchemy, Bcrypt, and LoginManager. SQLAlchemy for database, Bcrypt for password hashing, and Login Manager for user session management.
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS #needed for cross data sharing
from flask_migrate import Migrate
from backend import db, bcrypt


#initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/taskmanager.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    from backend.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    @login_manager.user_loader
    def load_user(user_id):
        from backend.models import User #avoid circular import
        return User.query.get(int(user_id))

    return app

#run flask in debug
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)