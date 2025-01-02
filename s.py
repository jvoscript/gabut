import os
import socket
import requests
import json
import subprocess
import datetime
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.parsemode import ParseMode
import logging
import os
import socket
import requests
import json
from telegram.ext import Updater, CommandHandler
import telegram
import ssl
import time
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import sublist3r

# Token bot Telegram Anda
TOKEN = "Gantitokenmu"

# Daftar ID pengguna yang diotorisasi
AUTHORIZED_USER_IDS = ['6238619204', '7153463884', '6083814573', '1682265469', '1954386866']

LOG_FILE = "bot_log.txt"

def log_user_usage(update: Update, context: CallbackContext) -> None:
    # Ambil detail pengguna dan waktu saat ini
    user = update.effective_user
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Tulis detail pengguna ke dalam file log
    with open('user_log.txt', 'a') as file:
        file.write(f"User: {user.username}, ID: {user.id}, Command: {context.args}, Timestamp: {timestamp}\n")

# Konfigurasi logger
logging.basicConfig(level=logging.INFO, filename=LOG_FILE, filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_welcome(update, context):
    user_id = update.message.from_user.id
    command = "/start"
    log_usage(user_id, command)
    message = "<b>•═══════•JVO-TEAM•═══════•</b>\n"
    message += "<b>✧ FITUR BOT <a href='https://t.me/fansstorevpn'>FANSSTORE.ID</a></b>\n"
    message += "<b>✧ /cek</b> = <b>Cek port dan server ON/OFF</b>\n"
    message += "<b>✧ /domain</b> = <b>Response</b>\n"
    message += "<b>✧ /ip</b> = <b>Lookup IP</b>\n"
    message += "<b>✧ /dompul</b> = <b>Cek Kuota XL/AXIS</b>\n"
    message += "<b>✧ /scan</b> = <b>Scan Subdomain IP/DOMAIN</b>\n"
    message += "<b>✧ CREATED</b> = <b>@fernandairfan</b>\n"
    message += "<b>•═══════•JVO-TEAM•═══════•</b>"
    
    # Membuat tombol "Donasi" dan "Menu"
    donate_button = InlineKeyboardButton(text="DONATE", callback_data="donate")
    menu_button = InlineKeyboardButton(text="MENU", callback_data="menu")
    keyboard = InlineKeyboardMarkup([[donate_button, menu_button]])
    
    # Mengirim pesan dengan tombol
    update.message.reply_text(message, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# Fungsi yang akan dipanggil saat tombol "Donasi" diklik
def donate(update, context):
    user = update.effective_user
    # Mengirim file QRIS JPG dan pesan terima kasih
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('/root/donate.jpg', 'rb'), caption=f"{user.first_name}, kami sangat menghargai setiap donasi yang diberikan kepada bot kami. Kontribusi Anda tidak hanya membantu menjalankan bot ini, tetapi juga memperbaiki layanannya.")

# Fungsi yang akan dipanggil saat tombol "Menu" diklik
def menu(update, context):
    query = update.callback_query
    telegram_button = InlineKeyboardButton(text="Owner", url="https://t.me/fernandairfan")
    group_button = InlineKeyboardButton(text="Grup Chat", url="https://t.me/fansstorevpn")
    back_button = InlineKeyboardButton(text="Kembali", callback_data="back")
    keyboard = InlineKeyboardMarkup([[telegram_button], [group_button], [back_button]])
    # Mengedit pesan dengan tombol baru
    query.edit_message_text(text="Pilih salah satu:", reply_markup=keyboard, parse_mode=ParseMode.HTML)

# Fungsi yang akan dipanggil saat tombol "Kembali" diklik
def back_to_menu(update, context):
    query = update.callback_query
    # Membuat tombol "Donasi" dan "Menu" kembali
    donate_button = InlineKeyboardButton(text="DONATE", callback_data="donate")
    menu_button = InlineKeyboardButton(text="MENU", callback_data="menu")
    keyboard = InlineKeyboardMarkup([[donate_button, menu_button]])
    # Mengedit pesan kembali ke tampilan awal
    query.edit_message_text(text="<b>•═══════•JVO-TEAM•═══════•</b>\n"
                                 "<b>✧ FITUR BOT <a href='https://t.me/fansstorevpn'>FANSSTORE.ID</a></b>\n"
                                 "<b>✧ /cek</b> = <b>Cek port dan server ON/OFF</b>\n"
                                 "<b>✧ /domain</b> = <b>Response</b>\n"
                                 "<b>✧ /ip</b> = <b>Lookup IP</b>\n"
                                 "<b>✧ /dompul</b> = <b>Cek Kuota XL/AXIS</b>\n"
                                 "<b>✧ /scan</b> = <b>Scan Subdomain IP/DOMAIN</b>\n"
                                 "<b>✧ CREATED</b> = <b>@fernandairfan</b>\n"
                                 "<b>•═══════•JVO-TEAM•═══════•</b>",
                                 reply_markup=keyboard, parse_mode=ParseMode.HTML)

# Fungsi untuk menangani callback query dari tombol InlineKeyboard
def button(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "donate":
        donate(update, context)
    elif query.data == "menu":
        menu(update, context)
    elif query.data == "back":
        back_to_menu(update, context)

def cek_kuota(msisdn: str) -> str:
    api_url = f"https://apigw.kmsp-store.com/sidompul/v3/cek_kuota?msisdn={msisdn}&isJSON=true"
    headers = {
        'Authorization': 'Basic c2lkb21wdWxhcGk6YXBpZ3drbXNw',
        'X-API-Key': '4352ff7d-f4e6-48c6-89dd-21c811621b1c',
        'X-App-Version': '3.0.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.get(api_url, headers=headers)
        logger.info(f"Request URL: {api_url}")
        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Content: {response.content}")

        if response.status_code == 200:
            try:
                data = response.json()
                hasil = data.get("data", {}).get("hasil", "")
                return hasil
            except ValueError:
                return "Error: Tidak dapat memproses respons JSON"
        else:
            return f"Error: Tidak dapat mengakses API, Status Code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")
        return "Terjadi kesalahan. Silakan coba lagi!"

def format_result(result: str) -> str:
    formatted = result.replace("<br />", "\n").replace("<br/>", "\n").replace("<br>", "\n")
    formatted = formatted.replace("📃 RESULT :", "📃 RESULT:")
    formatted = formatted.replace("🧧 Name :", "\n🧧 Name:")
    formatted = formatted.replace("🍂 Expired Date :", "\n🍂 Expired Date:")
    formatted = formatted.replace("🎨 Benefit :", "\n🎨 Benefit:")
    formatted = formatted.replace("🎁 Kuota :", "\n🎁 Kuota:")
    formatted = formatted.replace("🌲 Sisa Kuota :", "\n🌲 Sisa Kuota:")
    return formatted

def dompul(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_text('Penggunaan: /dompul <MSISDN>')
        return

    msisdn = context.args[0]
    
    # Kirim pesan bahwa pengecekan sedang berlangsung
    update.message.reply_text("Harap tunggu sebentar, Bot sedang memproses...")

    hasil_cek_kuota = cek_kuota(msisdn)
    formatted_result = format_result(hasil_cek_kuota)
    
    # Mengirim hasil dalam format mono
    update.message.reply_text(formatted_result, parse_mode=ParseMode.HTML)

    # Panggil fungsi untuk mencatat penggunaan perintah bot
    log_user_usage(update, context)

def cek_domain(update, context):
    try:
        user_id = update.message.from_user.id
        command = "/domain " + context.args[0]
        log_usage(user_id, command)
        if len(context.args) == 0:
            update.message.reply_text("Silakan masukkan nama domain yang ingin Anda cek.")
            return

        domain = context.args[0]
        domain_info = get_domain_info(domain)
        certificate_detail, ws_response_detail, port_detail = get_domain_details(domain)
        formatted_response = format_response(domain_info, certificate_detail, ws_response_detail, port_detail)
        update.message.reply_text(formatted_response, parse_mode=telegram.ParseMode.MARKDOWN)
    except Exception as e:
        update.message.reply_text(f"Format perintah salah. Gunakan /domain <domain>.")

def check_ip_info(update, context):
    try:
        user_id = update.message.from_user.id
        command = "/ip " + context.args[0]
        log_usage(user_id, command)
        if str(update.message.from_user.id) not in AUTHORIZED_USER_IDS:
            update.message.reply_text("Anda tidak diotorisasi untuk menggunakan perintah ini.")
            return

        if len(context.args) < 1:
            update.message.reply_text("Format perintah salah. Gunakan /ip <domain_or_IP>.")
            return

        address = context.args[0]
        ip_address = socket.gethostbyname(address)

        isp_response = requests.get("https://ipinfo.io/{}/json".format(ip_address))
        isp_data = json.loads(isp_response.text)
        isp = isp_data.get('org', 'Unknown')

        location_response = requests.get("https://ipinfo.io/{}/json".format(ip_address))
        location_data = json.loads(location_response.text)
        city = location_data.get('city', 'Unknown')
        region = location_data.get('region', 'Unknown')
        country = location_data.get('country', 'Unknown')
        latitude = location_data.get('loc', 'Unknown').split(',')[0]
        longitude = location_data.get('loc', 'Unknown').split(',')[1]

        message = "<b>═══════•JVO-TEAM•═══════</b>\n"
        message += "<b>✧IP Address: {}</b>\n".format(ip_address)
        message += "<b>✧ISP: {}</b>\n".format(isp)
        message += "<b>✧City: {}</b>\n".format(city)
        message += "<b>✧Region: {}</b>\n".format(region)
        message += "<b>✧Country: {}</b>\n".format(country)
        message += "<b>✧Latitude: {}</b>\n".format(latitude)
        message += "<b>✧Longitude: {}</b>\n".format(longitude)
        message += "<b>═══════•JVO-TEAM•═══════</b>"

        update.message.reply_text(message, parse_mode="HTML")

    except Exception as e:
        update.message.reply_text(f"Format perintah salah. Gunakan /ip <domain_or_IP>.")

def check_server_status(update, context):
    try:
        user_id = update.message.from_user.id
        command = "/cek " + context.args[0]
        log_usage(user_id, command)
        if str(update.message.from_user.id) not in AUTHORIZED_USER_IDS:
            update.message.reply_text("Anda tidak diotorisasi untuk menggunakan perintah ini.")
            return

        if len(context.args) < 1:
            update.message.reply_text("Format perintah salah. Gunakan /cek <domain_or_IP>.")
            return

        target = context.args[0]

        response = run_shell_command(f"ping -c 4 {target}")

        if "64 bytes from" in response:
            server_status = "<b>ONLINE</b> ✅"
        else:
            server_status = "<b>OFFLINE</b> ❌"

        response_80 = run_shell_command(f"nc -vz {target} 80 2>&1")
        response_443 = run_shell_command(f"nc -vz {target} 443 2>&1")

        port_80_status = "<b>ON</b> ✅" if "succeeded!" in response_80 else "<b>OFF</b> ❌"
        port_443_status = "<b>ON</b> ✅" if "succeeded!" in response_443 else "<b>OFF</b> ❌"

        notification_message = f"<b>▬▬▬▬▬▬▬▬▬▬▬▬▬▬</b>\n"
        notification_message += f"<b>✧DOMAIN:</b> {target}\n"
        notification_message += f"<b>✧SERVER:</b> {server_status}\n"
        notification_message += f"<b>✧PORT 80:</b> {port_80_status}\n"
        notification_message += f"<b>✧PORT 443:</b> {port_443_status}\n"
        notification_message += f"<b>▬▬▬▬▬▬▬▬▬▬▬▬▬▬</b>"

        update.message.reply_text(notification_message, parse_mode="HTML")
    except Exception as e:
        update.message.reply_text(f"Format perintah salah. Gunakan /cek <domain>.")

def run_shell_command(command):
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return str(e)

def get_domain_info(domain):
    try:
        ip = socket.gethostbyname(domain)
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        if response.status_code == 200:
            data = response.json()
            server = data.get('org', '')
            region = data.get('region', '')
            country = data.get('country', '')
            return {'host': domain, 'ip': ip, 'server': server, 'region': region, 'country': country}
    except Exception as e:
        return {'host': domain, 'ip': '', 'server': '', 'region': '', 'country': ''}

def get_domain_details(domain):
    certificate_detail = get_certificate_detail(domain)
    ws_response_detail = get_ws_response(domain)
    port_detail = get_port_details(domain)
    return certificate_detail, ws_response_detail, port_detail

def get_certificate_detail(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                subject = dict(x[0] for x in cert['subject'])
                issued_to = subject.get('commonName', '')
                issued_by = dict(x[0] for x in cert['issuer'])
                issued_by = issued_by.get('commonName', '')
                expiration_date = cert.get('notAfter', '')
                return f"Issued to: {issued_to}\nIssued by: {issued_by}\nExpiration Date: {expiration_date}"
    except Exception as e:
        return "No certificate information available"

def get_ws_response(domain):
    try:
        response = requests.get(f"http://{domain}", timeout=5)
        if response.status_code == 200:
            summary = f"HTTP/{response.raw.version} {response.status_code} {response.reason}\n{response.headers}"
            return (summary[:3000] + '...') if len(summary) > 3000 else summary
        else:
            return f"HTTP Request failed with status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"HTTP Request error: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

def get_port_details(domain):
    try:
        ports = []
        timeout = 1
        for port in [80, 443, 8443,]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            start_time = time.time()
            result = s.connect_ex((domain, port))
            elapsed_time = time.time() - start_time
            s.close()
            if result == 0:
                ports.append(str(port))
            elif elapsed_time >= timeout:
                ports.append(f"{port} (Timeout)")
        return ", ".join(ports) + "/tcp open"
    except Exception as e:
        return ""

def format_response(domain_info, certificate_detail, ws_response_detail, port_detail):
    response = "```\n"
    response += "────────────────\n"
    response += "INFORMASI DOMAIN\n"
    response += "────────────────\n"
    response += f"Host ➤ {domain_info['host']}\n"
    response += f"IP ➤ {domain_info['ip']}\n"
    response += f"Server ➤ {domain_info['server']}\n"
    response += f"Region ➤ {domain_info['region']}\n"
    response += f"Country ➤ {domain_info['country']}\n"
    response += "────────────────\n"
    response += "DETAIL CERTIFICATE:\n"
    response += certificate_detail + "\n"
    response += "────────────────\n"
    response += "DETAIL WS RESPONSE:\n"
    response += ws_response_detail + "\n"
    response += "────────────────\n"
    response += "DETAIL TCP PORT:\n"
    response += port_detail + "\n"
    response += "```"
    return response

    # Panggil fungsi untuk mencatat penggunaan perintah bot
    log_user_usage(update, context)

# Fungsi untuk melakukan reverse IP domain check
def reverse_ip_check(domain: str) -> str:
    url = "https://domains.yougetsignal.com/domains.php"
    data = {'remoteAddress': domain}
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        result = response.json()
        if 'domainArray' in result:
            domains = result['domainArray']
            if len(domains) > 0:
                domains_list = '\n'.join([domain[0] for domain in domains])
                return f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n           SCAN RESULTS\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\nSCAN TARGET : `{domain}`\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n               RESULT\n`{domains_list}`\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
            else:
                return f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n           SCAN RESULTS\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\nSCAN TARGET : `{domain}`\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n               RESULT\n`Tidak ada subdomain yang ditemukan atau terjadi kesalahan saat memindai target.`\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        else:
            return f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n           SCAN RESULTS\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\nSCAN TARGET : `{domain}`\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n               RESULT\n`Tidak ada subdomain yang ditemukan atau terjadi kesalahan saat memindai target.`\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
    else:
        return f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n           SCAN RESULTS\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\nSCAN TARGET : `{domain}`\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n               RESULT\n`Tidak ada subdomain yang ditemukan atau terjadi kesalahan saat memindai target.`\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"

# Fungsi untuk perintah /scan
def scan(update: Update, context: CallbackContext) -> None:
    if len(context.args) > 0:
        domain = context.args[0]
        update.message.reply_text(f"Melakukan pengecekan reverse IP untuk: {domain}")
        result = reverse_ip_check(domain)
        update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        update.message.reply_text("Harap berikan domain yang ingin dicek. Contoh: /scan example.com")

    log_user_usage(update, context)

def log_usage(user_id, command):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.datetime.now()} - User: {user_id} - Command: {command}\n")

def start_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", send_welcome))
    dp.add_handler(CommandHandler("help", send_welcome))
    dp.add_handler(CommandHandler("ip", check_ip_info))
    dp.add_handler(CommandHandler("cek", check_server_status))
    dp.add_handler(CommandHandler("domain", cek_domain))
    dp.add_handler(CommandHandler("scan", scan))
    dp.add_handler(CommandHandler("dompul", dompul))  # Menambahkan handler untuk perintah /dompul
    dp.add_handler(CallbackQueryHandler(donate, pattern='^donate$'))  # Menambahkan handler untuk tombol donasi
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("log_user_usage", log_user_usage))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    start_bot()
