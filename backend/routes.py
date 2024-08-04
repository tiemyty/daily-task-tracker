#import necessary functions for flask 
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from backend import db, bcrypt
from backend.models import User, Task, Note, Reminder
from datetime import datetime

bp = Blueprint('main', __name__)

#home route that requires login
@bp.route('/')
def home():
    return render_template('index.html')

#registration route
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

#login route
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

#logout route
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

#create task route
@bp.route('/create_task', methods=['POST'])
#@login_required
def create_task():
    name = request.form.get('name')
    due_date = request.form.get('due_date')
    priority = request.form.get('priority')
    category = request.form.get('category')
    user_id = 1  #bypass temporarily
    new_task = Task(name=name, due_date=due_date, priority=priority, category=category, user_id=user_id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('main.home'))

#route for deletion
@bp.route('/delete_task/<int:task_id>', methods=['DELETE'])
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
@bp.route('/edit_task/<int:task_id>', methods=['PUT'])
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
@bp.route('/get_task/<int:task_id>', methods=['GET'])
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
@bp.route('/add_note/<int:task_id>', methods=['POST'])
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
@bp.route('/get_notes/<int:task_id>', methods=['GET'])
@login_required
def get_notes(task_id):
    task = Task.query.get(task_id)
    if not task or task.user_id != current_user.id:
        return jsonify({'message': 'Task not found'}), 404

    notes = Note.query.filter_by(task_id=task.id).all()
    notes_list = [{'id': note.id, 'content': note.content} for note in notes]
    return jsonify(notes_list), 200

#route for creating reminder
@bp.route('/create_reminder', methods=['POST'])
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
@bp.route('/get_reminders/<int:task_id>', methods=['GET'])
@login_required
def get_reminders(task_id):
    task = Task.query.get(task_id)
    if not task or task.user_id != current_user.id:
        return jsonify({'message': 'Task not found'}), 404

    reminders = Reminder.query.filter_by(task_id=task_id).all()
    reminders_list = [{'id': reminder.id, 'reminder_time': reminder.reminder_time.isoformat(), 'message': reminder.message} for reminder in reminders]
    return jsonify(reminders_list), 200

#get tasks
@bp.route('/get_tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    task_list = [{'id': task.id, 'name': task.name} for task in tasks]
    return jsonify(task_list)

#route to update tasks
@bp.route('/tasks/<int:task_id>/update', methods=['POST'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.failed = 'failed' in request.form  #updates based on failure
    db.session.commit()
    return redirect(url_for('tasks.list_tasks'))