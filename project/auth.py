from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from . import db
from .models import User, FileAccess, File

# Initialize the blueprint for authentication routes
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
        Handle user login functionality.

        Validates the provided username and password, then logs the user in if valid.
        If unsuccessful, flashes an error message.

        Returns:
            Rendered login template if GET request, redirect to profile if POST request is successful.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        return redirect(url_for('main.profile'))
    return render_template('login.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """
        Handle user registration functionality.

        Checks if the username already exists, validates the passwords, and creates a new user.
        Assigns the new user permissions for all existing files.

        Returns:
            Redirect to the login page if registration is successful, else renders the signup form.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('password')
        repeated_password = request.form.get('password_2')

        # Check if user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('User already exists')
            return redirect(url_for('auth.signup'))

        if password != repeated_password:
            flash('Your password is incorrect.')
            return redirect(url_for('auth.signup'))

        # Create and add new user to the database
        new_user = User(username=username, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()

        # Assign permissions for all files to the new user
        all_files = File.query.all()
        for file in all_files:
            new_user_permissions = FileAccess(user_id=new_user.id, file_id=file.id, permission=True)
            db.session.add(new_user_permissions)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('signup.html')


@auth.route('/logout')
@login_required
def logout():
    """
        Handle user logout functionality.

        Logs out the current user and redirects them to the homepage.

        Returns:
            Redirect to the index route after logging out.
    """
    logout_user()
    return redirect(url_for('main.index'))
