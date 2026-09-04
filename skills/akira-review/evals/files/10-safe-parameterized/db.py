from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/user")
def get_user():
    uid = request.args.get("id")
    con = sqlite3.connect("app.db")
    cur = con.execute("SELECT name, email FROM users WHERE id = ?", (uid,))
    return {"rows": cur.fetchall()}
