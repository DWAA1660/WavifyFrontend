from main import db
from sqlalchemy import text

def email_to_id(email: str, app):
    with app.app_context():
        res  = db.session.get(text("SELECT id from user where email = :email"), {"email": email}).fetchone()[0]
        print(res)
        return res