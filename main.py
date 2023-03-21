from datetime import datetime
import os
import random
import string
import threading
import time
import zipfile
import requests
import json
import telebot
from tkinter import Tk, Label, Button, Text, Entry, Checkbutton, StringVar, IntVar, END
from tkinter.filedialog import askopenfilenames

bot_token = '***'
chat_id = '***'
bot = telebot.TeleBot(bot_token)


def get_ip_info():
    try:
        url = "https://ipinfo.io/json"
        response = requests.get(url)
        data = json.loads(response.text)
        return f"{data['ip']}, {data['country']}, {data['timezone']}\n"
    except:
        return "Unable to get IP info\n"


def remove_temp_archive(zip_file_name):
    try:
        os.remove(zip_file_name)
    except:
        pass


def send_files(log_text, password_entry, generate_password_var, zip_name_entry):
    try:
        file_paths = askopenfilenames()

        if not file_paths:
            log_text.insert(END, 'No files selected!\n')
            return

        start_time = time.time()
        log_text.insert(END, 'Creating ZIP archive...\n')

        zip_file_name = zip_name_entry.get() or datetime.now().strftime('%d-%m-%Y_%H-%M-%S.zip')
        password = password_entry.get() if not generate_password_var.get() else ''.join(
            random.choices(string.ascii_letters + string.digits, k=8))

        with zipfile.ZipFile(zip_file_name, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zip_file:
            for file_path in file_paths:
                zip_file.write(file_path, os.path.basename(file_path), compress_type=zipfile.ZIP_DEFLATED)
            if password:
                zip_file.setpassword(password.encode())

        log_text.insert(END, f'ZIP archive created in {time.time() - start_time:.2f} seconds\n')

        start_time = time.time()
        log_text.insert(END, 'Sending ZIP archive to Telegram bot...\n')

        with open(zip_file_name, 'rb') as zip_file:
            caption = f'Password: {password}\n\nSent by: {get_ip_info()}' if password else f'Sent by: {get_ip_info()}'
            bot.send_document(chat_id, zip_file, caption=caption)

        remove_temp_archive(zip_file_name)

        log_text.insert(END, f'ZIP archive sent in {time.time() - start_time:.2f} seconds\n')

        log_text.insert(END, 'Done!\n')
    except Exception as e:
        log_text.insert(END, f'Error: {e}\n')


root = Tk()
root.title('Send Files to Telegram Bot')

label1 = Label(root, text='Select files to send to Telegram bot:')
label1.pack()

log_text = Text(root)
log_text.pack()

label2 = Label(root, text='Enter name for ZIP archive (optional):')
label2.pack()

zip_name_entry = Entry(root)
zip_name_entry.pack()

label3 = Label(root, text='Enter password for ZIP archive (optional):')
label3.pack()

password_entry = Entry(root)
password_entry.pack()

generate_password_var = IntVar()
generate_password_checkbutton = Checkbutton(root, text='Generate random password', variable=generate_password_var,
                                            onvalue=1, offvalue=0)
generate_password_checkbutton.pack()

button = Button(root, text='Select Files', command=lambda: threading.Thread(target=send_files, args=(
    log_text, password_entry, generate_password_var, zip_name_entry), daemon=True).start())
button.pack()

root.mainloop()