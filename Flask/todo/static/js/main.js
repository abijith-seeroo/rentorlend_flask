// main.js

// Handle user login
document.getElementById('loginForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    console.log("hiiiiii")

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok) {
        // Save the JWT token in localStorage
        localStorage.setItem('token', data.token);

        // Redirect to dashboard
        window.location.href = '/dashboard';
    } else {
        alert('Login failed. Please try again.');
    }
});

// Load to-do list when on dashboard
if (window.location.pathname === '/dashboard') {
    loadTodoList();

    document.getElementById('todoForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        const todoText = document.getElementById('todoText').value;

        // Create a new todo item
        await fetch('/todo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-access-token': localStorage.getItem('token') // Attach the token
            },
            body: JSON.stringify({ text: todoText })
        });

        document.getElementById('todoText').value = '';
        loadTodoList(); // Reload the todo list
    });
}

// Function to load all to-do items for the user
async function loadTodoList() {
    const response = await fetch('/todo', {
        method: 'GET',
        headers: {
            'x-access-token': localStorage.getItem('token') // Attach the token
        }
    });

    const data = await response.json();
    const todoList = document.getElementById('todoList');

    todoList.innerHTML = ''; // Clear the existing list

    data['Todo list'].forEach(todo => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.textContent = todo.text;
        todoList.appendChild(listItem);
    });
}
