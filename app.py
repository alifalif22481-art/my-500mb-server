from flask import Flask, request, jsonify, send_from_directory
import os, uuid
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
file_map = {}
@app.route("/")
def home():
    return "Server OK! /get-data?key=YOUR_KEY e jao | /upload e file upload koro"
@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "no file"}), 400
    f = request.files['file']
    key = str(uuid.uuid4())[:8]
    filename = f"{key}_{f.filename}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    f.save(path)
    file_map[key] = filename
    with open(os.path.join(UPLOAD_FOLDER, f"{key}.txt"), "w") as mf:
        mf.write(filename)
    return jsonify({"key": key, "download_url": f"/get-data?key={key}"})
@app.route("/get-data")
def get_data():
    key = request.args.get("key")
    if not key:
        return "key dao?key=12345", 400
    filename = file_map.get(key)
    if not filename:
        txt_path = os.path.join(UPLOAD_FOLDER, f"{key}.txt")
        if os.path.exists(txt_path):
            with open(txt_path) as mf:
                filename = mf.read().strip()
        else:
            for fn in os.listdir(UPLOAD_FOLDER):
                if fn.startswith(key+"_"):
                    filename = fn
                    break
    if not filename:
        return "File not found", 404
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
