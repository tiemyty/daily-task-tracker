//Handles client side interactions on creating tasks.
//wait for content to load first
document.addEventListener('DOMContentLoaded', function () {
    alert('JavaScript Loaded');//debug

    //taskForm element and event listener for form submission
    document.getElementById('taskForm').addEventListener('submit', async function (event) {
        event.preventDefault();

        //form input values
        const formData = {
            name: document.getElementById('name').value,
            due_date: document.getElementById('due_date').value,
            priority: document.getElementById('priority').value,
            category: document.getElementById('category').value,
        };

        console.log('Form data:', formData);//debug

        //send request to create_task endpoint
        try {
            const response = await fetch('/create_task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),//convert to json string
            });

            console.log("Response status:", response.status);//debug

            //redirect to login page if not logged in 
            //This may have been my primary issue that login is required failing to create tasks without me knowing.
            if (response.redirected) {
                alert('You are not logged in. Redirecting to login page.');
                window.location.href = response.url;
            } else if (response.status === 201) {
                alert('Task created successfully');//debug
                document.getElementById('taskForm').reset();//reset form
                loadTasks();
            } else {
                alert('Failed to create task');
            }
        } catch (error) {
            console.error('Error:', error); //logs errors to console and notifies user of failure
            alert('Failed to create task');
        }
    });

    //editing tasks form submission
    async function editTask(event) {
        event.preventDefault();

        const taskId = document.getElementById('edit-task-id').value;
        const formData = {
            name: document.getElementById('edit-name').value,
            due_date: document.getElementById('edit-due_date').value,
            priority: document.getElementById('edit-priority').value,
            category: document.getElementById('edit-category').value,
            completed: document.getElementById('edit-completed').checked,
        };

        try {
            const response = await fetch(`/edit_task/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.status === 200) {
                alert('Task updated successfully');
                document.getElementById('editTaskForm').reset();
                loadTasks();
            } else {
                alert('Failed to update task');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to update task');
        }
    }

    //note form submission
    async function addNote(event) {
        event.preventDefault();

        const taskId = document.getElementById('edit-task-id').value;
        const noteContent = document.getElementById('noteContent').value;

        try {
            const response = await fetch(`/add_note/${taskId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: noteContent }),
            });

            if (response.status === 201) {
                alert('Note added successfully');
                loadNotes(taskId);
                document.getElementById('noteForm').reset();
            } else {
                alert('Failed to add note');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to add note');
        }
    }

    //load tasks
    async function loadTasks() {
        try {
            const response = await fetch('/get_tasks');
            console.log('Response:', response);//debug
            const tasks = await response.json();
            console.log('Tasks:', tasks);//debug

            const taskList = document.getElementById('taskList');
            taskList.innerHTML = '';
            tasks.forEach(task => {
                const li = document.createElement('li');
                li.id = `task-${task.id}`;
                li.textContent = `${task.name} - ${task.due_date}`;
                li.innerHTML += ` <button onclick="loadEditForm(${task.id})">Edit</button>`;
                li.innerHTML += ` <button onclick="deleteTask(${task.id})">Delete</button>`;
                li.innerHTML += ` <button onclick="loadNotes(${task.id})">View Notes</button>`;
                taskList.appendChild(li);
            });
        } catch (error) {
            alert('Failed to load tasks');
        }
    }


    //load task details into form
    async function loadEditForm(taskId) {
        try {
            const response = await fetch(`/get_task/${taskId}`);
            const task = await response.json();

            document.getElementById('edit-task-id').value = task.id;
            document.getElementById('edit-name').value = task.name;
            document.getElementById('edit-due_date').value = task.due_date;
            document.getElementById('edit-priority').value = task.priority;
            document.getElementById('edit-category').value = task.category;
            document.getElementById('edit-completed').checked = task.completed;
            document.getElementById('editTaskForm').action = `/edit_task/${task.id}`;
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to load task details');
        }
    }

    //delete tasks
    async function deleteTask(taskId) {
        try {
            const response = await fetch(`/delete_task/${taskId}`, {
                method: 'DELETE',
                headers: {
                },
            });

            if (response.status === 200) {
                alert('Task deleted successfully');
                loadTasks();
            } else {
                alert('Failed to delete task');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to delete task');
        }
    }

    //load notes for task
    async function loadNotes(taskId) {
        try {
            const response = await fetch(`/get_notes/${taskId}`);
            const notes = await response.json();

            const notesList = document.getElementById('notesList');
            notesList.innerHTML = '';
            notes.forEach(note => {
                const li = document.createElement('li');
                li.textContent = note.content;
                notesList.appendChild(li);
            });
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to load notes');
        }
    }

    //load reminders
    async function loadReminders(taskId) {
        try {
            const response = await fetch(`/get_reminders/${taskId}`);
            const reminders = await response.json();

            const reminderList = document.getElementById('reminderList');
            reminderList.innerHTML = '';
            reminders.forEach(reminder => {
                const li = document.createElement('li');
                li.textContent = `${reminder.reminder_time} - ${reminder.message}`;
                reminderList.appendChild(li);
            });
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to load reminders');
        }
    }

    //reminder form submission
    document.getElementById('reminderForm').addEventListener('submit', async function (event) {
        event.preventDefault();
        const taskId = document.getElementById('task-id').value;
        const formData = {
            task_id: taskId,
            reminder_time: document.getElementById('reminder-time').value,
            message: document.getElementById('reminder-message').value
        };

        try {
            const response = await fetch('/create_reminder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.status === 201) {
                alert('Reminder set successfully');
                loadReminders(taskId);
                document.getElementById('reminderForm').reset();
            } else {
                alert('Failed to set reminder');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to set reminder');
        }
    });


    //event listeners
    document.getElementById('editTaskForm').addEventListener('submit', editTask);
    document.getElementById('noteForm').addEventListener('submit', addNote);

    //initial load of tasks
    loadTasks();
});