import os

# Define the file structure and code
file_structure = {
    'public': {
        'index.html': """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat App</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="auth">
        <form id="loginForm">
            <input type="text" id="username" placeholder="Username" required>
            <button type="submit">Login</button>
        </form>
        <form id="registerForm">
            <input type="text" id="regUsername" placeholder="Username" required>
            <input type="password" id="password" placeholder="Password" required>
            <button type="submit">Register</button>
        </form>
    </div>
    <div id="chat" style="display:none;">
        <div id="messages"></div>
        <form id="sendMessageForm">
            <input type="text" id="message" placeholder="Message" required>
            <button type="submit">Send</button>
        </form>
    </div>
    <script src="/socket.io/socket.io.js"></script>
    <script src="app.js"></script>
</body>
</html>
""",
        'styles.css': """/* Add your CSS styling here */
body {
    font-family: Arial, sans-serif;
}
#auth, #chat {
    padding: 20px;
}
#messages {
    border: 1px solid #ccc;
    height: 300px;
    overflow-y: scroll;
}
""",
        'app.js': """const socket = io();

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
""",
    },
    'server': {
        'models': {
            'User.js': """const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    username: String,
    password: String
});

module.exports = mongoose.model('User', userSchema);
""",
        },
        'routes': {
            'auth.js': """const express = require('express');
const passport = require('passport');
const User = require('../models/User');
const router = express.Router();

router.post('/register', (req, res) => {
    const { username, password } = req.body;
    const user = new User({ username, password });
    user.save((err) => {
        if (err) return res.status(500).send('Error registering user');
        res.sendStatus(200);
    });
});

router.post('/login', passport.authenticate('local'), (req, res) => {
    res.sendStatus(200);
});

module.exports = router;
""",
        },
        'server.js': """const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const mongoose = require('mongoose');
const session = require('express-session');
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const User = require('./models/User');
const authRoutes = require('./routes/auth');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

mongoose.connect('mongodb://localhost/chat-app', { useNewUrlParser: true, useUnifiedTopology: true });

app.use(express.static('public'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use(session({ secret: 'secret', resave: false, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

passport.use(new LocalStrategy(
    (username, password, done) => {
        User.findOne({ username }, (err, user) => {
            if (err) return done(err);
            if (!user || password !== user.password) return done(null, false);
            return done(null, user);
        });
    }
));

passport.serializeUser((user, done) => done(null, user.id));
passport.deserializeUser((id, done) => {
    User.findById(id, (err, user) => {
        done(err, user);
    });
});

app.use('/auth', authRoutes);

io.on('connection', (socket) => {
    console.log('New user connected');

    socket.on('chatMessage', (msg) => {
        io.emit('message', { user: socket.username, text: msg });
    });

    socket.on('disconnect', () => {
        console.log('User disconnected');
    });
});

server.listen(3000, () => {
    console.log('Server running on http://localhost:3000');
});
""",
    },
    '.gitignore': """node_modules/
.env
""",
    'package.json': """{
  "name": "chat-app",
  "version": "1.0.0",
  "description": "A real-time chat application",
  "main": "server/server.js",
  "scripts": {
    "start": "node server/server.js"
  },
  "dependencies": {
    "express": "^4.17.1",
    "mongoose": "^6.0.0",
    "passport": "^0.5.0",
    "passport-local": "^1.0.0",
    "socket.io": "^4.0.0",
    "express-session": "^1.17.1"
  }
}
""",
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # Ensure directories exist before creating files
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as file:
                file.write(content)

# Create the file structure
create_structure('.', file_structure)
