from flask import Blueprint, render_template, redirect, url_for, request, current_app, session
from main import create_app, db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(email, password)
        res = db.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password,)).fetchone()
        print(res)
        if res is not None:
            session.permanent = True 
            session['email'] = email
            session.permanent = True 
            return redirect(url_for('search.index'))
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
        with current_app.app_context():
            res = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            print(res)
            if res is None:
                #this is currently unhashed for debugging purposes i know to not do this
                db.execute("INSERT INTO users (username, email, password, display_name) VALUES (?, ?, ?, ?)", (username, email, password, username))

            else:
                return "your already registered"
            return redirect(url_for('auth.login'))
    return render_template('register.html')
