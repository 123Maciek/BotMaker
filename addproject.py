import tkinter as tk
import os
import subprocess
from tkinter import font
from tkinter import filedialog

def add_line_to_file(file_path, line_to_add):
    try:
        with open(file_path, 'a') as file:
            file.write(line_to_add + '\n')
    except Exception as e:
        print(f"Error: {e}")

def open_folder_dialog():
    folder_path = filedialog.askdirectory(initialdir="Documents")
    if folder_path is not None:
        return folder_path

def set_project_path():
    global path
    path = open_folder_dialog()
    lblDir.config(text=path)

def sumbit():
    global path
    validated = True

    lblNameValidation.config(text="")
    lblDirectoryValidation.config(text="")

    #Name validation
    if len(tbName.get()) < 4:
        lblNameValidation.config(text="The Name must be longer then 3 letters")
        validated = False
    if len(tbName.get()) > 31:
        lblNameValidation.config(text="The name cannot be longer than 30 letters")
        validated = False
    if ' ' in tbName.get():
        lblNameValidation.config(text="The name cannot contain space")
        validated = False
    if path == "":
        lblDirectoryValidation.config(text="You must select project directory")
        validated = False

    name_folder_path2 = os.path.join(path, tbName.get())
    if validated == True:
        if os.path.exists(name_folder_path2):
            lblDirectoryValidation.config(text="Project already exists")
            validated = False

    #Create
    if validated == True:
        name_folder_path = os.path.join(path, tbName.get())
        try:
            os.makedirs(name_folder_path)
        except FileExistsError:
            pass
        macro_folder_path = os.path.join(name_folder_path, "Macros")
        try:
            os.makedirs(macro_folder_path)
        except FileExistsError:
            pass
        name_file_path = os.path.join(name_folder_path, f"{tbName.get()}.txt")
        with open(name_file_path, 'w') as file:
            pass
        add_line_to_file("projects.txt", f"{tbName.get()} {name_file_path}")
        if os.path.isfile("name.txt"):
            os.remove("name.txt")
        with open('name.txt', 'w') as file:
            file.write(tbName.get())
            file.write("\n")
            file.write(name_file_path)
        root.destroy()
        subprocess.run(['python', "main.py"])




path = ""

# Create the main window
root = tk.Tk()
root.title("Bot Programmer")
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

lblTitle = tk.Label(root, text="Create Project", font=("Arial", 30), fg="darkgreen", bg="lightgray")
lblTitle.pack(anchor="n", pady=20)

frameName = tk.Frame(root, width=600, height=150, bg="lightgray")
frameName.pack()
frameDir = tk.Frame(root, width=600, height=150, bg="lightgray")
frameDir.pack(anchor="n", pady=50)

#Name
tbName = tk.Entry(frameName, width=30, font=font.Font())
lblName = tk.Label(frameName, text="Project Name: ", font=font.Font(), bg="lightgray")
lblNameValidation = tk.Label(frameName, text="", bg="lightgray", fg="red", font=font.Font())
lblNameValidation.pack(side=tk.BOTTOM, anchor="sw", padx=10, pady=(0, 10))
lblName.pack(side=tk.LEFT, anchor="nw", padx=10)
tbName.pack(side=tk.LEFT, anchor="nw", padx=10)

#Localization
btnPath = tk.Button(frameDir, text="Set Direcory", font=font.Font(), command=set_project_path)
lblDir = tk.Label(frameDir, text="", font=font.Font(), bg="lightgray")
lblDirectoryValidation = tk.Label(frameDir, text="", font=font.Font(), bg="lightgray", fg="red")
btnPath.pack()
lblDir.pack()
lblDirectoryValidation.pack(side=tk.BOTTOM)

#Submit
btnSubmit = tk.Button(root, text="SUBMIT", font=font.Font(), command=sumbit)
btnSubmit.pack(side=tk.BOTTOM, anchor="center", pady=50)

# Run the Tkinter event loop
root.mainloop()