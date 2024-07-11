import tkinter as tk
import pyperclip
import os
from tkinter import messagebox
from github import Github
import subprocess
import github_api
from PIL import Image, ImageTk

def copy_path():
    path_to_copy = projectLoc.strip()
    pyperclip.copy(path_to_copy)

def open_folder():
    path_to_open = projectLoc.strip()
    os.startfile(path_to_open)

def close():
    root.destroy()

def apply():
    first = "1"
    second = "1"
    if checkbox_var1.get() == 1:
        first = "1"
    elif checkbox_var2.get() == 1:
        first = "2"
    elif checkbox_var3.get() == 1:
        first = "3"
    if checkbox_var4.get() == 1:
        second = "1"
    elif checkbox_var5.get() == 1:
        second = "2"
    save = first + second
    with open(settings_location, 'r') as file:
        line = file.readline()
    if save != line:
        response = messagebox.askyesno("Confirmation", "Do you want to save your changes?")
        if response == True:
            with open(settings_location, 'w') as file:
                file.write(save)
    root.destroy()

def load_settings():
    if os.path.isfile(settings_location):
        with open(settings_location, "r") as file:
            line = file.readline()
            if line[0] == "1":
                checkbox_var1.set(1)
            elif line[0] == "2":
                checkbox_var2.set(1)
            elif line[0] == "3":
                checkbox_var3.set(1)
            if line[1] == "1":
                checkbox_var4.set(1)
            elif line[1] == "2":
                checkbox_var5.set(1)
    else:
        with open(settings_location, "w") as file:
            file.write("11")
        load_settings()

def update():
    subprocess.run(["python", "download_repository.py"])
    root.destroy()

def check_for_update():
    if myVersion != serverVersion:
        versionInfo.config(text=f"Current version: v{myVersion} \n There is an update available to new version: v{serverVersion}")
        updateButton.place(relx=0.5, rely=0.7, anchor=tk.CENTER)
        versionCanvas.create_image(0, 0, anchor=tk.NW, image=tk_image)

# Read project location from file
with open("name.txt", 'r') as file:
    projectName = file.readline()
    projectLoc = "\\".join(file.readline().replace("/", "\\").split("\\")[:-1]) + "\\"

myVersion = github_api.get_my_version()
serverVersion = github_api.get_server_version()

settings_location = projectLoc + "set.txt"

# Create tkinter window
root = tk.Tk()
root.title("Settings")

# Calculate window position
window_width = 1728
window_height = 972
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Main title label
label = tk.Label(root, text="Settings", fg="black", font=("Helvetica", 48))
label.pack(pady=20)

root.resizable(width=False, height=False)

# Frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=50)

# Apply button (not used in this example)
apply_button = tk.Button(button_frame, text="Apply", bg="green", fg="white", font=("Helvetica", 20),
                         activebackground="green", activeforeground="white", command=apply)
apply_button.pack(side=tk.LEFT, padx=10)

# Close button (not used in this example)
close_button = tk.Button(button_frame, text="Close", bg="red", fg="white", font=("Helvetica", 20),
                         activebackground="red", activeforeground="white", command=close)
close_button.pack(side=tk.RIGHT, padx=10)

# Container frame for main content
frames_container = tk.Frame(root)
frames_container.pack(expand=True, fill=tk.BOTH, padx=20, pady=(20, 0))

# Frame for displaying project path
fFolder = tk.Frame(frames_container, width=window_width//2, height=(window_height-200)//2, bd=2, relief=tk.SOLID,
                   highlightbackground="black")
fFolder.grid(row=0, column=0, padx=5, pady=5)
lFolder = tk.Label(fFolder, text="Folder", font=("Helvetica", 24))
lFolder.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
folderPathText = f"Project path: {projectLoc}"
folderPath = tk.Label(fFolder, text=folderPathText, font=("Helvetica", 15), wraplength=700)
folderPath.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

# Buttons for copying path and opening folder
copy_button = tk.Button(fFolder, text="Copy Path", command=copy_path)
copy_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

open_button = tk.Button(fFolder, text="Open Folder", command=open_folder)
open_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

# Additional frames (not used in this example)
fCode = tk.Frame(frames_container, width=window_width//2, height=(window_height-200)//2, bd=2, relief=tk.SOLID,
                 highlightbackground="black")
fCode.grid(row=0, column=1, padx=5, pady=5)
lCode = tk.Label(fCode, text="Code", font=("Helvetica", 24))
lCode.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

# Variables to track the state of checkboxes
checkbox_var1 = tk.IntVar()
checkbox_var2 = tk.IntVar()
checkbox_var3 = tk.IntVar()

# Function to handle checkbox selection
def select_checkbox(checkbox_var):
    if checkbox_var.get() == 1:
        if checkbox_var == checkbox_var1:
            checkbox_var2.set(0)
            checkbox_var3.set(0)
        elif checkbox_var == checkbox_var2:
            checkbox_var1.set(0)
            checkbox_var3.set(0)
        elif checkbox_var == checkbox_var3:
            checkbox_var1.set(0)
            checkbox_var2.set(0)
    else:
        checkbox_var1.set(1)
        checkbox_var2.set(0)
        checkbox_var3.set(0)


# Checkboxes
checkbox1 = tk.Checkbutton(fCode, text="Don't show python code", variable=checkbox_var1, onvalue=1, offvalue=0, command=lambda: select_checkbox(checkbox_var1), font=("Helvetica", 15))
checkbox1.place(relx=0.05, rely=0.3, anchor=tk.W)

checkbox2 = tk.Checkbutton(fCode, text="Show python code without macro txt packed (for personal use on this computer)", variable=checkbox_var2, onvalue=1, offvalue=0, command=lambda: select_checkbox(checkbox_var2), font=("Helvetica", 15))
checkbox2.place(relx=0.05, rely=0.45, anchor=tk.W)

checkbox3 = tk.Checkbutton(fCode, text="Show python code with macro txt packed (for sharing and compiling to exe)", variable=checkbox_var3, onvalue=1, offvalue=0, command=lambda: select_checkbox(checkbox_var3), font=("Helvetica", 15))
checkbox3.place(relx=0.05, rely=0.6, anchor=tk.W)

#Console
fConsole = tk.Frame(frames_container, width=window_width//2, height=(window_height-200)//2, bd=2, relief=tk.SOLID,
                    highlightbackground="black")
fConsole.grid(row=1, column=0, padx=5, pady=5)
lConsole = tk.Label(fConsole, text="Console", font=("Helvetica", 24))
lConsole.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

checkbox_var4 = tk.IntVar()
checkbox_var5 = tk.IntVar()

def select_checkbox2(checkbox_var):
    if checkbox_var.get() == 1:
        if checkbox_var == checkbox_var4:
            checkbox_var5.set(0)
        elif checkbox_var == checkbox_var5:
            checkbox_var4.set(0)
    else:
        checkbox_var4.set(1)
        checkbox_var5.set(0)

checkbox1 = tk.Checkbutton(fConsole, text="Don't show console", variable=checkbox_var4, onvalue=1, offvalue=0, command=lambda: select_checkbox2(checkbox_var4), font=("Helvetica", 15))
checkbox1.place(relx=0.05, rely=0.3, anchor=tk.W)

checkbox2 = tk.Checkbutton(fConsole, text="Show console", variable=checkbox_var5, onvalue=1, offvalue=0, command=lambda: select_checkbox2(checkbox_var5), font=("Helvetica", 15))
checkbox2.place(relx=0.05, rely=0.45, anchor=tk.W)

#Version
def make_bg_transparent(img, bg_color=(255, 255, 255)):
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[:3] == bg_color:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

fVersion = tk.Frame(frames_container, width=window_width//2, height=(window_height-200)//2, bd=2, relief=tk.SOLID,
                    highlightbackground="black")
fVersion.grid(row=1, column=1, padx=5, pady=5)
lVersion = tk.Label(fVersion, text="Version", font=("Helvetica", 24))
lVersion.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
versionInfo = tk.Label(fVersion, text=f"Current version: v{myVersion} \n Program is app to date \n No downloads required :)", font=("Helvetica", 15), wraplength=700)
versionInfo.place(relx=0.5, rely=0.3, anchor=tk.CENTER)
versionCanvas = tk.Canvas(fVersion, width=50, height=50)
versionCanvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
image_path = 'img\\warning.png'
pil_image = Image.open(image_path)
pil_image = pil_image.resize((50, 50), Image.Resampling.LANCZOS)
tk_image = ImageTk.PhotoImage(pil_image)

updateButton = tk.Button(fVersion, text="Update", font=("Helvetica", 15), command=update, bg="yellow", activebackground="yellow", activeforeground="black")
check_for_update()

# Grid configuration for responsive layout
frames_container.grid_rowconfigure(0, weight=1)
frames_container.grid_rowconfigure(1, weight=1)
frames_container.grid_columnconfigure(0, weight=1)
frames_container.grid_columnconfigure(1, weight=1)

load_settings()

# Start tkinter main loop
root.mainloop()
