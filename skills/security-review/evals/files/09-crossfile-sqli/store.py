import sqlite3

def find_account(acct):
    con = sqlite3.connect("app.db")
    return con.execute("SELECT * FROM accounts WHERE acct = '" + acct + "'").fetchall()
