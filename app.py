from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Use a robust path for the comments file (project root)
COMMENTS_FILE = os.path.join(os.path.dirname(__file__), "fan_comments.json")


def ensure_comments_file():
    """
    Ensure the comments JSON file exists and is valid.
    If missing or invalid, create/reset to {"comments": []}.
    """
    if not os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, "w") as f:
            json.dump({"comments": []}, f, indent=2)
        return

    # If file exists but is invalid JSON, reset it
    try:
        with open(COMMENTS_FILE, "r") as f:
            json.load(f)
    except (json.JSONDecodeError, OSError):
        with open(COMMENTS_FILE, "w") as f:
            json.dump({"comments": []}, f, indent=2)


def load_comments():
    ensure_comments_file()
    with open(COMMENTS_FILE, "r") as f:
        data = json.load(f)
    # Guarantee structure
    if not isinstance(data, dict) or "comments" not in data:
        data = {"comments": []}
    return data


def save_comments(data):
    # Expecting a dict with "comments" key
    with open(COMMENTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# -----------------------
# Frontend routes
# -----------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/fighters")
def fighters():
    return render_template("fighters.html")


@app.route("/fanblog")
def fanblog():
    # The frontend (fanblog.html) can fetch /api/comments itself,
    # but we can also pass the comments directly if needed.
    return render_template("fanblog.html")


# -----------------------
# API endpoints used by frontend JS
# -----------------------
@app.route("/api/comments", methods=["GET"])
def api_get_comments():
    """
    Return JSON: { "comments": [ ... ] }
    """
    try:
        data = load_comments()
        return jsonify(data), 200
    except Exception as e:
        # Return JSON error instead of HTML
        return jsonify({"error": "Failed to load comments", "detail": str(e)}), 500


@app.route("/api/add_comment", methods=["POST"])
def api_add_comment():
    """
    Accepts JSON body like: { "name": "User", "comment": "Text" }
    Returns JSON: { "status": "success", "comment": { ... } }
    """
    try:
        payload = request.get_json(force=True, silent=True)
        if not payload:
            return jsonify({"error": "Missing or invalid JSON body"}), 400

        # Basic validation
        name = payload.get("name") or payload.get("username") or payload.get("author")
        comment_text = payload.get("comment") or payload.get("text") or payload.get("body")
        if not name or not comment_text:
            return jsonify({"error": "JSON must include 'name' and 'comment' fields"}), 400

        # Load, append, save
        data = load_comments()
        new_comment = {"name": name, "comment": comment_text}
        data["comments"].append(new_comment)
        save_comments(data)

        return jsonify({"status": "success", "comment": new_comment}), 201

    except Exception as e:
        return jsonify({"error": "Server error", "detail": str(e)}), 500


# -----------------------
# Run the app
# -----------------------
if __name__ == "__main__":
    # Make sure the comments file exists before starting
    ensure_comments_file()
    app.run(debug=True)

