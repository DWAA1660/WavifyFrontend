from flask import Blueprint, render_template, redirect, url_for, request, current_app, session
from models.playlists import Playlists
from main import db, download_video
from scripts import email_to_id
from sqlalchemy import Integer, String, text
from youtube_search import YoutubeSearch
from spotify import get_all_song_names
from proxy import get_proxy
import os
from threadedreturn import ThreadWithReturnValue
from concurrent.futures import ThreadPoolExecutor

playlists_bp = Blueprint('playlists', __name__)

@playlists_bp.route("/playlist-create", methods=["GET", "POST"])
def create_playlist():
    if session['email'] is None:
        return redirect(url_for('login'))
    if request.method == "POST":
        name = request.form.get("name")
        owner_id = email_to_id(session['email'])
        with current_app.app_context():
            db.session.add(Playlists(name=name, owner_id=owner_id, songs=""))
            db.session.commit()
    return render_template('playlists.html')

@playlists_bp.route("/playlists")
def playlist():
    return render_template('playlists.html')

@playlists_bp.route("/playlist", methods=["GET", "POST"])
def spotify():
    pl_id = request.args["pl_id"]
    print(pl_id)
    clean_returned = []
    songs = get_all_song_names(pl_id)

    def process_song(song):
        try:
            proxy = get_proxy()
            print(proxy)
            os.environ["HTTP_PROXY"] = proxy
            try:
                results_json = YoutubeSearch(song, max_results=1).to_dict()
                del os.environ["HTTP_PROXY"]
                try:
                    result = results_json[0]
                except KeyError:
                    print(results_json)
                ThreadWithReturnValue(
                    target=download_video, args=(result["id"],)
                ).start()

                try:
                    clean_returned.append(
                        {
                            "id": result["id"],
                            "title": result["title"],
                            "channel": result["channel"],
                            "thumbnail": result["thumbnails"][0],
                        }
                    )
                except IndexError:
                    print(result)
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)

    with ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(process_song, songs)

    return render_template("playlist.html", results=clean_returned)


