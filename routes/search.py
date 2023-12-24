from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
from main import download_video

import random, requests
from youtube_search_music import YoutubeMusicSearch
from threadedreturn import ThreadWithReturnValue
from config import GOOGLE_API
from main import db
from scripts import get_playlists

from threadedreturn import ThreadWithReturnValue
search_bp = Blueprint('search', __name__)

@search_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@search_bp.route("/search", methods=["POST", "GET"])
def search():
    if 'email' not in session:
        return redirect(url_for('auth.login'))
    if request.method == "POST":
        query = request.form["search_query"]
        results_json = YoutubeMusicSearch(GOOGLE_API).search(query)

        print(results_json)
        threads = {}
        i = 0
        cleaned_results = list(results_json["items"])
        for result in cleaned_results:
            threads[i] = ThreadWithReturnValue(
                target=download_video, args=(result["id"]["videoId"],)
            )
            threads[i].start()
            i += 1
        for i2 in range(len(threads)):
            status = threads[i2].join()
            if status == "Blacklisted":
                cleaned_results.remove(results_json["items"][i2])

            print(status)

        clean_returned = []
        for result in cleaned_results:
            snippet = result["snippet"]

            try:
                clean_returned.append(
                    {
                        "id": result["id"]["videoId"],
                        "title": snippet["title"],
                        "channel": snippet["channelTitle"],
                        "thumbnail": snippet["thumbnails"]["default"]["url"],
                    }
                )
            except IndexError:
                print(result)
        playlists = get_playlists(session['email'])
        print(clean_returned)
        return render_template("search.html", results=clean_returned, playlists=playlists)
    else:
        return render_template("search.html", results=None)
    
@search_bp.route("/home", methods=["GET"])
async def home():
    print(1)
    songs_list = requests.get("https://musicbackend.lunes.host/list_songs").json()
    songs_info = random.choices(songs_list, k=100)
    if 'email' in session:
        playlists = get_playlists(session['email'])
    else:
        playlists = None

    return render_template('home.html', results=songs_info, playlists=playlists)
    

