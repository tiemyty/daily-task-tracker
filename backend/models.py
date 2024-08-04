from backend import db
from flask_login import UserMixin
from datetime import datetime

#define user model. primary key, username, email, password, and relationship to task
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    tasks = db.relationship('Task', backref='author', lazy=True)
    
#define task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False, default=datetime)
    priority = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    failed = db.Column(db.Boolean, default=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.relationship('Note', backref='task', lazy=True)
    reminders = db.relationship('Reminder', backref='task', lazy=True)
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
#define reminder model
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reminder_time = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String(255), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)


#define note model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
