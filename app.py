from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

firebase_json = json.loads(os.environ["FIREBASE_CREDENTIALS"])

cred = credentials.Certificate(firebase_json)
firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------- APP ----------------
app = Flask(__name__)
CORS(app)

# ---------------- SEARCH ----------------
@app.route("/search")
def search():

    q = request.args.get("q", "").lower()

    docs = db.collection("items").stream()

    results = []

    for doc in docs:
        item = doc.to_dict()

        if (
            q in item.get("name", "").lower()
            or q in item.get("code", "").lower()
            or q in item.get("location", "").lower()
            or q in item.get("source", "").lower()
        ):
            results.append(item)

    return jsonify(results)

# ---------------- ITEM ----------------
@app.route("/item/<code>")
def item(code):

    docs = db.collection("items").stream()

    for doc in docs:
        item = doc.to_dict()

        if item.get("code", "").lower() == code.lower():
            return jsonify(item)

    return jsonify({"error": "Item not found"}), 404

# ---------------- LOCATION ----------------
@app.route("/location/<loc>")
def location(loc):

    docs = db.collection("items").stream()

    results = []

    for doc in docs:
        item = doc.to_dict()

        if loc.lower() in item.get("location", "").lower():
            results.append(item)

    return jsonify(results)

# ---------------- STATS ----------------
@app.route("/stats")
def stats():

    docs = db.collection("items").stream()

    total_items = 0
    total_qty = 0

    for doc in docs:
        item = doc.to_dict()

        total_items += 1

        try:
            total_qty += int(item.get("qty", 0))
        except:
            pass

    return jsonify({
        "total_items": total_items,
        "total_qty": total_qty
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
