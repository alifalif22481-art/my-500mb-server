from flask import Flask, request, jsonify, send_from_directory
import os
app = Flask(__name__)
MY_SECRET_KEY = "12345"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "Server OK! /get-data?key=12345 e jao"

@app.route('/get-data')
def get_data():
    key = request.args.get('key')
    if key != MY_SECRET_KEY:
        return jsonify({"error": "Key vul"})
    files = os.listdir(UPLOAD_FOLDER)
    total_size = sum(os.path.getsize(os.path.join(UPLOAD_FOLDER, f)) for f in files) if files else 0
    return jsonify({"message": "Server OK", "total_files": len(files), "files": files, "used_MB": round(total_size/(1024*1024),2), "limit_MB": 500})

@app.route('/upload', methods=['POST'])
def upload():
    key = request.args.get('key')
    if key != MY_SECRET_KEY:
        return "Key vul", 403
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "file pathao"}), 400
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return jsonify({"status": "saved", "file": file.filename})

@app.route('/download/<filename>')
def download(filename):
    key = request.args.get('key')
    if key != MY_SECRET_KEY:
        return "Key vul", 403
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/delete/<filename>')
def delete(filename):
    key = request.args.get('key')
    if key != MY_SECRET_KEY:
        return "Key vul", 403
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({"deleted": filename})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
