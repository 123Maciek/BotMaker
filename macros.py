import tkinter as tk
import pyautogui
import time
from PIL import ImageGrab
import sys
from tkinter import font
import ctypes
from pynput import mouse, keyboard
from tkinter import messagebox
import os

def save_macro():
    global chk_var
    if chk_var.get() != 0:
        messagebox.showerror("Hide mouse move error", "To run your macro you have to disavle hide mouse move option.")
        return
    
    try:
        act = text_to_action(tbValue.get("1.0", tk.END))
    except:
        messagebox.showerror("Recording error", "Incorrect recording value.")
        return
    
    with open('name.txt', 'r') as file:
        name = file.readline()
        loc = file.readline()
    projectLoc = loc
    name = name.replace('\n', '')
    if projectLoc == None or projectLoc == "":
        messagebox.showerror("Project error", "It seams that ur project doesn't exists.")
        return
    
    test_act = tbValue.get("1.0", tk.END).replace("\n", "")
    test_act = test_act.replace(" ", "")
    if test_act == "":
        messagebox.showerror("Recording error", "You cannot save empty recording.")
        return

    macro_loc = projectLoc[:-(len(name) + 4)]
    macro_name = tbName.get()
    if macro_name == "" or macro_name == None:
        messagebox.showerror("Macro Name error", "Your macro name cannot be empty.")
        return
    new_macro_name = macro_name.replace(" ", "")
    new_macro_name = new_macro_name.replace(".", "")
    new_macro_name = new_macro_name.replace("\n", "")
    new_macro_name = new_macro_name.replace("(", "")
    new_macro_name = new_macro_name.replace(")", "")
    if new_macro_name != macro_name:
        messagebox.showerror("Macro Name error", "Incorrect macro name value. Macro's name cannot contain space, dots and brackets")
        return
    
    macro_loc += f"Macros\\{macro_name}.txt"
    if os.path.isfile(macro_loc):
        result = messagebox.askquestion("Confirmation", "Macro of this name already exist in your current project. Do you wanna replace it?")
        if result.lower() == 'yes':
            os.remove(macro_loc)
        else:
            return
    with open(macro_loc, "w") as file:
        file.write(tbValue.get("1.0", tk.END))
    
    root.destroy()
            

def play_current_action():
    global chk_var
    if chk_var.get() != 0:
        messagebox.showerror("Hide mouse move error", "To run your macro you have to disavle hide mouse move option.")
        return

    act = text_to_action(tbValue.get("1.0", tk.END))
    time.sleep(3)
    play_actions(act)

def text_to_action(text):
    lines = text.split("\n")
    act = []
    for line in lines:
        if line != "":
            line = line[:-1]
            line = line[1:]
            line = line.replace(" ", "")
            args = line.split(",")
            arr = []
            for arg in args:
                if arg[0] == "'" and arg[len(arg)-1] == "'":
                    arg = arg[1:]
                    arg = arg[:-1]
                else:
                    try:
                        arg = int(arg)
                    except:
                        arg = float(arg)
                arr.append(arg)
            act.append(arr)
    return act

def action_to_text(arr):
    result = ""
    num = 0
    for el in arr:
        string = str(el)
        string = string.replace("[", "(")
        string = string.replace("]", ")")
        result += string
        if num != len(arr)-1:
            result += "\n"
        num += 1
    return result

def start_record():
    # Start listeners
    btnStart.config(text="STOP - F8",  fg="white", bg="red", activeforeground="white", activebackground="red")
    global actions
    actions = []

    global is_recording
    is_recording = True
    #mouse_listener.start()
    #keyboard_listener.start()
    global start_time
    start_time = time.time()

def stop_recording():
    #Stop listeners
    #mouse_listener.stop()
    #keyboard_listener.stop()
    global is_recording
    global actions
    is_recording = False
    btnStart.config(text="START - F8", fg="white", bg="green", activeforeground="white", activebackground="darkgreen")
    messagebox.showinfo("Succesfull recording", "Your macro has been succesfully recorded.")
    set_tbValue(action_to_text(actions))
    chk_var.set(0)
    

def on_window_close():
    mouse_listener.stop()
    keyboard_listener.stop() 
    root.destroy()

def is_f8_pressed():
    return ctypes.windll.user32.GetKeyState(0x77) < 0

def remove_prefix_if_matches(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    else:
        return string

def actions_without_movement():
    result = ""
    new_act = hide_chain_values(text_to_action(tbValue.get("1.0", tk.END)))
    result = action_to_text(new_act)
    return result

def number_in_array(arr, el):
    num = 0
    el = str(el)
    el = el.replace("[", "(")
    el = el.replace("]", ")")
    for a in arr:
        if str(a) == el:
            return num
        num += 1
    return num

def number_in_array2(arr, el):
    num = 0
    el = str(el)
    for a in arr:
        if str(a) == el:
            return num
        num += 1
    return num

def insert_value(arr, value, index):
    if index < 0 or index > len(arr):
        arr.append(value)
        return arr
    return arr[:index] + [value] + arr[index:]

def actions_with_movement():
    global actions
    result = ""
    cur_act = text_to_action(tbValue.get("1.0", tk.END))
    mouse_moves_number = []
    num = 0
    for el in cur_act:
        if el[0] == "mouse_move":
            mouse_moves_number.append(el)
        num += 1
    for object in mouse_moves_number:
        number = number_in_array2(cur_act, object)
        mm = number_in_array(actions, cur_act[number])
        next = 0
        if (number + 1) == len(cur_act):
            next = len(actions) - 1
        else:
            next = number_in_array(actions, cur_act[number+1])
        iteration = 1
        range_list = range(next-mm-1)
        result_list = [num + mm + 1 for num in range_list]
        for i in result_list:
            if (actions[i])[0] != "mouse_move":
                break
            cur_act = insert_value(cur_act, actions[i], number + iteration)
            iteration += 1
    actions = []
    for i in cur_act:
        actions.append(tuple(i))
    result = action_to_text(cur_act)
    return result

def remove_element(arr, elem):
    return [x for x in arr if x != elem]

def play_actions(act):
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
            pyautogui.mouseDown(x, y, button)
        elif action_type == "mouse_release":
            x, y, button = params
            pyautogui.mouseUp(x, y, button)
        elif action_type == "key_press":
            key = params[0]
            pyautogui.keyDown(key)
        elif action_type == "key_release":
            key = params[0]
            pyautogui.keyUp(key)

def set_tbValue(text):
    tbValue.delete(1.0, tk.END)
    tbValue.insert(tk.END, text)

def on_checkbox_click():
    if chk_var.get() == 1:
        txt = actions_without_movement()
        tbValue.delete(1.0, tk.END)
        tbValue.insert(tk.END, txt)
    else:
        txt = actions_with_movement()
        tbValue.delete(1.0, tk.END)
        tbValue.insert(tk.END, txt)
        

# Create the main window
root = tk.Tk()
root.configure(bg="lightgray")
root.protocol("WM_DELETE_WINDOW", on_window_close)
root.title("Macro Recorder")

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
btnSave = tk.Button(root, text="SAVE", fg="white", bg="green", activeforeground="white", activebackground="darkgreen", bd=1, relief=tk.FLAT, font=("Heltevica", 25), command=save_macro)
btnSave.pack(side=tk.LEFT, pady=(0, 50), padx=(120, 20))
btnStart = tk.Button(root, text="START - F8", fg="white", bg="green", activeforeground="white", activebackground="darkgreen", bd=1, relief=tk.FLAT, font=("Heltevica", 25))
btnStart.pack(side=tk.LEFT, pady=(0, 50), padx=10)
btnPlay = tk.Button(root, text="PLAY - 3 SEC DELAY", fg="white", bg="green", activeforeground="white", activebackground="darkgreen", bd=1, relief=tk.FLAT, font=("Heltevica", 25), command=play_current_action)
btnPlay.pack(side=tk.LEFT, pady=(0, 50), padx=(20, 0))

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
    if is_recording == False:
        return

    elapsed_time = time.time() - start_time
    actions.append(("mouse_move", x, y, elapsed_time))

def on_mouse_click(x, y, button, pressed):
    if is_recording == False:
        return

    elapsed_time = time.time() - start_time
    click = ""
    if str(button)[:7] == "Button.":
        click = str(button)[7:]
    if click[0] == "x":
        num = click[1]
        click = None
        click = num
    action = ("mouse_press" if pressed else "mouse_release", x, y, click, elapsed_time)
    actions.append(action)

# Keyboard event handler
def on_key_press(key):
    if is_recording == False:
        return
    elapsed_time = time.time() - start_time
    try:
        key_char = key.char
    except AttributeError:
        key_char = str(key)

    key_char = key_char.lower()
    key_char = remove_prefix_if_matches(key_char, "key.")
    if key_char == "cmd":
        key_char = "win"
    if key_char == "alt_l":
        key_char = "alt"

    if key_char == "f8":
        return
    actions.append(("key_press", key_char, elapsed_time))

def on_key_release(key):
    global is_recording
    elapsed_time = time.time() - start_time
    try:
        key_char = key.char
    except AttributeError:
        key_char = str(key)

    if is_recording:
        if key_char == "Key.f8":
            stop_recording()
            return
    else:
        if key_char == "Key.f8":
            start_record()
            return

    if is_recording == False:
        return

    key_char = key_char.lower()
    key_char = remove_prefix_if_matches(key_char, "key.")
    if key_char == "cmd":
        key_char = "win"
    if key_char == "alt_l":
        key_char = "alt"

    actions.append(("key_release", key_char, elapsed_time))

# Set up listeners
mouse_listener = mouse.Listener(on_move=on_mouse_move, on_click=on_mouse_click)
keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)

mouse_listener.start()
keyboard_listener.start()
is_recording = False

root.mainloop()