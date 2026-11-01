import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
# Create and hide the main root window so only the message box shows
root = tk.Tk()
root.withdraw()
# Add an input field (Note: simpledialog is a main alternative to Entry widget)
# Alternatively, using Entry widget manually would require a new
# a standard tkinter.Tk() window.
# Create a standard input dialog to box get text from the user
input_dialog = simpledialog.askstring("Input", "Please enter your text:")
# If the user entered a text, display it in the message box
if input_dialog:
    messagebox.showinfo("Information", input_dialog)
# Close the root window
root.destroy()
