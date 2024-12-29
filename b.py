import json
import os
import logging
import requests
from urllib.parse import quote_plus
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

# Direktori untuk menyimpan file YAML
YAML_DIR = "yaml_files"

# Status percakapan
WAITING_FOR_FILENAME = 1
WAITING_FOR_CONFIG = 2

# Fungsi untuk menyimpan ID pengguna ke dalam file
def save_user(user_id: int):
    # Memuat data pengguna yang sudah ada dari file JSON
    users_data = load_users()
    
    # Menyimpan ID pengguna jika belum ada
    if user_id not in users_data:
        users_data[user_id] = {}

    # Menyimpan kembali data ke file
    save_users(users_data)

# Fungsi untuk memuat data pengguna dari file JSON
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}

# Fungsi untuk menyimpan data pengguna ke dalam file JSON
def save_users(users_data):
    with open('users.json', 'w') as f:
        json.dump(users_data, f)

# Fungsi untuk mendapatkan jumlah total pengguna
def get_total_users():
    users_data = load_users()
    return len(users_data)

# Fungsi untuk mengonversi konfigurasi XRay ke dalam URL Clash berdasarkan mode
def convert_to_clash_url(config: str, mode: str) -> str:
    encoded_config = quote_plus(config)
    base_url = "https://sub.bonds.id/sub2?target=clash"

    mode_configs = {
        "REDIRHOST": "base%2Fdatabase%2Fconfig%2Fstandard%2Fstandard_redir.ini",
        "FAKEIP": "base%2Fdatabase%2Fconfig%2Fstandard%2Fstandard_fake.ini",
        "BESTPING_FAKEIP": "base%2Fdatabase%2Fconfig%2Fcustom%2Fgroups%2Furltest_fake.ini",
        "BESTPING_ADBLOCK_FAKEIP": "base%2Fdatabase%2Fconfig%2Fcustom%2Fadblocks%2Fadblock_urltest_fake.ini",
    }

    config_path = mode_configs.get(mode)
    if not config_path:
        return None

    url = (
        f"{base_url}&url={encoded_config}&insert=false&config={config_path}"
        "&filename=yaml.yaml&emoji=false&list=false&udp=true&tfo=false"
        "&expand=false&scv=true&fdn=false&sort=false&new_name=true"
    )
    return url

# Fungsi untuk mengunduh file YAML dari URL
def download_yaml(url: str, filename: str) -> str:
    os.makedirs(YAML_DIR, exist_ok=True)  # Membuat folder jika belum ada
    file_path = os.path.join(YAML_DIR, filename)

    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    else:
        return None

# Fungsi untuk menampilkan tombol mode
async def show_modes(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    save_user(user.id)  # Menyimpan ID pengguna yang berinteraksi

    total_users = get_total_users()  # Mendapatkan jumlah total pengguna

    keyboard = [
        [InlineKeyboardButton("REDIRHOST (basic)", callback_data='REDIRHOST')],
        [InlineKeyboardButton("FAKEIP (basic)", callback_data='FAKEIP')],
        [InlineKeyboardButton("BEST PING - FAKE IP", callback_data='BESTPING_FAKEIP')],
        [InlineKeyboardButton("BEST PING + ADBLOCK - FAKE IP", callback_data='BESTPING_ADBLOCK_FAKEIP')],
        [InlineKeyboardButton("Penjelasan", callback_data='EXPLANATION')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "———————————————————————\n"
        "=>              Subconvert YAML              <=\n"
        "———————————————————————\n"
        f"👤 Informasi Pengguna\n\n"
        f"» NAMA : {user.full_name}\n"
        f"» USERNAME : @{user.username}\n"
        f"» ID USER : {user.id}\n"
        "———————————————————————\n"
        f"» Total Member: {total_users}\n"
        "———————————————————————\n"
        "Jika anda bingung tentang MODE/FITUR\n"
        "Tekan tombol Penjelasan.\n"
        "———————————————————————\n"
        "Thanks to sub.bonds.id\n"
        "Thanks to @fernandairfan\n"
        "———————————————————————"
    )

    # Menggunakan pengecekan callback_query untuk menghindari error
    if update.callback_query:
        await update.callback_query.answer()  # Menanggapi callback query
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

# Fungsi untuk menangani pilihan mode
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data

    if data == 'EXPLANATION':
        explanation_text = (
            "Berikut penjelasan singkat tentang fitur/mode Xray:\n\n"
            "1. **Redirhost Basic**: Mengarahkan lalu lintas internet ke host tertentu dengan pengaturan dasar, cocok untuk penggunaan sederhana tanpa banyak modifikasi data.\n"
            "2. **FakeIP Basic**: Mengganti IP asli pengguna dengan IP palsu untuk menyembunyikan identitas dan meningkatkan privasi.\n"
            "3. **Best Ping + Fake IP**: Memilih server dengan ping terbaik untuk koneksi lebih cepat, sambil mengganti IP asli dengan IP palsu untuk privasi.\n"
            "4. **Best Ping + Adblock + Fake IP**: Memilih server dengan ping terbaik, memblokir iklan, dan mengganti IP asli dengan IP palsu, memberikan pengalaman browsing yang cepat dan aman."
        )
        keyboard = [[InlineKeyboardButton("Kembali", callback_data='BACK')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.answer()
        await query.edit_message_text(explanation_text, parse_mode='Markdown', reply_markup=reply_markup)
    elif data == 'BACK':
        await query.answer()
        await show_modes(update, context)
    else:
        context.user_data['mode'] = data  # Menyimpan mode yang dipilih
        await query.answer()
        await query.edit_message_text(f"Mode {data} dipilih. Kirimkan konfigurasi XRay Anda untuk dikonversi.")
        return WAITING_FOR_FILENAME

# Fungsi untuk meminta nama file dari pengguna
async def ask_for_filename(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Silakan masukkan nama file untuk konfigurasi (tanpa ekstensi, misalnya 'config1').")
    return WAITING_FOR_FILENAME

# Fungsi untuk menangani nama file yang diberikan pengguna
async def handle_filename(update: Update, context: CallbackContext) -> None:
    filename = update.message.text.strip() + ".yaml"  # Menambahkan ekstensi .yaml
    config = context.user_data.get('config')
    mode = context.user_data.get('mode')

    if not filename:
        await update.message.reply_text("Nama file tidak valid. Silakan coba lagi.")
        return WAITING_FOR_FILENAME

    url = convert_to_clash_url(config, mode)

    if url:
        downloaded_file = download_yaml(url, filename)

        if downloaded_file:
            await update.message.reply_text(f"File YAML untuk mode {mode} berhasil dikonversi! Mengirimkan file...")
            with open(downloaded_file, 'rb') as file:
                await update.message.reply_document(file)
        else:
            await update.message.reply_text("Gagal mengunduh file. Coba lagi nanti.")
    else:
        await update.message.reply_text(f"Mode {mode} tidak valid. Silakan pilih mode yang benar.")
    return ConversationHandler.END

# Fungsi untuk menangani konfigurasi XRay yang dikirimkan
async def handle_xray_config(update: Update, context: CallbackContext) -> None:
    if 'mode' not in context.user_data:
        await update.message.reply_text("Silakan pilih mode terlebih dahulu dengan menggunakan /start.")
        return

    mode = context.user_data['mode']
    config = update.message.text.strip()

    valid_prefixes = ["vmess://", "trojan://", "vless://"]
    if not any(config.startswith(prefix) for prefix in valid_prefixes):
        await update.message.reply_text(
            "Konfigurasi XRay tidak valid. Pastikan Anda mengirimkan konfigurasi dalam format yang benar (vmess://, trojan://, atau vless://)."
        )
        return

    context.user_data['config'] = config
    await ask_for_filename(update, context)
    return WAITING_FOR_FILENAME

# Fungsi untuk mengonfigurasi bot
def main():
    token = '7085804913:AAGv_ZYJVl-HGmZgCjQpNhRigWnng39aJmY'  # Ganti dengan token bot Anda

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", show_modes))
    application.add_handler(CallbackQueryHandler(button))

    conversation_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_xray_config)],
        states={WAITING_FOR_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filename)]},
        fallbacks=[],
    )

    application.add_handler(conversation_handler)

    application.run_polling()

if __name__ == '__main__':
   main()
