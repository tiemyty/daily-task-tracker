#import necessary functions for flask 
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from __init__ import app, db, bcrypt
from backend.models import User, Task, Note
from datetime import datetime

#home route that requires login
@app.route('/')
@login_required
def home():
    return f"Hello, {current_user.username}!"

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
#@login_required
def create_task():
    data = request.get_json()
    print(f"Received data: {data}")

    name = data.get('name')
    due_date = data.get('due_date')
    priority = data.get('priority')
    category = data.get('category')
   # user_id = current_user.id

    if not all([name, due_date, priority, category]):
        print("Missing data")
        return jsonify({'message': 'Invalid data'}), 400
    
    user_id = 1 #hard coded user id to bypass login
    due_date = datetime.fromisoformat(due_date)
    
    #create task
    new_task = Task(name=name, due_date=due_date, priority=priority, category=category, user_id=user_id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'}), 201

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

#@app.route('/get_tasks', methods=['GET'])
#@login_required
#def get_tasks():
 #   print("get_tasks route hit")#debug
 #   tasks = Task.query.filter_by(user_id=current_user.id).all()
  #  tasks_list = [{'id': task.id, 'name': task.name, 'due_date': task.due_date.isoformat(), 'priority': task.priority, 'category': task.category, 'completed': task.completed} for task in tasks]
  #  return jsonify(tasks_list)

print(app.url_map)#debug