from flask import Blueprint, render_template, request, current_app
from main import download_video

from youtube_search_music import YoutubeMusicSearch
from threadedreturn import ThreadWithReturnValue
from config import GOOGLE_API
from sqlalchemy import text
from main import db

from threadedreturn import ThreadWithReturnValue
search_bp = Blueprint('search', __name__)

@search_bp.route("/", methods=["GET"])
def index():
    with current_app.app_context():
        print(db.session.execute(text("SELECT * FROM user")).fetchone())

    return render_template("index.html")


@search_bp.route("/search", methods=["POST", "GET"])
def search():
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

        return render_template("search.html", results=clean_returned)
    else:
        return render_template("search.html", results=None)

