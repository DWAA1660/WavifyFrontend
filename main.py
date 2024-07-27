from flask import Flask, current_app, session
import requests
from config import SECRET_KEY
from database import Database

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
db = Database("database.db")
def create_app():


    # Register Blueprints
    from routes.auth import auth_bp
    from routes.playlists import playlists_bp
    from routes.search import search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(playlists_bp)
    app.register_blueprint(search_bp)

    # Create tables within the application context

    return app


def download_video(yt_id: str):
    url = f"https://www.youtube.com/watch?v={yt_id}"
    
    res = requests.post("https://musicbackend.lunes.host/download", headers={"url": url}).text
    print(res)
    return res

if __name__ == "__main__":
    create_app().run("0.0.0.0", port=3014, debug=True)
