import subprocess
import os
import github_login

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

#clone_private_repo(github_username, github_token, repository_url, destination_directory)
