#The following comments are reminders for when I work on this to activate enviroment. Disregard
#cd C:\Users\tysch\OneDrive\Documents\GitHub\Capstone
#.\venv\Scripts\Activate in vscode powershell
#python __init__.py (run flask)
#ONLY WORKS IN VSCODE TERMINAL PORT 5000
#fix for missing db
#flask db init
#flask db migrate -m "Initial migration."
#flask db upgrade
#$env:FLASK_APP = "__init__.py"

#Import Flask, SQLAlchemy, Bcrypt, and LoginManager. SQLAlchemy for database, Bcrypt for password hashing, and Login Manager for user session management.
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime


#initialize extensions
app = Flask(__name__)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
#app configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['DEBUG'] = True
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
migrate.init_app(app, db)
CORS(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    name = db.Column(db.String(100))
    due_date = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    failed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.relationship('Note', backref='task', lazy=True)
    #reminders = db.relationship('Reminder', backref='task', lazy=True)

    def __repr__(self):
        return f'<Task {self.name}>'
    
#define reminder model
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    reminder_time = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String(255), nullable=False)
    notified = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Reminder {self.id}>'

#define note model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    

#redirect to login page
login_manager.login_view = 'login'


#home route that requires login
#updated to reflect notes underneath tasks and proper task fetching
@app.route('/')
@login_required
def home():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    for task in tasks:
        task.notes = Note.query.filter_by(task_id=task.id).all()
        #task.reminders = Reminder.query.filter_by(task_id=task.id).all() 
    reminders = Reminder.query.all()
    return render_template('index.html', tasks=tasks)

#registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

#logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#necessary to render index when returning from a different html page
@app.route('/')
def index():
    return render_template('index.html')

#create task route
@app.route('/create_task', methods=['POST'])
@login_required
def create_task():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    name = request.form.get('name')
    due_date_str = request.form.get('due_date')
    priority = request.form.get('priority')
    category = request.form.get('category')
    due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
    new_task = Task(name=name, due_date=due_date, priority=priority, category=category, user_id=current_user.id)

    try:
        db.session.add(new_task)
        db.session.commit()
        flash('Task created successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
        print(f"Exception: {e}")

    return redirect(url_for('home'))

#route for deletion
#changed method to post instead of delete
@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    #remove related notes before deleting the task
    notes_to_remove = Note.query.filter_by(task_id=task_id).all()
    for note in notes_to_remove:
        db.session.delete(note)
        
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('home'))

#route for editing a task
@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'POST':
        task.name = request.form['name']
        
        #datetime conversion
        due_date_str = request.form['due_date']
        try:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            return "Invalid date format", 400
        
        task.priority = request.form['priority']
        task.category = request.form['category']
        task.completed = 'completed' in request.form
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_task.html', task=task)


#route for retrieving a single task
@app.route('/get_task/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    task = Task.query.get(task_id)
    if not task or task.user_id != current_user.id:
        return jsonify({'message': 'Task not found'}), 404

    task_data = {'id': task.id,'name': task.name,'due_date': task.due_date.isoformat(),'priority': task.priority,'category': task.category,'completed': task.completed}
    return jsonify(task_data), 200

#route for adding a note to a task
@app.route('/add_note/<int:task_id>', methods=['POST'])
@login_required
def add_note(task_id):
    task = Task.query.get_or_404(task_id)
    content = request.form.get('content')
    
    if content:
        note = Note(content=content, task_id=task_id)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return "Content is required", 400

#route for retrieving notes of a task
@app.route('/get_notes/<int:task_id>', methods=['GET'])
@login_required
def get_notes(task_id):
    task = Task.query.get(task_id)
    if not task or task.user_id != current_user.id:
        return jsonify({'message': 'Task not found'}), 404

    notes = Note.query.filter_by(task_id=task.id).all()
    notes_list = [{'id': note.id, 'content': note.content} for note in notes]
    return jsonify(notes_list), 200

#route for creating reminder
@app.route('/create_reminder', methods=['POST'])
@login_required
def create_reminder():
    #task_id = request.form.get('task_id')
    reminder_time = datetime.strptime(request.form.get('reminder_time'), '%Y-%m-%dT%H:%M')
    message = request.form.get('message')

    reminder = Reminder(reminder_time=reminder_time, message=message)
    db.session.add(reminder)
    db.session.commit()

    return redirect(url_for('home'))

#route to get reminders
@app.route('/get_reminders/<int:task_id>', methods=['GET'])
@login_required
def get_reminders():
    reminders = Reminder.query.all()
    return render_template('index.html', reminders=reminders)

#mark reminder as notified
@app.route('/mark_reminder_notified/<int:reminder_id>', methods=['POST'])
@login_required
def mark_reminder_notified(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    reminder.notified = True
    db.session.commit()
    return '', 204


#route to get tasks
@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', tasks=tasks)

#route to update tasks
@app.route('/tasks/<int:task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    print(f"Received task_id: {task_id}") 
     
    task = Task.query.get_or_404(task_id)
    task.failed = 'failed' in request.form  #updates based on failure
    db.session.commit()
    return redirect(url_for('get_tasks'))


#run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5000)