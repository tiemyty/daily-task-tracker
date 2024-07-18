#import necessary functions for flask 
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from __init__ import app, db, bcrypt
from backend.models import User, Task

#home route that requires login
@app.route('/')
#@login_required
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
    return render_template('login.html')

#create task route
@app.route('/create_task', methods=['POST'])
def create_task():
    data = request.get_json()
    print(f"Received data: {data}")#debug

    name = request.json.get('name')
    due_date = request.json.get('due_date')
    priority = request.json.get('priority')
    category = request.json.get('category')
    user_id = request.json.get('user_id')  #ensure user_id is passed from frontend or current_user.id

    if not all([name, due_date, priority, category, user_id]):
        return jsonify({'message': 'Invalid data'}), 400
    
    #create task
    new_task = Task(name=name, due_date=due_date, priority=priority, category=category, user_id=user_id)
    db.session.add(new_task)
    db.session.commit()
    #status 201 means it is a success
    return jsonify({'message': 'Task created successfully'}), 201

#route for deletion
@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'}), 200
    else:
        return jsonify({'message': 'Task not found'}), 404