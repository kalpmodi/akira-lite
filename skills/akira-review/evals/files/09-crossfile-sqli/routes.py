from flask import Flask, request
from store import find_account

app = Flask(__name__)

@app.route("/account")
def account():
    acct = request.args.get("acct")
    return {"rows": find_account(acct)}
