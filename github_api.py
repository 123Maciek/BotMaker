import requests
import git

def get_server_version():
    url = "https://raw.githubusercontent.com/123Maciek/BotProgrammer/main/version.txt"
    response = requests.get(url)
    if response.status_code == 200:
        line = response.text
        return line
    return None

def download_newest_files(path):
    repo_url = "https://github.com/123Maciek/BotProgrammer"
    try:
        git.Repo.clone_from(repo_url, path)
    except Exception as e:
        pass

def get_my_version():
    with open("version.txt", "r") as f:
        line = f.readline()
        return line

print()