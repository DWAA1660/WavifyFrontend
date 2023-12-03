from main import db 
def email_to_id(email):
    print(email)
    return db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()