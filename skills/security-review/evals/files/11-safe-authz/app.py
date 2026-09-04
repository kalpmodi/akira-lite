from flask import Flask, session, jsonify

app = Flask(__name__)
ORDERS = {}

@app.route("/order/<oid>")
def order(oid):
    o = ORDERS.get(oid)
    if o is None:
        return jsonify({"error": "not found"}), 404
    if o["user_id"] != session.get("user_id"):
        return jsonify({"error": "forbidden"}), 403
    return jsonify(o)
