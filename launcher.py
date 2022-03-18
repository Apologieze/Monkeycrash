import tkinter as tk
import ctypes as ct

root = tk.Tk()
root.title("Casino")
root.geometry("500x500")

w_width = 1000
w_height = 700
screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()

center_x, center_y = int(screen_width/2 - w_width / 2), int(screen_height/2 - w_height / 2)
root.geometry(f'{w_width}x{w_height}+{center_x}+{center_y}')
root.configure(bg="#36393F")

label = tk.Label(root, text="Hello World")
label.pack()

def dark_bar(window):
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value),ct.sizeof(value))
    root.iconify()
    root.deiconify()

dark_bar(root)
root.mainloop()
