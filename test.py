import tkinter as tk

def bring_to_top(window):
    # Check if window is minimized
    if window.state() == "iconic":
        window.deiconify()  # Restore the window from minimized state
    window.lift()  # Bring the window to the top

def delayed_bring_to_top(window):
    window.after(3000, lambda: bring_to_top(window))  # Wait 3000 milliseconds (3 seconds) before bringing to top

root = tk.Tk()
root.title("Bring to Top Example")

button = tk.Button(root, text="Bring to Top after 3 seconds", command=lambda: delayed_bring_to_top(root))
button.pack(pady=20)

root.mainloop()
