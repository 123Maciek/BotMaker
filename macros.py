import tkinter as tk
import pyautogui
import time
from PIL import ImageGrab
import keyboard
import sys
from tkinter import font
from pynput import mouse, keyboard

def start_record():
    btnStart["state"] = "disabled"
    # Start listeners
    global actions
    actions = []
    mouse_listener.start()
    keyboard_listener.start()
    global start_time
    start_time = time.time()

    time.sleep(10)

    # Stop listeners
    mouse_listener.stop()
    keyboard_listener.stop()
    time.sleep(3)
    on_checkbox_click()
    play_actions(actions)
    btnStart["state"] = "normal"


def actions_without_movement():
    result = ""
    new_act = hide_chain_values(actions)
    for act in new_act:
        result += str(act)
        result += "\n"
    return result

def actions_with_movement():
    result = ""
    for act in actions:
        result += str(act)
        result += "\n"
    return result

def remove_element(arr, elem):
    return [x for x in arr if x != elem]

def play_actions(act):
    print("Start playing actions")
    start = time.time()

    for action in act:
        action_type, *params, timestamp = action

        elapsed_time = time.time() - start
        delay = timestamp - elapsed_time

        pyautogui.PAUSE = max(0, delay)

        # Odtwarzaj akcję
        if action_type == "mouse_move":
            x, y = params
            pyautogui.moveTo(x, y)
        elif action_type == "mouse_press":
            x, y, button = params
            click = ""
            if str(button) == "Button.left":
                click = "left"
            pyautogui.mouseDown(x, y, click)
        elif action_type == "mouse_release":
            x, y, button = params
            click = ""
            if str(button) == "Button.left":
                click = "left"
            pyautogui.mouseUp(x, y, click)
        elif action_type == "key_press":
            key = params[0]
            pyautogui.keyDown(key)
        elif action_type == "key_release":
            key = params[0]
            pyautogui.keyUp(key)

def on_checkbox_click():
    if chk_var.get() == 1:
        tbValue.delete(1.0, tk.END)
        tbValue.insert(tk.END, actions_without_movement())
    else:
        tbValue.delete(1.0, tk.END)
        tbValue.insert(tk.END, actions_with_movement())
        

# Create the main window
root = tk.Tk()
root.configure(bg="lightgray")

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the x and y coordinates for the window to be centered
x_coordinate = (screen_width - 1000) // 2
y_coordinate = (screen_height - 900) // 2

# Set the window size and position
root.geometry(f"1000x900+{x_coordinate}+{y_coordinate}")
root.resizable(width=False, height=False)
lblTitle = tk.Label(root, text="Add Macro", font=("Arial", 30), fg="darkgreen", bg="lightgray")
lblTitle.pack(anchor="n", pady=20)
lblName = tk.Label(root, text="Macro Name: ", font=font.Font(), bg="lightgray")
lblName.pack(side=tk.TOP)
tbName = tk.Entry(root, width=30, font=font.Font())
tbName.pack(side=tk.TOP)
lblNameValidation = tk.Label(root, text="", fg="red", bg="lightgray", font=font.Font())
lblNameValidation.pack(side=tk.TOP)
lblValue = tk.Label(root, text="Recorded input: ", font=font.Font(), bg="lightgray")
lblValue.pack(side=tk.TOP, pady=(30, 0))
chk_var = tk.IntVar()
checkbox = tk.Checkbutton(root, text="Hide mouse movement", variable=chk_var, command=on_checkbox_click)
checkbox.pack(pady=20)
tbValue = tk.Text(root, width=70, height=20, font=font.Font())
tbValue.pack(side=tk.TOP)
btnStart = tk.Button(root, text="START", fg="white", bg="green", activeforeground="white", activebackground="darkgreen", bd=1, relief=tk.FLAT, font=("Heltevica", 25), command=start_record)
btnStart.pack(side=tk.BOTTOM, pady=(0, 50))

# Lists to store recorded actions
actions = []

# Record start time
start_time = time.time()



def hide_chain_values(arr, value="mouse_move"):
    result = []
    previous = None
    
    for num in arr:
        if num[0] != value or num[0] != previous:
            result.append(num)
        previous = num[0]
    
    return result

# Mouse event handler
def on_mouse_move(x, y):
    elapsed_time = time.time() - start_time
    actions.append(("mouse_move", x, y, elapsed_time))

def on_mouse_click(x, y, button, pressed):
    elapsed_time = time.time() - start_time
    action = ("mouse_press" if pressed else "mouse_release", x, y, button, elapsed_time)
    actions.append(action)

# Keyboard event handler
def on_key_press(key):
    elapsed_time = time.time() - start_time
    try:
        key_char = key.char
    except AttributeError:
        key_char = str(key)

    actions.append(("key_press", key_char, elapsed_time))

def on_key_release(key):
    elapsed_time = time.time() - start_time
    try:
        key_char = key.char
    except AttributeError:
        key_char = str(key)

    actions.append(("key_release", key_char, elapsed_time))

# Set up listeners
mouse_listener = mouse.Listener(on_move=on_mouse_move, on_click=on_mouse_click)
keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)


root.mainloop()