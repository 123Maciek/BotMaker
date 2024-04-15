import tkinter as tk
import pyautogui
import time
from PIL import ImageGrab
import keyboard
import sys
from tkinter import font

def get_info():
    time.sleep(5)
    mouse_x, mouse_y = pyautogui.position()
    screen_width, screen_height = pyautogui.size()

    screen = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height))
    pixel_color = screen.getpixel((mouse_x, mouse_y))
    pixel_color = str(pixel_color)
    pixel_color = pixel_color[:-1]
    pixel_color = pixel_color[1:]
    tbPos.delete(0, tk.END)
    tbPos.insert(0, f"{mouse_x}, {mouse_y}")
    tbColor.delete(0, tk.END)
    tbColor.insert(0, f"{pixel_color}")

# Create the main window
root = tk.Tk()
root.title("Bot Maker")
root.configure(bg="lightgray")

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the x and y coordinates for the window to be centered
x_coordinate = (screen_width - 600) // 2
y_coordinate = (screen_height - 500) // 2

# Set the window size and position
root.geometry(f"600x500+{x_coordinate}+{y_coordinate}")
root.resizable(width=False, height=False)

lblTitle = tk.Label(root, text="Position and Color Helper", font=("Arial", 30), fg="darkgreen", bg="lightgray")
lblTitle.pack(anchor="n", pady=20)


lblPos = tk.Label(root, text="X, Y: ", font=font.Font(), bg="lightgray")
tbPos = tk.Entry(root, width=30)
lblPos.pack(side=tk.TOP, pady=5)
tbPos.pack(side=tk.TOP)
lblColor = tk.Label(root, text="RGB: ", font=font.Font(), bg="lightgray")
tbColor = tk.Entry(root, width=30)
lblColor.pack(side=tk.TOP, pady=5)
tbColor.pack(side=tk.TOP)

lblInfo = tk.Label(root, text="After u click a button move ur mouse to a\n place u want to get info about and wait 6 seconds.\n Then return to this window", font=font.Font(), bg="lightgray")
lblInfo.pack(side=tk.TOP, pady=10)

btnCheck = tk.Button(root, text="Check", font=font.Font(), command=get_info)
btnCheck.pack(side=tk.BOTTOM, pady=50)

root.mainloop()