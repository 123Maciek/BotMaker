import tkinter as tk
from tkinter import font
import pyautogui
from tkinter import messagebox
import time
import keyboard
import sys
import os
import subprocess
from PIL import ImageGrab
from tkinter import Scrollbar
import tempfile
from tkinter import Canvas

class SubMenu:
    def __init__(self, parent, buttons, text, is_last=False):
        self.parent = parent
        self.buttons = buttons
        self.text = text
        self.is_last = is_last
        self.submenu_visible = False
        self.btn = tk.Label(self.parent, text=f"{self.text} \u25B6", borderwidth=1, font=("Helvetica", 13), relief=tk.SOLID, width=35, height=2)
        if self.is_last:
            self.btn.pack(side=tk.BOTTOM, anchor="sw", pady=(0, 730), padx=40)
        else:
            self.btn.pack(side=tk.BOTTOM, anchor="sw", pady=(0, 17), padx=40)

        self.submenu = tk.Menu(root, tearoff=0)
        for btn in buttons:
            self.submenu.add_command(label=btn, command=lambda b=btn: self.add_to_entry(b), font=("Helvetica", 13))

        self.btn.bind("<Button-1>", self.show_submenu)
        self.btn.bind("<Leave>", self.hide_submenu)

    def pack(self):
        if not self.btn.winfo_exists():
            self.btn = tk.Label(self.parent, text=f"{self.text} \u25B6", borderwidth=1, relief=tk.SOLID, width=35, height=2)
            if self.is_last:
                self.btn.pack(side=tk.BOTTOM, anchor="sw", pady=(0, 730), padx=40)
            else:
                self.btn.pack(side=tk.BOTTOM, anchor="sw", pady=(0, 17), padx=40)

    def destroy(self):
        self.btn.destroy()

    def show_submenu(self, event):
        if self.submenu_visible:
            self.hide_submenu()
        else:
            button_pos_x = self.btn.winfo_rootx()
            button_pos_y = self.btn.winfo_rooty()
            self.submenu.post(button_pos_x + self.btn.winfo_width(), button_pos_y)
            self.submenu_visible = True

    def hide_submenu(self, event=None):
        self.submenu.unpost()
        self.submenu_visible = False

    def mouse_in_widget(self, widget):
        if isinstance(widget, tk.Menu):
            widget_x, widget_y = widget.winfo_rootx(), widget.winfo_rooty()
            widget_width, widget_height = widget.winfo_width(), widget.winfo_height()
        else:
            widget_x, widget_y = widget.winfo_rootx(), widget.winfo_rooty()
            widget_width, widget_height = widget.winfo_width(), widget.winfo_height()
        return widget_x <= self.parent.winfo_pointerx() <= widget_x + widget_width and widget_y <= self.parent.winfo_pointery() <= widget_y + widget_height

    def add_to_entry(self, button):
        global tbCode
        line_num = get_cursor_line_number()
        content = tbCode.get("1.0", tk.END)
        lines = content.splitlines()
        if lines[line_num-1] == "":
            lines[line_num-1] = button
        else:
            lines.insert(line_num, button)
        tbCode.delete("1.0", tk.END)
        tbCode.insert(tk.END, "\n".join(map(str, lines)))


class Macro:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.location = projectLoc[:-(len(projectName)+4)] + "Macros\\" + name + ".txt"
        self.btn = tk.Button(self.parent, text=self.name, bd=1, relief="solid", highlightthickness=0, height=2, width=45, command=self.add_macro, font=font.Font, bg="#EEEEEE")
        self.btn.bind("<Button-3>", self.remove_macro)
        self.btn.pack(side=tk.TOP)
    
    def pack(self):
        if self.btn.winfo_exists() == False:
            self.btn = tk.Button(self.parent, text=self.name, bd=1, relief="solid", highlightthickness=0, height=2, width=45, command=self.add_macro, font=font.Font, bg="#EEEEEE")
            self.btn.bind("<Button-3>", self.remove_macro)
            self.btn.pack(side=tk.TOP)

    def destroy(self):
        self.btn.destroy()

    def add_macro(self):
        global tbCode
        line_num = get_cursor_line_number()
        content = tbCode.get("1.0", tk.END)
        lines = content.splitlines()
        if lines[line_num-1] == "":
            lines[line_num-1] = f"Macro({self.name})"
        else:
            lines.insert(line_num, f"Macro({self.name})")
        tbCode.delete("1.0", tk.END)
        tbCode.insert(tk.END, "\n".join(map(str, lines)))
    
    def remove_macro(self, event):
        result = messagebox.askquestion("Confirmation", f'Are you sure you want to delete "{self.name}" macro?')
        if result.lower() == 'yes':
            if os.path.isfile(self.location):
                os.remove(self.location)
                reload_side_frame_obj()


def get_txt_files(directory):
    txt_files = []
    
    try:
        for file_name in os.listdir(directory):
            if file_name.endswith(".txt"):
                txt_files.append(file_name)
    except OSError:
        print(f"Error: Unable to access directory {directory}")
    
    return txt_files

def is_key_on_keyboard(key_name):
    for name in pyautogui.KEYBOARD_KEYS:
        if key_name == name:
            return True
    return False

def is_number(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def add_tabs(number):
    string = ""
    for i in range(number):
        string += "\t"
    return string

def iteration_var(tabs):
    string = "i"
    for i in range(tabs):
        string += "i"
    return string
def start():
    save_time(None)
    save_stop(None)
    content = tbCode.get("1.0", tk.END)
    lines = content.splitlines()
    code_to_exec = f'''time.sleep({int(tbTime.get())})\n'''
    code_to_exec += "end_loop = False\n"
    code_to_exec += r"""
def play_actions(act):
    start = time.time()

    for action in act:
        action_type, *params, timestamp = action

        elapsed_time = time.time() - start
        delay = timestamp - elapsed_time

        pyautogui.PAUSE = max(0, delay)

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


"""
    code_to_exec += "\n"
    code_to_exec += f'macroLoc = r"{projectLoc[:-(len(projectName)+5)] + "/Macros/"}"\n'
    tabs = 0
    looptabs = []
    endlooptabs = []
    iftabs = []
    endiftabs = []
    stopkey = tbStop.get()
    line_num = 1
    for line in lines:
        line = line.split("#")[0]
        print(line)

        command = line.split('(')
        command[0] = command[0].replace(" ", '')
        command[0] = command[0].replace('\t', '')
        if len(command) > 2:
            messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
            return
        

        if command[0].replace(" ", "") == "ClickOnKeyboard":
            if len(command) != 2:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            arg = command[1].replace(" ", '')
            arg = arg[:-1]

            if is_key_on_keyboard(arg) == False:
                messagebox.showerror("Program Error", f"Not recognized key name '{arg}' in line {line_num}. \n {line}")
                return
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"keyboard.press_and_release('{arg}')\n"
        elif command[0].replace(" ", '') == "KeyDown":
            if len(command) != 2:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            arg = command[1].replace(" ", '')
            arg = arg[:-1]

            if is_key_on_keyboard(arg) == False:
                messagebox.showerror("Program Error", f"Not recognized key name '{arg}' in line {line_num}. \n {line}")
                return
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"keyboard.press('{arg}')\n"
        elif command[0].replace(" ", '') == "KeyUp":
            if len(command) != 2:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            arg = command[1].replace(" ", '')
            arg = arg[:-1]

            if is_key_on_keyboard(arg) == False:
                messagebox.showerror("Program Error", f"Not recognized key name '{arg}' in line {line_num}. \n {line}")
                return
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"keyboard.release('{arg}')\n"
        elif command[0].replace(" ", '') == "WaitSeconds":
            if len(command) != 2:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            arg = command[1].replace(" ", '')
            arg = arg[:-1]

            if is_number(arg) == False:
                messagebox.showerror("Program Error", f"Not recognized number '{arg}' in line {line_num}. \n {line}")
                return
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"time.sleep({arg})\n"
        elif command[0].replace(" ", '') == "WaitForKeyboard":
            if len(command) != 2:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            arg = command[1].replace(" ", '')
            arg = arg[:-1]

            if is_key_on_keyboard(arg) == False:
                messagebox.showerror("Program Error", f"Not recognized key name '{arg}' in line {line_num}. \n {line}")
                return
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"while end_loop == False: \n"
            code_to_exec += add_tabs(tabs+1)
            code_to_exec += f"if keyboard.is_pressed('{arg}'): \n"
            code_to_exec += add_tabs(tabs+2)
            code_to_exec += f"end_loop = True\n"
            code_to_exec += add_tabs(tabs+1)
            code_to_exec += f"while keyboard.is_pressed('{arg}'):\n"
            code_to_exec += add_tabs(tabs+2)
            code_to_exec += f"pass\n"
            code_to_exec += add_tabs(tabs+1)
            code_to_exec += f"if keyboard.is_pressed('{stopkey}'):\n"
            code_to_exec += add_tabs(tabs+2)
            code_to_exec += f"sys.exit()\n"
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"end_loop = False \n"
        elif command[0].replace(" ", '') == "MoveMouseTo":
            if len(command) != 2:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            arg = command[1].replace(" ", '')
            arg = arg[:-1]
            arg = arg.replace(" ", "")
            pos = arg.split(',')
            if len(pos) != 2:
                messagebox.showerror("Program Error", f"Bad position implementation in line {line_num}. \n {line}")
                return
            if pos[0].isdigit() == False or pos[1].isdigit() == False:
                messagebox.showerror("Program Error", f"Bad position implementation in line {line_num}. \n {line}")
                return
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"pyautogui.moveTo({pos[0]}, {pos[1]})\n"
        elif command[0].replace(" ", '') == "MouseUp":
            if len(command) != 2:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            arg = command[1].replace(" ", '')
            arg = arg[:-1]
            if arg != "right" and arg != "left":
                messagebox.showerror("Program Error", f"Not recognized mouse button in line {line_num}. \n {line}")
                return
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"pyautogui.mouseUp(button='{arg}')\n"
        elif command[0] == "MouseDown":
            if len(command) != 2:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            arg = command[1].replace(" ", '')
            arg = arg[:-1]
            if arg != "right" and arg != "left":
                messagebox.showerror("Program Error", f"Not recognized mouse button in line {line_num}. \n {line}")
                return
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"pyautogui.mouseDown(button='{arg}')\n"
        elif command[0] == "Loop":
            if len(command) != 2:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            arg = command[1].replace(" ", '')
            arg = arg[:-1]
            if arg.isdigit() == False:
                messagebox.showerror("Program Error", f"Not recognized digit '{arg}' in line {line_num}. \n {line}")
                return
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"for {iteration_var(tabs)} in range({arg}):\n"
            tabs += 1
            looptabs.append(tabs)
        elif command[0] == "EndLoop":
            if len(command) != 1:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            endlooptabs.append(tabs)
            tabs -= 1
        elif command[0].replace(" ", '') == "WaitForPixel":
            if len(command) != 2:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            arg = command[1].replace(" ", '')
            arg = arg[:-1]
            arg = arg.replace(" ", "")
            args = arg.split(',')
            if len(args) != 5:
                messagebox.showerror("Program Error", f"Bad arguments implementation in line {line_num}. \n {line}")
                return
            if args[0].isdigit() == False or args[1].isdigit() == False or args[2].isdigit() == False or args[3].isdigit() == False or args[4].isdigit() == False:
                messagebox.showerror("Program Error", f"Bad position implementation in line {line_num}. \n {line}")
                return
            if int(args[2]) < 0 or int(args[2]) > 256 or int(args[3]) < 0 or int(args[3]) > 256 or int(args[4]) < 0 or int(args[4]) > 256:
                messagebox.showerror("Program Error", f"Bad position implementation in line {line_num}. \n {line}")
                return
            
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"screen_width, screen_height = pyautogui.size()\n"
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"while True:\n"
            code_to_exec += add_tabs(tabs+1)
            code_to_exec += f"screen = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height))\n"
            code_to_exec += add_tabs(tabs+1)
            code_to_exec += f"pix = screen.getpixel(({args[0]}, {args[1]}))\n"
            code_to_exec += add_tabs(tabs+1)
            code_to_exec += f"tar = ({args[2]}, {args[3]}, {args[4]})\n"
            code_to_exec += add_tabs(tabs+1)
            code_to_exec += f"if pix == tar:\n"
            code_to_exec += add_tabs(tabs+2)
            code_to_exec += f"break\n"
        elif command[0] == "InfLoop":
            if len(command) != 1:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"while True:\n"
            tabs += 1
            looptabs.append(tabs)
        elif command[0] == "ExitLoop":
            if len(command) != 1:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"break\n"
        elif command[0] == "IfPixelColor":
            if len(command) != 2:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            arg = command[1].replace(" ", '')
            arg = arg[:-1]
            arg = arg.replace(" ", "")
            args = arg.split(',')
            print(args)
            if len(args) != 5:
                messagebox.showerror("Program Error", f"Bad arguments implementation in line {line_num}. \n {line}")
                return
            if args[0].isdigit() == False or args[1].isdigit() == False or args[2].isdigit() == False or args[3].isdigit() == False or args[4].isdigit() == False:
                messagebox.showerror("Program Error", f"Bad position implementation in line {line_num}. \n {line}")
                return
            if int(args[2]) < 0 or int(args[2]) > 256 or int(args[3]) < 0 or int(args[3]) > 256 or int(args[4]) < 0 or int(args[4]) > 256:
                messagebox.showerror("Program Error", f"Bad position implementation in line {line_num}. \n {line}")
                return
            
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"screen_width, screen_height = pyautogui.size()\n"
            code_to_exec += f"screen = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height))\n"
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"pix = screen.getpixel(({args[0]}, {args[1]}))\n"
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"tar = ({args[2]}, {args[3]}, {args[4]})\n"
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"if pix == tar:\n"
            tabs += 1
            iftabs.append(tabs)
        elif command[0] == "Else":
            if len(command) != 1:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            code_to_exec += add_tabs(tabs-1)
            code_to_exec += f"else:\n"
        elif command[0] == "EndIf":
            if len(command) != 1:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            endiftabs.append(tabs)
            tabs -= 1
        elif command[0] == "Macro":
            if len(command) != 2:
                messagebox.showerror("Program Error", f"Bad implementation in line {line_num}. \n {line}")
                return
            arg = command[1].replace(" ", '')
            arg = arg[:-1]
            #print(arg)
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"with open(macroLoc + '{arg}.txt', 'r') as file:\n"
            code_to_exec += add_tabs(tabs+1)
            code_to_exec += f'play_actions(text_to_action(file.read()))\n'
        elif command[0] == "":
            continue
        else:
            messagebox.showerror("Program Error", f"Not recognized command '{command[0]}' in line {line_num}. \n {line}")
            return
        
        if command[0] != "":
            code_to_exec += add_tabs(tabs)
            code_to_exec += f"if keyboard.is_pressed('{stopkey}'):\n"
            code_to_exec += add_tabs(tabs+1)
            code_to_exec += f"sys.exit()\n"
        line_num += 1
    
    if looptabs != endlooptabs:
        messagebox.showerror("Program Error", f"Incorrect loop implementation")
        return
    
    if iftabs != endiftabs:
        messagebox.showerror("Program Error", f"Incorrect if implementation")
        return

    try:
        exec(code_to_exec)
    except SystemExit:
        messagebox.showinfo("Bot Stopped", f"Bot succesfully has been stopped using key {stopkey}")
    except:
        messagebox.showerror("Executing Error", "There was an error while executing the program")


    libs = """
import tkinter as tk
from tkinter import font
import pyautogui
from tkinter import messagebox
import time
import keyboard
import sys
import os
import subprocess
from PIL import ImageGrab
from tkinter import Scrollbar
import tempfile
from tkinter import Canvas

"""
    code_to_exec = libs + code_to_exec
    show_in_notepad(code_to_exec)

    

def show_in_notepad(string):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(string.encode('utf-8'))
        temp_file_path = temp_file.name

    os.system(f'notepad.exe {temp_file_path}')


def get_cursor_line_number():
    cursor_position = tbCode.index(tk.INSERT)
    line_number = cursor_position.split('.')[0]
    return int(line_number)

def blocks():
    global isBlocksFrame
    isBlocksFrame = True
    btnBlocks.config(bg="#555555", activebackground="#555555", activeforeground="white")
    btnMacro.config(bg="#777777", activebackground="#777777", activeforeground="white")
    reload_side_frame_obj()

def macro():
    global isBlocksFrame
    isBlocksFrame = False
    btnMacro.config(bg="#555555", activebackground="#555555", activeforeground="white")
    btnBlocks.config(bg="#777777", activebackground="#777777", activeforeground="white")
    reload_side_frame_obj()

def add_macro():
    subprocess.run(['python', "macros.py"])
    reload_side_frame_obj()

def save_code(event):
    global tbCode
    tbCode.edit_modified(False)
    content = tbCode.get("1.0", tk.END)
    with open(projectLoc, "w") as file:
        file.write(content)

def load_code():
    global tbCode
    with open(projectLoc, "r") as file:
        lines = file.readlines()
        content = ""
        for line in lines:
            content += line
        tbCode.delete("1.0", tk.END)
        tbCode.insert(tk.END, content)

def save_time(event):
    global tbTime
    num = len(name) + 4
    loc = projectLoc[:-num]
    loc += "settings.txt"
    if is_number(tbTime.get()) == False:
        messagebox.showerror("Time Start Error", f"Time Start Error: {tbTime.get()} is not a number")
        load_settings()
        return
    stop = ""
    if os.path.isfile(loc) == True:
        with open(loc, 'r') as file:
            stop = file.readline().replace('\n', '')
    with open(loc, 'w') as file:
        file.write(stop + "\n" + tbTime.get())

def helper():
    subprocess.run(['python', "posHelper.py"])

def save_stop(event):
    global tbStop
    num = len(name) + 4
    loc = projectLoc[:-num]
    loc += "settings.txt"
    if is_key_on_keyboard(tbStop.get()) == False:
        messagebox.showerror("Stop Time Error", f"Stop Time Error: {tbStop.get()} is not a key")
        load_settings()
        return
    time = ""
    if os.path.isfile(loc) == True:
        with open(loc, 'r') as file:
            lines = file.readlines()
            if len(lines) == 2:
                time = lines[1].replace('\n', '')
    with open(loc, 'w') as file:
        file.write(tbStop.get() + "\n" + time)

def load_settings():
    num = len(name) + 4
    loc = projectLoc[:-num]
    loc += "settings.txt"
    if os.path.isfile(loc) == True:
        with open(loc, 'r') as file:
            lines = file.readlines()
            if len(lines) == 1:
                tbStop.delete(0, tk.END)
                tbStop.insert(0, lines[0].replace('\n', ''))
            if len(lines) == 2:
                tbStop.delete(0, tk.END)
                tbStop.insert(0, lines[0].replace('\n', ''))
                tbTime.delete(0, tk.END)
                tbTime.insert(0, lines[1].replace('\n', ''))

def reload_side_frame_obj():
    if isBlocksFrame:
        #Blocks
        global btnAddMacro
        global codingBlocks
        global btnMacro
        global btnBlocks
        global frameMacros
        global canvas
        global scrollbar
        global macroBlocks
        global macros_frame

        btnMacro.destroy()
        btnBlocks.destroy()
        try:
            btnAddMacro.destroy()
        except:
            pass
        try:
            frameMacros.destroy()
        except:
            pass
        btnBlocks = tk.Button(frameMenu, text="Blocks", bg="#555555", fg="white", command=blocks, font=("Helvetica", 15), width=18, bd=1, relief="solid", highlightthickness=0, activebackground="#555555", activeforeground="white", highlightcolor="white")
        btnMacro = tk.Button(frameMenu, text="Macro", bg="#777777", fg="white", command=macro, font=("Helvetica", 15), width=18, bd=1, relief="solid", highlightthickness=0, activebackground="#777777", activeforeground="white", highlightcolor="white")

        for mcr in macroBlocks:
            mcr.destroy()

        codingBlocks = []
        codingBlocks.append(SubMenu(frameMenu, ["Loop( number_of_repeats )", "ExitLoop", "InfLoop", "EndLoop"], "Loop", is_last=True))
        codingBlocks.append(SubMenu(frameMenu, ["IfPixelColor(x, y, r, g, b)", "Else", "EndIf"], "If"))
        codingBlocks.append(SubMenu(frameMenu, ["WaitSeconds( number_of_seconds )", "WaitForKeyboard( keyname )", "WaitForPixel(x, y, r, g, b)", ], "Wait"))
        codingBlocks.append(SubMenu(frameMenu, ["MouseDown( left / right )", "MouseUp( left / right )", "MoveMouseTo(x, y)"], "Mouse"))
        codingBlocks.append(SubMenu(frameMenu, ["ClickOnKeyboard( keyname )", "KeyDown( keyname )", "KeyUp( keyname )", "WriteText( text )"], "Keyboard"))

        #Generate
        for block in codingBlocks:
            block.pack()
        
        btnBlocks.pack(anchor="nw", side=tk.LEFT)
        btnMacro.pack(anchor="nw", side=tk.LEFT)
        btnBlocks["state"] = "disabled"
        btnMacro["state"] = "normal"
        btnBlocks["disabledforeground"] = "white"
    else:
        #Macros
        btnMacro.destroy()
        btnBlocks.destroy()
        btnBlocks = tk.Button(frameMenu, text="Blocks", bg="#777777", fg="white", command=blocks, font=("Helvetica", 15), width=18, bd=1, relief="solid", highlightthickness=0, activebackground="#555555", activeforeground="white", highlightcolor="white")
        btnMacro = tk.Button(frameMenu, text="Macro", bg="#555555", fg="white", command=macro, font=("Helvetica", 15), width=18, bd=1, relief="solid", highlightthickness=0, activebackground="#777777", activeforeground="white", highlightcolor="white")

        for block in codingBlocks:
            block.destroy()
        
        try:
            btnAddMacro.destroy()
        except:
            pass
        btnAddMacro = tk.Button(frameMenu, text="Add Macro", bg="green", fg="white", command=add_macro, font=("Helvetica", 30), relief=tk.FLAT, bd=0, width=10, activebackground="dark green", activeforeground="white")
        

        try:
            frameMacros.destroy()
        except:
            pass

        for mcr in macroBlocks:
            mcr.destroy()

        frameMacros = tk.Frame(frameMenu, width=410, height=850, bg="#666666")
        frameMacros.pack(side=tk.BOTTOM, anchor="sw")
        btnAddMacro.pack(side=tk.BOTTOM, anchor="sw", padx=85, pady=50)
        frameMacros.pack_propagate(False)
        scrollbar = Scrollbar(frameMacros, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas = Canvas(frameMacros, yscrollcommand=scrollbar.set, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.configure(bg="#666666")
        macros_frame = tk.Frame(canvas, bg="#666666")
        canvas.create_window((0, 0), window=macros_frame, anchor="nw")
        scrollbar.config(command=canvas.yview)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.bind("<MouseWheel>", on_mousewheel)

        macroBlocks = []
        txt_files = get_txt_files(projectLoc[:-(len(projectName)+4)] + "Macros\\")
        for txt in txt_files:
            macroBlocks.append(Macro(txt[:-4], macros_frame))

        for mcr in macroBlocks:
            mcr.pack()
            mcr.btn.bind("<MouseWheel>", on_mousewheel)
        
        if len(macroBlocks) >= 19:
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.configure(yscrollcommand=scrollbar.set)
        else:
            scrollbar.pack_forget()
            canvas.configure(yscrollcommand=None)
        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        btnBlocks.pack(anchor="nw", side=tk.LEFT)
        btnMacro.pack(anchor="nw", side=tk.LEFT)

        btnMacro["state"] = "disabled"
        btnBlocks["state"] = "normal"
        btnMacro["disabledforeground"] = "white"

isBlocksFrame = True
projectLoc = ""
codingBlocks = []
macroBlocks = []

def on_canvas_configure(event):
    if len(macroBlocks) >= 19:
        canvas.configure(scrollregion=canvas.bbox("all"))


def on_mousewheel(event):
    if len(macroBlocks) >= 19:
        canvas_y = canvas.winfo_y()
        canvas_height = canvas.winfo_height()

        if canvas_y <= event.y <= canvas_y + canvas_height:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

# Create the main window
root = tk.Tk()
with open('name.txt', 'r') as file:
    name = file.readline()
    loc = file.readline()
projectLoc = loc
name = name.replace('\n', '')
projectName = name
root.title(name + " - Bot Maker")

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the x and y coordinates for the window to be centered
x_coordinate = (screen_width - 1920) // 2
y_coordinate = (screen_height - 1080) // 2

# Set the window size and position
root.geometry(f"1920x1080+{x_coordinate}+{y_coordinate}")
root.resizable(width=False, height=False)

# Create a frame on the left side with dark gray background
frameMenu = tk.Frame(root, width=410, height=screen_height, bg="dark gray")
frameMenu.pack(side=tk.LEFT, fill=tk.Y)
btnAddMacro = tk.Button(frameMenu, text="Add Macro", bg="green", fg="white", command=add_macro, font=("Helvetica", 30), relief=tk.FLAT, bd=0, width=10, activebackground="dark green", activeforeground="white")
frameMacros = tk.Frame(frameMenu, width=400, height=700, bg="dark gray")
scrollbar = Scrollbar(frameMacros, orient=tk.VERTICAL)
canvas = Canvas(frameMacros, yscrollcommand=scrollbar.set, highlightthickness=0)
macros_frame = tk.Frame(canvas, bg="#666666")

# Create the green button with white text, adjust font size, padding, and remove onclick effect and border
btnStart = tk.Button(root, text="Start", bg="green", fg="white", command=start, font=("Helvetica", 30),
                   relief=tk.FLAT, bd=0, width=6, activebackground="dark green", activeforeground="white")  # Set width to 100 pixels
# Create the green button with white text, adjust font size, padding, and remove onclick effect and border
btnBlocks = tk.Button(frameMenu, text="Blocks", bg="#555555", fg="white", command=blocks, font=("Helvetica", 15),
                   width=18, bd=1, relief="solid", highlightthickness=0, activebackground="#555555", activeforeground="white", highlightcolor="white")  # Set width to 100 pixels
# Create the green button with white text, adjust font size, padding, and remove onclick effect and border
btnMacro = tk.Button(frameMenu, text="Macro", bg="#777777", fg="white", command=macro, font=("Helvetica", 15),
                   width=18, bd=1, relief="solid", highlightthickness=0, activebackground="#777777", activeforeground="white", highlightcolor="white")  # Set width to 100 pixels
lblCode = tk.Label(root, text="Code:", font=("Heltevica", 30))
tbCode = tk.Text(root, width=155, height=55)
tbCode.bind("<<Modified>>", save_code)
lblTime = tk.Label(root, text="Time before start: ", font=font.Font())
btnHelper = tk.Button(root, text="Position and Color Helper", command=helper, font=("Heltevica", 15), fg="white", bg="green", bd=1, relief=tk.FLAT, activebackground="darkgreen", activeforeground="white")
tbTime = tk.Entry(root, width=30)
lblTime.pack(side=tk.TOP)
tbTime.pack(side=tk.TOP)
lblStop = tk.Label(root, text="Stop Key: ", font=font.Font())
tbStop = tk.Entry(root, width=30)
lblStop.pack(side=tk.TOP)
tbStop.pack(side=tk.TOP)
btnHelper.pack(side=tk.TOP, pady=30)
tbTime.bind("<FocusOut>", save_time)
tbStop.bind("<FocusOut>", save_stop)

# Set padding for the button (10 px from top and right)
btnStart.pack(pady=20, padx=20, anchor="ne")
btnBlocks.pack(anchor="nw", side=tk.LEFT)
btnMacro.pack(anchor="nw", side=tk.LEFT)
lblCode.pack(side=tk.TOP)
tbCode.pack()

load_code()
reload_side_frame_obj()
load_settings()

# Run the Tkinter event loop
root.mainloop()
