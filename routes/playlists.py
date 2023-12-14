from flask import Blueprint, render_template, redirect, url_for, request, current_app, session
from main import db, download_video
from scripts import email_to_id
from youtube_search import YoutubeSearch
from spotify import get_all_song_names
from proxy import get_proxy
import os, json, time
from scripts import get_playlists
import requests
from threadedreturn import ThreadWithReturnValue
from concurrent.futures import ThreadPoolExecutor

playlists_bp = Blueprint('playlists', __name__)

def get_song_info(yt_id: str):
    resp = requests.get(f"https://musicbackend.lunes.host/song_from_yt_info/{yt_id}").text
    return json.loads(resp)

@playlists_bp.route("/playlist-create", methods=["GET", "POST"])
def create_playlist():
    if session['email'] is None:
        return redirect(url_for('login'))
    if request.method == "POST":
        name = request.form.get("name")
        with current_app.app_context():
            owner_id = email_to_id(session['email'])
            if owner_id is not None:
                db.execute("INSERT INTO playlists (owner_id, name) VALUES (?, ?)", (owner_id[0], name))
    return redirect(url_for('playlists.playlist'))

@playlists_bp.route("/playlists")
def playlist():
    if 'email' not in session:
        return redirect(url_for('auth.login'))
    user_id = email_to_id(session['email'])
    if user_id is None:
        return redirect(url_for('auth.register'))
    playlists_json = []
    playlists = db.execute("SELECT * FROM playlists WHERE owner_id = ?", (user_id[0],)).fetchall()
    for playlist in playlists:
        playlists_json.append({"id": playlist[0], "owner_id": playlist[1], "songs":playlist[2], "name": playlist[3]})
    return render_template('playlists.html', playlists=playlists_json)

@playlists_bp.route("/add_song", methods=["POST"])
def add_song():

    song_id = request.form["song_id"]
    pl_id = request.form["pl_id"]
    res = db.execute("SELECT * from playlists where owner_id = ? AND id = ?", (email_to_id(session['email'])[0], pl_id)).fetchone()
    if res is not None:
        old_songs = res[2]
        if old_songs is None:
            old_songs = ""
        new_songs = f"{old_songs}&&{song_id}"
        db.execute("UPDATE playlists SET songs = ? WHERE id = ?", (new_songs, pl_id))
        return "Success"
        
@playlists_bp.route("/playlist/<pl_id>", methods=["GET"])
def play_playlist(pl_id: str):
    request_time = time.time()
    print(time.time() - request_time, 1)
    res = db.execute("SELECT * from playlists where id = ?", (pl_id,)).fetchone()
    print(time.time() - request_time, 2)
    if res is None:
        return "This playlist doesnt exist"
    try:
        songs_list=res[2].split("&&")
        songs_list.remove(songs_list[0])
    except AttributeError:
        songs_list = []
        
    if songs_list == []:
        return render_template('playlist.html', results=None)
    print(time.time() - request_time, 3)
    threads = {}
    i = 0
    for song in songs_list:
        threads[i] = ThreadWithReturnValue(target=get_song_info, args=(song,))
        threads[i].start()
        i += 1
    print(time.time() - request_time, 4)
    cleaned_results = []
    
    for i in range(len(threads)):
        info = threads[i].join()
        if info is not None:
            info['thumbnail'] = f"https://img.youtube.com/vi/{info['yt_id']}/0.jpg"
            cleaned_results.append(info)
    print(time.time() - request_time, 5)
    owner_name = db.execute("SELECT display_name from users where id = ?", (res[1],)).fetchone()
    print(time.time() - request_time, 6)
    return render_template('playlist.html', results=cleaned_results, name=res[3], owner=owner_name[0])
    

@playlists_bp.route("/spotify", methods=["GET", "POST"])
def spotify():
    pl_id = request.args["pl_id"]
    print(pl_id)
    if 'email' not in session:
        return redirect(url_for('auth.login'))
    clean_returned = []
    songs = get_all_song_names(pl_id)

    def process_song(song):
        try:
            # proxy = get_proxy()
            # print(proxy)
            # os.environ["HTTP_PROXY"] = proxy
            try:
                results_json = YoutubeSearch(song, max_results=1).to_dict()
                # del os.environ["HTTP_PROXY"]
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

    playlists = get_playlists(session['email'])
    return render_template("search.html", results=clean_returned, playlists=playlists)


