import subprocess
import os
import shutil
import stat
import github_api
import tkinter as tk
from tkinter import ttk, messagebox

def clone_private_repo(username, token, repo_url, destination_path):
    clone_url = f"https://{username}:{token}@{repo_url}"
    subprocess.run(["git", "clone", clone_url, destination_path])

destination_directory = "\\".join(os.getcwd().split("\\")[:-1]) + "\\BotProgrammerClone"
outside_folder = "\\".join(os.getcwd().split("\\")[:-1])

def remove_read_only(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def delete_files_except_script(directory):
    script_name = os.path.basename(__file__)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) and filename not in ["name.txt", "projects.txt", "start.bat", "window.vbs"]:
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            pass

def main():
    if os.path.isdir(destination_directory):
        shutil.rmtree(destination_directory, onerror=remove_read_only)

    # Simulate progress for cloning repo
    github_api.download_newest_files(destination_directory)
    progress_var.set(40)
    root.update_idletasks()

    # Simulate progress for removing files
    os.remove(destination_directory + "\\download_repository.py")
    os.remove(destination_directory + "\\name.txt")
    os.remove(destination_directory + "\\projects.txt")
    os.remove(destination_directory + "\\start.bat")
    os.remove(destination_directory + "\\window.vbs")
    progress_var.set(70)
    root.update_idletasks()

    delete_files_except_script(os.getcwd())
    progress_var.set(85)
    root.update_idletasks()

    try:
        shutil.copytree(destination_directory, os.getcwd(), dirs_exist_ok=True)
    except Exception as e:
        pass

    if os.path.isdir(destination_directory):
        shutil.rmtree(destination_directory, onerror=remove_read_only)
    progress_var.set(100)
    root.update_idletasks()

    with open("needreset.txt", 'w') as file:
        file.write("True")

    messagebox.showinfo("Info", "BotMaker needs a reset")
    root.destroy()

root = tk.Tk()
root.title("Downloading...")
root.geometry("300x100")

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

root.after(100, main)
root.mainloop()
