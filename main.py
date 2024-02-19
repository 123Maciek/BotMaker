import tkinter as tk

def start():
    print("Start button clicked!")

def blocks():
    isBlocksFrame = True
    btnBlocks.config(bg="#555555", activebackground="#555555", activeforeground="white")
    btnMacro.config(bg="#777777", activebackground="#777777", activeforeground="white")

def macro():
    isBlocksFrame = False
    btnMacro.config(bg="#555555", activebackground="#555555", activeforeground="white")
    btnBlocks.config(bg="#777777", activebackground="#777777", activeforeground="white")
isBlocksFrame = True

# Create the main window
root = tk.Tk()

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

# Set padding for the button (10 px from top and right)
btnStart.pack(pady=20, padx=20, anchor="ne")
btnBlocks.pack(side=tk.LEFT, fill=tk.X, anchor="n")
btnMacro.pack(side=tk.LEFT, fill=tk.X, anchor="n")

# Run the Tkinter event loop
root.mainloop()
