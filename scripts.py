from main import db 
import aiohttp, asyncio
def email_to_id(email):
    print(email, 99)
    return db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()

def get_playlists(email):
    print(email, 100)
    us_id = email_to_id(email)
    playlists = db.execute("SELECT * FROM playlists WHERE owner_id = ?", (us_id[0],)).fetchall()
    return playlists

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