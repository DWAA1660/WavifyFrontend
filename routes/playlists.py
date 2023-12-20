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
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

playlists_bp = Blueprint('playlists', __name__)

def divide_into_groups(lst, group_size):
    return [lst[i:i + group_size] for i in range(0, len(lst), group_size)]

async def fetch_song_info(session, song):
    url = f"https://musicbackend.lunes.host/song_from_yt_info/{song}"
    async with session.get(url) as response:
        resp = await response.json()
        resp['thumbnail'] = f"https://i.ytimg.com/vi/{song}/default.jpg"
        return resp
async def fetch_all_song_info(songs_list):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_song_info(session, song) for song in songs_list]
        return await asyncio.gather(*tasks)

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
    
    
@playlists_bp.route("/remove_song", methods=["POST"])
def remove_song():

    song_id = request.form["song_id"]
    pl_id = request.form["pl_id"]
    res = db.execute("SELECT * from playlists where owner_id = ? AND id = ?", (email_to_id(session['email'])[0], pl_id)).fetchone()
    if res is not None:
        old_songs = res[2]
        if old_songs is None:
            old_songs = ""
        old_songs_list = old_songs.split("&&")
        print(old_songs_list, song_id)
        old_songs_list.remove(song_id)
        
        new_songs = '&&'.join(old_songs_list)
        db.execute("UPDATE playlists SET songs = ? WHERE id = ?", (new_songs, pl_id))
        return "Success"
    else:
        return "ur not owner"
        
        
@playlists_bp.route("/playlist/<pl_id>", methods=["GET"])
async def play_playlist(pl_id: str):
    request_time = time.time()
    print(time.time() - request_time, 1)
    res = db.execute("SELECT * from playlists where id = ?", (pl_id,)).fetchone()
    print(time.time() - request_time, 2)
    if res is None:
        return "This playlist doesnt exist"
    try:
        songs_list: list=res[2].split("&&")
        songs_list.remove("")
    except:
        songs_list = []
        
    if songs_list == []:
        return render_template('playlist.html', results=None)
    print(time.time() - request_time, 3)
    threads = {}
    i = 0
    cleaned_results = await fetch_all_song_info(songs_list)
    print(time.time() - request_time, 5)
    owner_name = db.execute("SELECT display_name from users where id = ?", (res[1],)).fetchone()
    print(time.time() - request_time, 6)
    return render_template('playlist.html', results=cleaned_results, name=res[3], owner=owner_name[0], pl_id=pl_id)
    

@playlists_bp.route("/spotify", methods=["GET", "POST"])
def spotify():
    pl_id = request.args["pl_id"]
    page = request.args.get("page", 0)
    print(pl_id)
    if 'email' not in session:
        return redirect(url_for('auth.login'))
    clean_returned = []
    songs = get_all_song_names(pl_id)
    grouped_songs = divide_into_groups(songs, 10)

    def process_song(song):

        try:
            results_json = YoutubeSearch(song, max_results=1).to_dict()
            if results_json:
                result = results_json[0]
                print(result, 1.5)
                ThreadWithReturnValue(target=download_video, args=(result["id"],)).start()
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
            else:
                print("No results found for:", song)
        except Exception as e:
            print(e, 1)

    print(songs, page)
    with ThreadPoolExecutor(max_workers=4) as executor:
        
        executor.map(process_song, grouped_songs[int(page)])

    playlists = get_playlists(session['email'])
    return render_template("search.html", results=clean_returned, playlists=playlists)


