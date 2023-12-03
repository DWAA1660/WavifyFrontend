from main import db 
def email_to_id(email):
    print(email, 99)
    return db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()

def get_playlists(email):
    print(email, 100)
    us_id = email_to_id(email)
    playlists = db.execute("SELECT * FROM playlists WHERE owner_id = ?", (us_id[0],)).fetchall()
    return playlists