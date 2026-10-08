import os
import threading
from flask import Flask, request, jsonify, send_from_directory
import telebot
import requests

# --- CONFIG ---
BOT_TOKEN = "8693415080:AAFUIQxQx15XrhmP-FDkMgdNVTYARjl2cw8"
RENDER_URL = "https://my-500mb-server.onrender.com"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

# --- FILE SERVER PART ---
@app.route('/')
def home():
    return "Server + Bot Running! Bot is @my500filebot"

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "no file"}), 400
    f = request.files['file']
    path = os.path.join(UPLOAD_FOLDER, f.filename)
    f.save(path)
    return jsonify({"download_url": f"/download/{f.filename}"})

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# --- BOT PART ---
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "👋 Welcome! 500MB porjonto file pathao, ami direct download link baniye debo!")

@bot.message_handler(content_types=['document', 'video', 'audio', 'photo'])
def handle_file(m):
    try:
        if m.document:
            file_id = m.document.file_id
            file_name = m.document.file_name
        elif m.video:
            file_id = m.video.file_id
            file_name = m.video.file_name or "video.mp4"
        else:
            file_id = m.photo[-1].file_id
            file_name = "photo.jpg"
        
        bot.reply_to(m, f"⏳ Uploading {file_name}... please wait 1-2 min")
        
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        
        # download from telegram and save locally (no extra upload needed, same server!)
        r = requests.get(file_url, stream=True)
        save_path = os.path.join(UPLOAD_FOLDER, file_name)
        with open(save_path, 'wb') as out:
            for chunk in r.iter_content(1024*1024):
                out.write(chunk)
        
        link = f"{RENDER_URL}/download/{file_name}"
        bot.reply_to(m, f"✅ Done!\n\n📁 {file_name}\n🔗 Link:\n{link}\n\nShare koro jake khusi!")
    except Exception as e:
        bot.reply_to(m, f"❌ Error: {e}")

def run_bot():
    print("Bot thread started")
    bot.infinity_polling()

# start bot in background thread when Flask starts
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
