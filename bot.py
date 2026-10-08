import telebot
import requests
import os

BOT_TOKEN = "8693415080:AAFUIQxQx15XrhmP-FDkMgdNVTYARjl2cw8"
RENDER_SERVER = "https://my-500mb-server.onrender.com"

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
        bot.reply_to(m, f"⏳ Uploading {file_name}...")
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        r = requests.get(file_url, stream=True)
        files = {'file': (file_name, r.raw)}
        resp = requests.post(f"{RENDER_SERVER}/upload", files=files, timeout=600)
        if resp.status_code == 200:
            data = resp.json()
            link = f"{RENDER_SERVER}{data['download_url']}"
            bot.reply_to(m, f"✅ Done!\n📁 {file_name}\n🔗 Link:\n{link}")
        else:
            bot.reply_to(m, f"❌ Error: {resp.text[:200]}")
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

print("Bot started")
bot.infinity_polling()
