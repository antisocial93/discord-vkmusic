import vk_api
import pypresence
import time
import tkinter as tk
import os
import json
import ctypes
import sys
import pystray
import threading
import time

from tkinter import messagebox
from PIL import Image, ImageDraw

app_id = '543726720289734656'
serviceKey = None
vkId = None

config_file = "config.json"

# Значения по умолчанию
saved_service_key = ""
saved_vk_id = ""

# Проверяем наличие файла
def fileCheck():
    global saved_service_key, saved_vk_id
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            try:
                data = json.load(file)
                saved_service_key = data.get("serviceKey", "").strip()
                saved_vk_id = data.get("vkId", "").strip()
            except json.JSONDecodeError:
                saved_service_key = ""
                saved_vk_id = ""
    else:
        # Файл не существует — создаём пустой
        with open(config_file, "w") as file:
            json.dump({"serviceKey": "", "vkId": ""}, file)
        saved_service_key = ""
        saved_vk_id = ""

def save_data(c, d):
    data = {
        "serviceKey": c,
        "vkId": d
    }
    with open(config_file, "w") as file:
        json.dump(data, file)

def checkInput(a, b):
    global saved_service_key, saved_vk_id
    if a == "" or b == "":
        messagebox.showerror("Ошибка!", "Введите верные данные!")
    else:
        messagebox.showinfo("Подключение", "Пробуем подключиться!")
        save_data(a, b)
        saved_service_key = a
        saved_vk_id = b
        root.destroy()
        return

def GUI():
    global saved_service_key, saved_vk_id, root
    #fileCheck()

    root = tk.Tk()
    root.title("VK Music - Discord RPC")
    root.config(bg="skyblue")
    root.resizable(False, False)

    frame = tk.Frame(root, width=280, height=280)
    frame.pack(padx=10, pady=10)
    frame.config(bg="skyblue")

    tk.Label(frame, text="Service Key:", bg="skyblue").pack(anchor="w", padx=30)
    serviceKey = tk.Entry(frame)
    serviceKey.insert(0, saved_service_key)
    serviceKey.pack()
    tk.Label(frame, text="VK ID:", bg="skyblue").pack(anchor="w", padx=45)
    vkId = tk.Entry(frame)
    vkId.insert(0, saved_vk_id)
    vkId.pack()

    tk.Button(root, text="Подключиться", command=lambda: checkInput(serviceKey.get(), vkId.get()), width=18).pack(pady=10, padx=30, fill="x")

    saved_service_key = serviceKey.get()
    saved_vk_id = vkId.get()
    root.mainloop()

def on_quit(icon, item):
    icon.stop()
    # Можно завершить программу, если нужно
    os._exit(0)

def tray_icon():
    image = Image.open("assets/icon.ico")
    icon = pystray.Icon("icon", image, "VK Discord RPC", menu=pystray.Menu(pystray.MenuItem("Выход", on_quit)))
    icon.run()

def hide_console():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_MINIMIZE = 6 — свернуть окно, 0 - скрыть
    else:
        print("Нет окна консоли")

fileCheck()
# Проверяем, есть ли сохранённые данные
if saved_service_key == "" or saved_vk_id == "":
    GUI()  # Показываем окно только если данных нет
presence = pypresence.Presence(app_id)
presence.connect()
vk_session = vk_api.VkApi(token=saved_service_key)
vk = vk_session.get_api()

print("Приложение было проинициализировано. Запуск через 5 секунд.")
time.sleep(5)
print("Работает! Сворачиваемся...")
time.sleep(2)
hide_console()
threading.Thread(target=tray_icon, daemon=True).start()

while True:
    large_image = "vk"
    activity = {
        "large_image": large_image
    }
    res = vk.users.get(user_ids=saved_vk_id, fields="status")[0]
    #print(res) Отчёт по отслеживанию данных о музыке в консоль

    if "status_audio" not in res:
        state = "No Music"
        if "details" in activity:
            activity.pop("details")

        large_image = 'vk'
        activity.update({'state': state, 'large_image': large_image})
    else:
        curr_music = res['status_audio']

        state = f"{curr_music['artist']}"
        details = f"{curr_music['artist']} - {curr_music['title']}"
        if 'album' in curr_music and 'thumb' in curr_music['album']:
            large_image = curr_music["album"]["thumb"]["photo_300"]

        activity.update(
            {'state': None, 'details': details,
            'large_image': large_image})
    presence.update(**activity)
    time.sleep(5)    
