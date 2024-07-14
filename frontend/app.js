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
            user_id: 1  //replace with actual user_id or fetch from backend
        };

        //send request to create_task endpoint
        try {
            const response = await fetch('http://localhost:8080/create_task', {
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
