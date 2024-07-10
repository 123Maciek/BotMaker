with open("version.txt") as file:
    version = file.read().strip()

main_ver = int(version.split(".")[0])
small_ver = int(version.split(".")[1])

def is_int(number):
    try:
        number = int(number)
        return True
    except:
        return False

def get_option(question, options):
    for i in range(1, len(options)+1):
        print(str(i) + ". " + options[i-1])
    anwser = input(question)

    if is_int(anwser):
        num = int(anwser)
        if num > 0 and num <= len(options):
            return num
        else:
            print("Incorect anwser.")
            return get_option(question, options)
    else:
        print("Incorect anwser.")
        return get_option(question, options)

print(f"Current version: v{version}")

anwser = get_option("Update version to: ", [f"v{main_ver}.{small_ver+1}", f"v{main_ver+1}.0", "Exit"])
if anwser == 0:
    with open("version.txt", 'w') as file:
        file.write(f"{main_ver}.{small_ver+1}")
elif anwser == 1:
    with open("version.txt", "w") as file:
        file.write(f"{main_ver+1}.0")