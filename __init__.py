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
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime


#initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    #redirect to login page
    login_manager.login_view = 'login'


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
        name = db.Column(db.String, nullable=False)
        due_date = db.Column(db.DateTime, nullable=False)
        priority = db.Column(db.String, nullable=False)
        category = db.Column(db.String, nullable=False)
        completed = db.Column(db.Boolean, default=False)
        failed = db.Column(db.Boolean, default=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        notes = db.relationship('Note', backref='task', lazy=True)
        reminders = db.relationship('Reminder', backref='task', lazy=True)
    
        def __repr__(self):
            return f'<Task {self.name}>'
        
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
        
    #home route that requires login
    @app.route('/')
    @login_required
    def home():
        tasks = get_tasks()
        return render_template('index.html')
    
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

    #create task route
    @app.route('/create_task', methods=['POST'])
    @login_required
    def create_task():
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        name = request.form.get('name')
        due_date = request.form.get('due_date')
        priority = request.form.get('priority')
        category = request.form.get('category')
        print(f"Name: {name}, Due Date: {due_date}, Priority: {priority}, Category: {category}")

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
    @app.route('/delete_task/<int:task_id>', methods=['DELETE'])
    @login_required
    def delete_task(task_id):
        task = Task.query.get(task_id)
        if task and task.user_id == current_user.id:
            db.session.delete(task)
            db.session.commit()
            return jsonify({'message': 'Task deleted successfully'}), 200
        else:
            return jsonify({'message': 'Task not found'}), 404

    #route for editing a task
    @app.route('/edit_task/<int:task_id>', methods=['PUT'])
    @login_required
    def edit_task(task_id):
        task = Task.query.get(task_id)
        if not task or task.user_id != current_user.id:
            return jsonify({'message': 'Task not found'}), 404

        data = request.get_json()
        task.name = data.get('name', task.name)
        task.due_date = data.get('due_date', task.due_date)
        task.priority = data.get('priority', task.priority)
        task.category = data.get('category', task.category)
        task.completed = data.get('completed', task.completed)

        db.session.commit()
        return jsonify({'message': 'Task updated successfully'}), 200

    #route for retrieving a single task
    @app.route('/get_task/<int:task_id>', methods=['GET'])
    @login_required
    def get_task(task_id):
        task = Task.query.get(task_id)
        if not task or task.user_id != current_user.id:
            return jsonify({'message': 'Task not found'}), 404

        task_data = {
            'id': task.id,
            'name': task.name,
            'due_date': task.due_date.isoformat(),
            'priority': task.priority,
            'category': task.category,
            'completed': task.completed
        }
        return jsonify(task_data), 200

    #route for adding a note to a task
    @app.route('/add_note/<int:task_id>', methods=['POST'])
    @login_required
    def add_note(task_id):
        task = Task.query.get(task_id)
        if not task or task.user_id != current_user.id:
            return jsonify({'message': 'Task not found'}), 404

        content = request.json.get('content')
        if not content:
            return jsonify({'message': 'Content is required'}), 400

        new_note = Note(task_id=task.id, content=content)
        db.session.add(new_note)
        db.session.commit()
        return jsonify({'message': 'Note added successfully'}), 201

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
        data = request.get_json()
        task_id = data.get('task_id')
        reminder_time = datetime.fromisoformat(data.get('reminder_time'))
        message = data.get('message')

        new_reminder = Reminder(task_id=task_id, reminder_time=reminder_time, message=message)
        db.session.add(new_reminder)
        db.session.commit()
        return jsonify({'message': 'Reminder created successfully'}), 201
    
    #route to get reminders
    @app.route('/get_reminders/<int:task_id>', methods=['GET'])
    @login_required
    def get_reminders(task_id):
        task = Task.query.get(task_id)
        if not task or task.user_id != current_user.id:
            return jsonify({'message': 'Task not found'}), 404

        reminders = Reminder.query.filter_by(task_id=task_id).all()
        reminders_list = [{'id': reminder.id, 'reminder_time': reminder.reminder_time.isoformat(), 'message': reminder.message} for reminder in reminders]
        return jsonify(reminders_list), 200

    #route to get tasks
    @app.route('/get_tasks', methods=['GET'])
    def get_tasks():
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        return render_template('index.html', tasks=tasks)

    #route to update tasks
    @app.route('/tasks/<int:task_id>/update', methods=['POST'])
    def update_task(task_id):
        task = Task.query.get_or_404(task_id)
        task.failed = 'failed' in request.form  #updates based on failure
        db.session.commit()
        return redirect(url_for('get_tasks'))

    return app

#run
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)