from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests

from config import SECRET_KEY

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    # Initialize Flask extensions
    db.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.playlists import playlists_bp
    from routes.search import search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(playlists_bp)
    app.register_blueprint(search_bp)

    # Create tables within the application context
    with app.app_context():
        db.create_all()

    return app

def download_video(yt_id: str):
    url = f"https://www.youtube.com/watch?v={yt_id}"
    
    res = requests.post("https://musicbackend.lunes.host/download", headers={"url": url}).text
    print(res)
    return res

if __name__ == "__main__":
    create_app().run("0.0.0.0", port=27163, debug=True)
