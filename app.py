from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# ---------------- FIREBASE ----------------

firebase_json = json.loads(os.environ["FIREBASE_CREDENTIALS"])

cred = credentials.Certificate(firebase_json)
firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------- APP ----------------

app = Flask(__name__)
CORS(app)

# ---------------- HOME ----------------

@app.route("/")
def home():
    return jsonify({
        "status": "Inventory API Running"
    })

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

# ---------------- ITEM BY CODE ----------------

@app.route("/item/<code>")
def item(code):

    docs = db.collection("items").stream()

    for doc in docs:

        item = doc.to_dict()

        if item.get("code", "").lower() == code.lower():
            return jsonify(item)

    return jsonify({
        "error": "Item not found"
    }), 404

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

# ---------------- ADD ITEM ----------------

@app.route("/add", methods=["POST"])
def add_item():

    try:

        data = request.json

        code = data.get("code")

        if not code:
            return jsonify({
                "error": "Code is required"
            }), 400

        # Check if already exists
        existing = db.collection("items").document(code).get()

        if existing.exists:
            return jsonify({
                "error": "Item already exists"
            }), 400

        db.collection("items").document(code).set(data)

        return jsonify({
            "message": "Item added successfully",
            "item": data
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# ---------------- UPDATE ITEM ----------------

@app.route("/update/<code>", methods=["PUT"])
def update_item(code):

    try:

        data = request.json

        doc_ref = db.collection("items").document(code)

        if not doc_ref.get().exists:

            return jsonify({
                "error": "Item not found"
            }), 404

        doc_ref.update(data)

        updated_item = doc_ref.get().to_dict()

        return jsonify({
            "message": "Item updated successfully",
            "item": updated_item
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# ---------------- DELETE ITEM ----------------

@app.route("/delete/<code>", methods=["DELETE"])
def delete_item(code):

    try:

        doc_ref = db.collection("items").document(code)

        if not doc_ref.get().exists:

            return jsonify({
                "error": "Item not found"
            }), 404

        doc_ref.delete()

        return jsonify({
            "message": "Item deleted successfully"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# ---------------- RECENT ITEMS ----------------

@app.route("/recent")
def recent():

    docs = db.collection("items").stream()

    results = []

    for doc in docs:

        item = doc.to_dict()

        results.append(item)

    results = results[::-1]

    return jsonify(results[:10])

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
