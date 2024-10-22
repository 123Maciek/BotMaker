import tkinter as tk
import os
import subprocess
from tkinter import font
from tkinter import messagebox
import shutil
from tkinter import Scrollbar
from tkinter import *

class Project:
    def __init__(self, parent, name, localization, number):
        self.parent = parent
        self.name = name
        self.localization = localization
        self.number = number
        self.btn = tk.Button(self.parent, text=self.name, fg="white", bg="dark gray", activebackground="dark gray", activeforeground="white", bd=1, relief="solid", highlightthickness=0, height=2, width=100, command=self.set_number, font=font.Font, anchor="w", padx=50)
        self.btn.pack(side=tk.TOP)

    def pack(self):
        if self.btn.winfo_exists() == False:
            self.btn = tk.Button(self.parent, text=self.name, fg="white", bg="dark gray", activebackground="dark gray", activeforeground="white", bd=1, relief="solid", highlightthickness=0, height=2, width=100, command=self.set_number, font=font.Font, anchor="w", padx=50)
            self.btn.pack(side=tk.TOP)

    def set_number(self):
        global selected_project_number
        selected_project_number = self.number
        global projects
        for project in projects:
            project.btn.config(font=font.Font(), fg = "white")
        self.btn.config(font=font.Font(), fg="black")

    def destroy(self):
        self.btn.destroy()

def createNewProject():
    subprocess.run(['python', "addproject.py"])
    loadProjectsFromFile()

def check_for_reset():
    with open("needreset.txt", 'r') as file:
        line = file.readline()
    if line == "True":
        with open("needreset.txt", 'w') as file:
            file.write("False")
        subprocess.run(["python", "program.py"])

def deleteProject():
    global  projects
    if len(projects) > 0:
        result = messagebox.askquestion("Confirmation", f"Are you sure u want to delete {projects[selected_project_number].name}")
        if result == "yes":
            delete_line("projects.txt", selected_project_number + 1)
            length = len(projects[selected_project_number].name) + 5
            new_loc = projects[selected_project_number].localization[:-length]
            if os.path.isdir(new_loc):
                try:
                    shutil.rmtree(new_loc)
                except OSError as e:
                    pass
            loadProjectsFromFile()

def openProject():
    if len(projects) > 0:
        if os.path.isfile("name.txt"):
            os.remove("name.txt")
        with open('name.txt', 'w') as file:
            file.write(projects[selected_project_number].name)
            file.write("\n")
            file.write(projects[selected_project_number].localization)
        subprocess.run(['python', "program.py"])
        with open("needreset.txt", 'r') as file:
            line = file.readline()
            if line == "True":
                root.destroy()
                subprocess.run(["cscript.exe", "window.vbs"])

def delete_line(file_path, line_number):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    if 1 <= line_number <= len(lines):
        del lines[line_number - 1]
        with open(file_path, 'w') as file:
            file.writelines(lines)

def checkForDupes(file_name):
    if os.path.isfile(file_name):
        with open(file_name, 'r') as file:
            lines = file.readlines()
            num = 1
            seen = set()
            for line in lines:
                if line in seen:
                    return num
                else:
                    seen.add(line)
                num = num + 1
            return 0

def loadProjectsFromFile():
    global projects
    global selected_project_number
    global canvas
    global scrollbar
    
    to_delete_line = checkForDupes("projects.txt")
    while to_delete_line != 0:
        delete_line("projects.txt", to_delete_line)
        to_delete_line = checkForDupes("projects.txt")
    selected_project_number = 0
    if len(projects) > 0:
        for project in projects:
            project.destroy()
    projects = []
    with open("projects.txt", 'r') as file:
        lines = file.readlines()
        num = 1
        for i, line in enumerate(lines):
            info = line.strip().split(' ')
            if len(info) > 1:
                name = info[0]
                localization = ""
                for j in info:
                    if j != name:
                        localization += j
                        localization += " "
                loc2 = localization[:-1]
                if os.path.isfile(loc2) == False:
                    delete_line("projects.txt", num)
                    loadProjectsFromFile()
                    return
                projects.append(Project(projects_frame, name, loc2, i))
                projects[i].pack()
                projects[i].btn.bind("<MouseWheel>", on_mousewheel)
            num = num + 1
    
    if len(projects) >= 10:
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
    else:
        scrollbar.pack_forget()
        canvas.configure(yscrollcommand=None)

    if len(projects) > 0:
        projects[0].btn.config(font=font.Font(), fg="black")
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

selected_project_number = 0
projects = []

# Create the main window
root = tk.Tk()
root.title("Bot Maker")
root.configure(bg="lightgray")

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the x and y coordinates for the window to be centered
x_coordinate = (screen_width - 800) // 2
y_coordinate = (screen_height - 600) // 2

# Set the window size and position
root.geometry(f"800x600+{x_coordinate}+{y_coordinate}")
root.resizable(width=False, height=False)

# Create the project frame with a vertical scrollbar
frameProjects = tk.Frame(root, width=700, height=400, bg="dark gray")
frameProjects.pack(anchor="sw", padx=50, pady=30, side=tk.BOTTOM, fill=tk.BOTH, expand=True)
frameProjects.pack_propagate(False)

# Create and pack the vertical scrollbar
scrollbar = Scrollbar(frameProjects, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create the canvas to hold the projects
canvas = Canvas(frameProjects, yscrollcommand=scrollbar.set, highlightthickness=0)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
canvas.configure(bg="dark gray")

# Create a frame inside the canvas to hold the projects
projects_frame = tk.Frame(canvas, bg="dark gray")
canvas.create_window((0, 0), window=projects_frame, anchor="nw")

# Configure the scrollbar to work with the canvas
scrollbar.config(command=canvas.yview)

# Function to update the scrollbar when the canvas size changes
def on_canvas_configure(event):
    if len(projects) >= 10:
        canvas.configure(scrollregion=canvas.bbox("all"))

# Function to handle mouse wheel scrolling
def on_mousewheel(event):
    if len(projects) >= 10:
        canvas_y = canvas.winfo_y()
        canvas_height = canvas.winfo_height()

        if canvas_y <= event.y <= canvas_y + canvas_height:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

# Bind the canvas to the scrollbar
canvas.bind("<Configure>", on_canvas_configure)
canvas.bind("<MouseWheel>", on_mousewheel)

loadProjectsFromFile()

lblTitle = tk.Label(root, text="Bot Maker", font=("Arial", 30), fg="Black", bg="lightgray")
lblTitle.pack(anchor="n", pady=20)
btnAddProject = tk.Button(root, text="Create New Project", font=("Arial", 12), fg="White", bg="green", activebackground="green", activeforeground="white", relief=tk.FLAT, bd=0, command=createNewProject)
btnAddProject.pack(side=tk.LEFT, anchor="n", padx=(50, 10))
btnAddProject = tk.Button(root, text="Remove Project", font=("Arial", 12), fg="White", bg="red", activebackground="red", activeforeground="white", relief=tk.FLAT, bd=0, command=deleteProject)
btnAddProject.pack(side=tk.LEFT, anchor="n", padx=10)
btnAddProject = tk.Button(root, text="Open Project", font=("Arial", 12), fg="White", bg="dark blue", activebackground="dark blue", activeforeground="white", relief=tk.FLAT, bd=0, command=openProject)
btnAddProject.pack(side=tk.LEFT, anchor="n", padx=10)

check_for_reset()

# Run the Tkinter event loop
root.mainloop()