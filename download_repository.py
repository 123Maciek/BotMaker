import subprocess
import os
import sys
import shutil
import github_login
import stat

def clone_private_repo(username, token, repo_url, destination_path):
    # Construct the clone URL with the username and PAT
    clone_url = f"https://{username}:{token}@{repo_url}"
    
    # Use subprocess to run the git clone command
    subprocess.run(["git", "clone", clone_url, destination_path])

# Replace these variables with your actual GitHub username, PAT, repo URL, and local destination path
github_username = github_login.USERNAME
github_token = github_login.TOKEN
repository_url = "github.com/123Maciek/BotProgrammer.git"
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
            if os.path.isfile(file_path) and filename != script_name and filename != "name.txt" and filename != "projects.txt" and filename != "start.bat" and filename != "window.vbs":
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            pass


if os.path.isdir(destination_directory):
    shutil.rmtree(destination_directory, onerror=remove_read_only)

clone_private_repo(github_username, github_token, repository_url, destination_directory)

os.remove(destination_directory + "\\download_repository.py")
os.remove(destination_directory + "\\name.txt")
os.remove(destination_directory + "\\projects.txt")
os.remove(destination_directory + "\\start.bat")
os.remove(destination_directory + "\\window.vbs")

delete_files_except_script(os.getcwd())

try:
    shutil.copytree(destination_directory, os.getcwd(), dirs_exist_ok=True)
except:
    pass

if os.path.isdir(destination_directory):
    shutil.rmtree(destination_directory, onerror=remove_read_only)

with open("needreset.txt", 'w') as file:
    file.write("True")