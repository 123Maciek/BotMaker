import tkinter as tk
from tkinter import messagebox

class SubMenu:
    def __init__(self, parent, buttons, text):
        self.parent = parent
        self.buttons = buttons
        self.text = text
        self.btn = tk.Label(self.parent, text=f"{self.text} \u25B6", borderwidth=1, font = ("Helvetica", 15), relief=tk.SOLID, padx=20, pady=5)
        self.btn.pack(pady=50)

        self.submenu = tk.Menu(root, tearoff=0)
        for btn in buttons:
            self.submenu.add_command(label=btn, command=lambda b=btn: self.add_to_entry(b), font=("Helvetica", 15))
        
        self.btn.bind("<Enter>", self.show_submenu)
        self.btn.bind("<Leave>", self.hide_submenu)


    def show_submenu(self, event):
        button_pos_x = self.btn.winfo_rootx()
        button_pos_y = self.btn.winfo_rooty()
        
        self.submenu.post(button_pos_x + self.btn.winfo_width(), button_pos_y)

    def hide_submenu(self, event):
        self.submenu.unpost()

    def add_to_entry(self, button):
        print(f"Clicked {button}")


root = tk.Tk()
root.geometry("300x200")

smKeyboard = SubMenu(root, ["Option1", "Option2", "Option3"], "Keyboard")

root.mainloop()
