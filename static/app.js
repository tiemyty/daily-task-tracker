//Handles client side interactions on creating tasks.

//wait for content to load first
document.addEventListener('DOMContentLoaded', function () {

    //taskForm element and event listener for form submission
    const taskForm = document.getElementById('taskForm');

    taskForm.addEventListener('submit', async function (event) {
        event.preventDefault();//prevents default form submission


        //form input values
        const formData = {
            name: document.getElementById('name').value,
            due_date: document.getElementById('due_date').value,
            priority: document.getElementById('priority').value,
            category: document.getElementById('category').value,
            user_id: 1
        };

        //send request to create_task endpoint
        try {
            const response = await fetch('/create_task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)//convert to json string
            });

            //request successful = 201 - created
            if (response.status === 201) {
                alert('Task created successfully'); //notify user it was successful
                taskForm.reset(); //resets form
            } else {
                alert('Failed to create task'); //notify user of failure
            }
        } catch (error) {
            console.error('Error:', error); //logs errors to console and notifies user of failure
            alert('Failed to create task');
        }
        
        
    })
});

//function for deleting tasks
async function deleteTask(taskId) {
    try {
        const response = await fetch(`/delete_task/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            document.getElementById(`task-${taskId}`).remove();
            alert('Task deleted successfully');
        } else {
            alert('Failed to delete task');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete task');
    }
}
