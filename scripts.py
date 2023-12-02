from main import db
from sqlalchemy import text
from flask import current_app

def email_to_id(email: str):
    with current_app.app_context():
        return db.session.execute(text("SELECT id from user where email = :email"), {"email": email})