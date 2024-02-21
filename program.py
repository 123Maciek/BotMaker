import tkinter as tk

def start():
    pass

def blocks():
    isBlocksFrame = True
    btnBlocks.config(bg="#555555", activebackground="#555555", activeforeground="white")
    btnMacro.config(bg="#777777", activebackground="#777777", activeforeground="white")

def macro():
    isBlocksFrame = False
    btnMacro.config(bg="#555555", activebackground="#555555", activeforeground="white")
    btnBlocks.config(bg="#777777", activebackground="#777777", activeforeground="white")

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

isBlocksFrame = True
projectLoc = ""

# Create the main window
root = tk.Tk()
with open('name.txt', 'r') as file:
    name = file.readline()
    loc = file.readline()
projectLoc = loc
name = name.replace('\n', '')
root.title(name + " - Bot Programmer")

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
frameMenu = tk.Frame(root, width=400, height=screen_height, bg="dark gray")
frameMenu.pack(side=tk.LEFT, fill=tk.Y)


# Create the green button with white text, adjust font size, padding, and remove onclick effect and border
btnStart = tk.Button(root, text="Start", bg="green", fg="white", command=start, font=("Helvetica", 30),
                   relief=tk.FLAT, bd=0, width=6, activebackground="dark green", activeforeground="white")  # Set width to 100 pixels
# Create the green button with white text, adjust font size, padding, and remove onclick effect and border
btnBlocks = tk.Button(frameMenu, text="Blocks", bg="#555555", fg="white", command=blocks, font=("Helvetica", 15),
                   width=13, bd=1, relief="solid", highlightthickness=0, activebackground="#555555", activeforeground="white")  # Set width to 100 pixels
# Create the green button with white text, adjust font size, padding, and remove onclick effect and border
btnMacro = tk.Button(frameMenu, text="Macro", bg="#777777", fg="white", command=macro, font=("Helvetica", 15),
                   width=13, bd=1, relief="solid", highlightthickness=0, activebackground="#777777", activeforeground="white")  # Set width to 100 pixels
lblCode = tk.Label(root, text="Code:", font=("Heltevica", 30))
tbCode = tk.Text(root, width=155, height=55)
tbCode.bind("<<Modified>>", save_code)

# Set padding for the button (10 px from top and right)
btnStart.pack(pady=20, padx=20, anchor="ne")
btnBlocks.pack(side=tk.LEFT, fill=tk.X, anchor="n")
btnMacro.pack(side=tk.LEFT, fill=tk.X, anchor="n")
lblCode.pack(side=tk.TOP)
tbCode.pack()

load_code()

# Run the Tkinter event loop
root.mainloop()
