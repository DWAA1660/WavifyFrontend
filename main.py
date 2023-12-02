from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
import requests
from sqlalchemy import Integer, String, text
from config import SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy()
db.init_app(app)

def create_app():

    class Playlists(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        owner_id = db.Column(db.Integer, nullable=False)
        name = db.Column(db.String(255), nullable=False)

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(255), nullable=False)
        email = db.Column(db.String(255), nullable=False, primary_key=True)
        password = db.Column(db.String(255), nullable=False)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.playlists import playlists_bp
    from routes.search import search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(playlists_bp)
    app.register_blueprint(search_bp)

    # Create tables within the application context
    with app.app_context():
        print("making tables")
        db.create_all()
        print(db.session.execute(text("SELECT * FROM user")).fetchone())

    return app


def download_video(yt_id: str):
    url = f"https://www.youtube.com/watch?v={yt_id}"
    
    res = requests.post("https://musicbackend.lunes.host/download", headers={"url": url}).text
    print(res)
    return res

if __name__ == "__main__":
    create_app().run("0.0.0.0", port=27163, debug=True)
