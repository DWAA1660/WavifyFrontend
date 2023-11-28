from flask import *
from youtube_search_music import YoutubeMusicSearch
import requests
import threading
import json
from threadedreturn import ThreadWithReturnValue
from config import GOOGLE_API

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

def download_video(yt_id: str):
    url= f"https://www.youtube.com/watch?v={yt_id}"
    
    res = requests.post("http://node2.lunes.host:27237/download", headers={"url": url}).text
    print(res)
    return res
    

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
            
        print(2)
        print(threads)
        for i2 in range(len(threads)):
            print(2.5)

            status = threads[i2].join()
            if status == "Blacklisted":
                cleaned_results.remove(results_json['videos'][i2])
                
            print(status)
            
        print(3)
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