import tkinter as tk
from tkinter import font

class Block:
    def __init__(self, name, parent, number):
        self.name = name
        self.parent = parent
        self.number = number
        self.btn = tk.Button(self.parent, text=self.name, bd=1, relief="solid", highlightthickness=0, height=2, width=35, command=self.add_block, font=font.Font)
        self.btn.pack(side=tk.BOTTOM, anchor="sw", pady=(0, 950 - (self.number * 50)), padx=40)
    
    def pack(self):
        if self.btn.winfo_exists() == False:
            self.btn = tk.Button(self.parent, text=self.name, bd=1, relief="solid", highlightthickness=0, height=2, width=35, command=self.add_block, font=font.Font)
            self.btn.pack(side=tk.BOTTOM, anchor="sw", pady=(0, 500 - (self.number * 50)), padx=40)
    
    def destroy(self):
        self.btn.destroy()
    
    def add_block(self):
        global tbCode
        line_num = get_cursor_line_number()
        content = tbCode.get("1.0", tk.END)
        lines = content.splitlines()
        if lines[line_num-1] == "":
            lines[line_num-1] = self.name
        else:
            lines.insert(line_num, self.name)
        tbCode.delete("1.0", tk.END)
        tbCode.insert(tk.END, "\n".join(map(str, lines)))


def start():
    pass

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

def reload_side_frame_obj():
    if isBlocksFrame:
        #Blocks
        global codingBlocks
        global btnMacro
        global btnBlocks
        btnMacro.destroy()
        btnBlocks.destroy()
        btnBlocks = tk.Button(frameMenu, text="Blocks", bg="#555555", fg="white", command=blocks, font=("Helvetica", 15), width=18, bd=1, relief="solid", highlightthickness=0, activebackground="#555555", activeforeground="white", highlightcolor="white")
        btnMacro = tk.Button(frameMenu, text="Macro", bg="#777777", fg="white", command=macro, font=("Helvetica", 15), width=18, bd=1, relief="solid", highlightthickness=0, activebackground="#777777", activeforeground="white", highlightcolor="white")

        codingBlocks = []
        codingBlocks.append(Block('ClickOnKeyboard("key_name")', frameMenu, 0))

        btnBlocks.pack(anchor="nw", side=tk.LEFT)
        btnMacro.pack(anchor="nw", side=tk.LEFT)
        btnBlocks["state"] = "disabled"
        btnMacro["state"] = "normal"
        btnBlocks["disabledforeground"] = "white"

        #Generate
        for block in codingBlocks:
            block.pack()
    else:
        #Macros
        btnMacro["state"] = "disabled"
        btnBlocks["state"] = "normal"
        btnMacro["disabledforeground"] = "white"

        for block in codingBlocks:
            block.destroy()

isBlocksFrame = True
projectLoc = ""
codingBlocks = []

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
                   width=18, bd=1, relief="solid", highlightthickness=0, activebackground="#555555", activeforeground="white", highlightcolor="white")  # Set width to 100 pixels
# Create the green button with white text, adjust font size, padding, and remove onclick effect and border
btnMacro = tk.Button(frameMenu, text="Macro", bg="#777777", fg="white", command=macro, font=("Helvetica", 15),
                   width=18, bd=1, relief="solid", highlightthickness=0, activebackground="#777777", activeforeground="white", highlightcolor="white")  # Set width to 100 pixels
lblCode = tk.Label(root, text="Code:", font=("Heltevica", 30))
tbCode = tk.Text(root, width=155, height=55)
tbCode.bind("<<Modified>>", save_code)

# Set padding for the button (10 px from top and right)
btnStart.pack(pady=20, padx=20, anchor="ne")
btnBlocks.pack(anchor="nw", side=tk.LEFT)
btnMacro.pack(anchor="nw", side=tk.LEFT)
lblCode.pack(side=tk.TOP)
tbCode.pack()

load_code()
reload_side_frame_obj()

# Run the Tkinter event loop
root.mainloop()
