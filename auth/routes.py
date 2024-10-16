from flask import render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User
from . import auth

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password'])
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(username=data['username']).first()
        if user and check_password_hash(user.password_hash, data['password']):
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('auth/login.html')
