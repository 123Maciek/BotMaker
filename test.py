import tkinter as tk

def create_label(root, text):
    # Create a Frame to hold the labels
    frame = tk.Frame(root)
    frame.pack(pady=20)

    # Create a Label for the main text (normal color)
    label_text = tk.Label(frame, text=f"{text} <span style='color: green;'>+</span>", font=("Arial", 12))
    label_text.pack(side=tk.LEFT)


# Create the main tkinter window
root = tk.Tk()
root.title("Text with Green Plus")

# Example text
example_text = "Sample Text"

# Create the label dynamically
create_label(root, example_text)

root.mainloop()

