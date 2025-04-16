import telebot
import os
import datetime
import requests
import platform
import socket
import re
from typing import List

# Securely load bot token from environment variable
BOT_TOKEN = os.getenv("6913030366:AAEtMr3xpYaioIzEk7iYT_Mio7YgXrEjluE")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set.")

# Configuration
ADMIN_IDS: List[str] = ["7383077317"]  # Admin Telegram IDs
ALLOWED_USER_IDS: List[str] = []  # Dynamically loaded from users.txt
LOG_FILE: str = "log.txt"
USERS_FILE: str = "users.txt"

# Initialize bot
try:
    bot = telebot.TeleBot(BOT_TOKEN)
except Exception as e:
    raise ValueError(f"Failed to initialize bot: {e}")

# Utility Functions
def get_ip_info(ip: str) -> str:
    """Fetch geolocation data for an IP address."""
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5).json()
        return f"{response.get('city', 'Unknown')}, {response.get('country_name', 'Unknown')}"
    except requests.RequestException:
        return "Unknown"

def get_device_info() -> str:
    """Get the operating system of the host machine."""
    return platform.system()

def is_host_alive(ip: str, port: int) -> str:
    """Check if a host is reachable on a specific port."""
    try:
        with socket.create_connection((ip, port), timeout=2):
            return "Alive"
    except (socket.timeout, socket.gaierror, ConnectionRefusedError):
        return "Offline"

def log_user_activity(log_data: str, user_id: str) -> None:
    """Log user activity to log.txt for non-admin users."""
    if user_id not in ADMIN_IDS:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as file:
                file.write(f"{log_data}\n")
        except IOError as e:
            print(f"Error writing to log file: {e}")

def load_allowed_users() -> None:
    """Load allowed user IDs from users.txt."""
    global ALLOWED_USER_IDS
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                ALLOWED_USER_IDS = [line.strip() for line in file if line.strip()]
    except IOError as e:
        print(f"Error reading users file: {e}")

def validate_ip(ip: str) -> bool:
    """Validate IP address format."""
    ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    return bool(re.match(ip_pattern, ip))

def validate_port(port: int) -> bool:
    """Validate port number."""
    return 1 <= port <= 65535

# Load allowed users at startup
load_allowed_users()

# Bot Command Handlers
def create_handlers(bot: telebot.TeleBot) -> None:
    @bot.message_handler(commands=['start'])
    def start_command(message):
        user_id = str(message.chat.id)
        full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
        username = message.from_user.username or "NoUsername"
        if user_id in ADMIN_IDS:
            bot.reply_to(message, (
                f"Hello {full_name} (ID: {user_id}),\n\n"
                "Welcome to the bot! You are an admin. Use /help to see available commands."
            ))
        elif user_id in ALLOWED_USER_IDS:
            bot.reply_to(message, (
                f"Hello {full_name},\n\n"
                "You are authorized to use this bot. Use /help for commands."
            ))
        else:
            bot.reply_to(message, (
                "You are not authorized to use this bot.\n"
                "Contact @spoliator_personal or visit our Telegram channel: https://t.me/Linuxcode_channel."
            ))

    @bot.message_handler(commands=['add'])
    def add_user(message):
        user_id = str(message.chat.id)
        if user_id not in ADMIN_IDS:
            bot.reply_to(message, "Only admins can use this command.")
            return

        command = message.text.split()
        if len(command) != 2:
            bot.reply_to(message, "Usage: /add <userId>")
            return

        user_to_add = command[1].strip()
        if not user_to_add.isdigit():
            bot.reply_to(message, "User ID must be a number.")
            return

        if user_to_add in ALLOWED_USER_IDS:
            bot.reply_to(message, "User already authorized.")
            return

        ALLOWED_USER_IDS.append(user_to_add)
        try:
            with open(USERS_FILE, "a", encoding="utf-8") as file:
                file.write(f"{user_to_add}\n")
            bot.reply_to(message, f"User {user_to_add} added successfully.")
        except IOError as e:
            bot.reply_to(message, f"Error adding user: {e}")

    @bot.message_handler(commands=['remove'])
    def remove_user(message):
        user_id = str(message.chat.id)
        if user_id not in ADMIN_IDS:
            bot.reply_to(message, "Only admins can use this command.")
            return

        command = message.text.split()
        if len(command) != 2:
            bot.reply_to(message, "Usage: /remove <userId>")
            return

        user_to_remove = command[1].strip()
        if user_to_remove not in ALLOWED_USER_IDS:
            bot.reply_to(message, f"User {user_to_remove} not found in authorized list.")
            return

        ALLOWED_USER_IDS.remove(user_to_remove)
        try:
            with open(USERS_FILE, "w", encoding="utf-8") as file:
                for uid in ALLOWED_USER_IDS:
                    file.write(f"{uid}\n")
            bot.reply_to(message, f"User {user_to_remove} removed successfully.")
        except IOError as e:
            bot.reply_to(message, f"Error removing user: {e}")

    @bot.message_handler(commands=['clearlogs'])
    def clear_logs_command(message):
        user_id = str(message.chat.id)
        if user_id not in ADMIN_IDS:
            bot.reply_to(message, "Only admins can use this command.")
            return

        try:
            if not os.path.exists(LOG_FILE) or os.stat(LOG_FILE).st_size == 0:
                bot.reply_to(message, "Logs are already empty.")
                return
            with open(LOG_FILE, "w", encoding="utf-8"):
                pass  # Truncate file
            bot.reply_to(message, "Logs cleared successfully.")
        except IOError as e:
            bot.reply_to(message, f"Error clearing logs: {e}")

    @bot.message_handler(commands=['allusers'])
    def show_all_users(message):
        user_id = str(message.chat.id)
        if user_id not in ADMIN_IDS:
            bot.reply_to(message, "Only admins can use this command.")
            return

        if not ALLOWED_USER_IDS:
            bot.reply_to(message, "No authorized users found.")
            return

        response = "Authorized Users:\n" + "\n".join(f"- {uid}" for uid in ALLOWED_USER_IDS)
        bot.reply_to(message, response)

    @bot.message_handler(commands=['logs'])
    def show_recent_logs(message):
        user_id = str(message.chat.id)
        if user_id not in ADMIN_IDS:
            bot.reply_to(message, "Only admins can use this command.")
            return

        if not os.path.exists(LOG_FILE) or os.stat(LOG_FILE).st_size == 0:
            bot.reply_to(message, "No logs found.")
            return

        try:
            with open(LOG_FILE, "rb") as file:
                bot.send_document(message.chat.id, file, caption="Log File")
        except Exception as e:
            bot.reply_to(message, f"Error sending logs: {e}")

    @bot.message_handler(commands=['id'])
    def show_user_id(message):
        user_id = str(message.chat.id)
        bot.reply_to(message, f"Your ID: {user_id}")

    @bot.message_handler(commands=['check'])
    def check_server(message):
        user_id = str(message.chat.id)
        if user_id not in ADMIN_IDS and user_id not in ALLOWED_USER_IDS:
            bot.reply_to(message, (
                "Unauthorized. Contact @spoliator_personal or visit: "
                "https://t.me/Linuxcode_channel."
            ))
            return

        command = message.text.split()
        if len(command) != 3:
            bot.reply_to(message, "Usage: /check <ip> <port>")
            return

        ip, port_str = command[1], command[2]
        if not validate_ip(ip):
            bot.reply_to(message, "Invalid IP address format.")
            return

        try:
            port = int(port_str)
            if not validate_port(port):
                bot.reply_to(message, "Port must be between 1 and 65535.")
                return
        except ValueError:
            bot.reply_to(message, "Port must be a number.")
            return

        full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
        username = message.from_user.username or "NoUsername"
        status = is_host_alive(ip, port)
        location = get_ip_info(ip)
        device = get_device_info()
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        response = f"Server {ip}:{port} is {status}."

        # Log activity for non-admins
        if user_id not in ADMIN_IDS:
            log_line = (
                f"{timestamp} Name: {full_name} | Username: @{username} | "
                f"UserID: {user_id} | IP: {ip} | Port: {port} | "
                f"Status: {status} | Device: {device} | Location: {location}"
            )
            log_user_activity(log_line, user_id)

        bot.reply_to(message, response)

    @bot.message_handler(commands=['mylogs'])
    def show_command_logs(message):
        user_id = str(message.chat.id)
        if user_id in ADMIN_IDS:
            bot.reply_to(message, "Admins are anonymous. No logs stored.")
            return

        try:
            if not os.path.exists(LOG_FILE):
                bot.reply_to(message, "No logs found.")
                return
            with open(LOG_FILE, "r", encoding="utf-8") as file:
                logs = file.readlines()
                user_logs = [log for log in logs if f"UserID: {user_id}" in log]
                if not user_logs:
                    bot.reply_to(message, "No logs found for you.")
                    return
                bot.reply_to(message, "".join(user_logs))
        except IOError as e:
            bot.reply_to(message, f"Error reading logs: {e}")

    @bot.message_handler(commands=['help'])
    def show_help(message):
        help_text = '''
Available Commands:
/start : Welcome message
/check <ip> <port> : Check server status
/add <userId> : Add authorized user (admin only)
/remove <userId> : Remove authorized user (admin only)
/clearlogs : Clear logs (admin only)
/allusers : List authorized users (admin only)
/logs : Download logs (admin only)
/id : Show your user ID
/mylogs : Show your logs
/help : Show this help
'''
        bot.reply_to(message, help_text)

# Register handlers
create_handlers(bot)

# Run bot
def run_bot():
    print("Bot is running...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"Bot polling error: {e}")
            import time
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
