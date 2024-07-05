import tkinter as tk
import pyautogui
import time
from PIL import ImageGrab
import keyboard
import sys
from tkinter import messagebox
from tkinter import font

class SubMenu:
    def __init__(self, parent, buttons, text, is_last=False):
        self.parent = parent
        self.buttons = buttons
        self.text = text
        self.is_last = is_last
        self.submenu_visible = False
        self.is_disabled = False
        self.btn = tk.Label(self.parent, text=f"{self.text} \u25B6", borderwidth=1, font=("Helvetica", 13), relief=tk.SOLID, width=35, height=2)

        self.submenu = tk.Menu(root, tearoff=0)
        for btn in buttons:
            self.submenu.add_command(label=btn, command=lambda b=btn: self.add_to_entry(b), font=("Helvetica", 13))

        self.btn.bind("<Button-1>", self.show_submenu)
        self.btn.bind("<Leave>", self.hide_submenu)

    def disable(self):
        self.is_disabled = True
        self.btn.config(text="Check position and color to use it.")
    
    def enable(self):
        self.is_disabled = False
        self.btn.config(text="Add block with position and color to code \u25B6")

    def show_submenu(self, event):
        if self.is_disabled:
            return

        if self.submenu_visible:
            self.hide_submenu()
        else:
            button_pos_x = self.btn.winfo_rootx()
            button_pos_y = self.btn.winfo_rooty()
            self.submenu.post(button_pos_x + self.btn.winfo_width(), button_pos_y)
            self.submenu_visible = True

    def hide_submenu(self, event=None):
        if self.is_disabled:
            return

        self.submenu.unpost()
        self.submenu_visible = False

    def add_to_entry(self, button):
        add_new_line_to_end_of_real_text(projectLoc, button)

def add_new_line_to_end_of_real_text(file_path, text):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    while lines and lines[-1].strip() == "":
        lines.pop()
    
    lines.append(text)

    with open(file_path, 'w') as file:
        file.writelines(lines)


def bring_to_top(window):
    # Check if window is minimized
    if window.state() == "iconic":
        window.deiconify()  # Restore the window from minimized state
    window.lift()  # Bring the window to the top

def delayed_info(window):
    window.after(5000, lambda: bring_to_top(window))
    window.after(5000, get_info)

def get_info():
    global submenu

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

    submenu.submenu.delete(0, 'end')
    new_commends = [f"MoveMouseTo({mouse_x}, {mouse_y})", f"WaitForPixel({mouse_x}, {mouse_y}, {pixel_color})", f"IfPixelColor({mouse_x}, {mouse_y}, {pixel_color})", f"MoveAndClickMouse({mouse_x}, {mouse_y}, left / right )"]
    for btn in new_commends:
            submenu.submenu.add_command(label=btn, command=lambda b=btn: submenu.add_to_entry(b), font=("Helvetica", 13))
    submenu.enable()

with open('name.txt', 'r') as file:
    name = file.readline()
    loc = file.readline()
projectLoc = loc
name = name.replace('\n', '')
projectName = name

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

submenu = SubMenu(root, ["MoveMouseTo( 200, 200 )"], "Add block with position and color to code")
submenu.btn.pack(pady=(50, 0))
submenu.disable()

btnCheck = tk.Button(root, text="Check", font=font.Font(), command=lambda: delayed_info(root))
btnCheck.pack(side=tk.BOTTOM, pady=(0, 50))

root.mainloop()