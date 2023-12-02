from flask import *
from youtube_search_music import YoutubeMusicSearch
import requests
import threading
import json
from spotify import get_all_song_names
from threadedreturn import ThreadWithReturnValue
from config import GOOGLE_API
from youtube_search import YoutubeSearch
import os
from proxy import get_proxy
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

def download_video(yt_id: str):
    url= f"https://www.youtube.com/watch?v={yt_id}"
    
    res = requests.post("https://musicbackend.lunes.host/download", headers={"url": url}).text
    print(res)
    return res


@app.route("/playlist", methods=["GET", "POST"])
def spotify():
    pl_id = request.args['pl_id']
    print(pl_id)
    clean_returned = []
    songs = get_all_song_names(pl_id)

    def process_song(song):
        try:
            proxy = get_proxy()
            print(proxy)
            os.environ['HTTP_PROXY'] = proxy
            try:
                results_json = YoutubeSearch(song, max_results=1).to_dict()
                del os.environ['HTTP_PROXY']
                try:
                    result = results_json[0]
                except KeyError:
                    print(results_json)
                ThreadWithReturnValue(target=download_video, args=(result['id'],)).start()

                try:
                    clean_returned.append({"id": result['id'], "title": result['title'], "channel": result['channel'],
                                        "thumbnail": result['thumbnails'][0]})
                except IndexError:
                    print(result)
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_song, songs)

    return render_template("search.html", results=clean_returned)

@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        query = request.form['search_query']
        results_json = YoutubeMusicSearch(GOOGLE_API).search(query)
        
        print(results_json)
        threads = {}
        i = 0
        cleaned_results = list(results_json['items'])
        for result in cleaned_results:
            threads[i] = ThreadWithReturnValue(target=download_video, args=(result['id']['videoId'],))
            threads[i].start()
            i += 1
        for i2 in range(len(threads)):
            status = threads[i2].join()
            if status == "Blacklisted":
                cleaned_results.remove(results_json['items'][i2])
                
            print(status)
            
        clean_returned = []
        for result in cleaned_results:
            snippet = result['snippet']
            
            try:
                clean_returned.append({"id": result['id']['videoId'], "title": snippet['title'], "channel": snippet['channelTitle'],
                                    "thumbnail": snippet['thumbnails']['default']['url']})
            except IndexError:
                print(result)
            
        return render_template("search.html", results=clean_returned)

if __name__ == "__main__":
    app.run("0.0.0.0", port=27163)