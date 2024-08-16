const socket = io();

document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username}),
    }).then(response => {
        if (response.ok) {
            document.getElementById('auth').style.display = 'none';
            document.getElementById('chat').style.display = 'block';
        }
    });
});

document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('password').value;
    fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password}),
    }).then(response => {
        if (response.ok) {
            document.getElementById('auth').style.display = 'none';
            document.getElementById('chat').style.display = 'block';
        }
    });
});

document.getElementById('sendMessageForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const message = document.getElementById('message').value;
    socket.emit('chatMessage', message);
    document.getElementById('message').value = '';
});

socket.on('message', function(data) {
    const messages = document.getElementById('messages');
    messages.innerHTML += `<p><strong>${data.user}:</strong> ${data.text}</p>`;
    messages.scrollTop = messages.scrollHeight;
});
