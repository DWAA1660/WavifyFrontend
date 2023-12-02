from flask import Blueprint, render_template, redirect, url_for, request, current_app, session
from models.user import User
from main import db, create_app
from sqlalchemy import Integer, String, text

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        with current_app.app_context():
            res = db.session.execute(text("SELECT * FROM user WHERE email = :email AND password = :password"), {"email": email, "password": password}).fetchone()
            if res is not None:
                session['email'] = email
                return redirect(url_for('index'))
            else:
                return "WRONG LOSER"
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle registration logic here
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        res = db.session.execute(text("SELECT * FROM user WHERE email = :email"), {"email": email}).fetchone()
        print(res)
        if res is None:
            with current_app.app_context():
                #this is currently unhashed for debugging purposes i know to not do this
                db.session.add(User(email=email, username=username, password=password))
                db.session.commit()
        else:
            return "your already registered"
        return redirect(url_for('login'))
    return render_template('register.html')
