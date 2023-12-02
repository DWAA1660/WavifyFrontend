from main import db

class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(255), nullable=False)
        email = db.Column(db.String(255), nullable=False, primary_key=True)
        password = db.Column(db.String(255), nullable=False)
