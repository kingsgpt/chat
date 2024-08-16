const express = require('express');
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
