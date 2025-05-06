#!/usr/bin/python

import utilities.handlers as handlers
import utilities.db_handlers as db_handlers
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from dateutil.parser import parse as dateparse
from datetime import datetime
import tksheet

# TODO: The current issue here is that I need to refactor the way that the parser handles the inputs.
# I think the problem is I am sending just a big list to the textbox class which of course it cant handle.  Though I dont
# know why it isnt creating more boxes because it should be creating multiple text boxes at least

root = Tk()
root.title("Welcome to MyPyBudget")
root.geometry("1024x800")

mainframe = ttk.Frame(root, padding="8 8 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

importfile = StringVar()

# End EntryBoxBiulder Class ================================================


def dateCheck(datestring, fuzzy=False):
    try:
        dateparse(datestring, fuzzy=fuzzy)
        return True
    except:
        return False
    
def file_import(): #This works now, don't change it
    
    importfile.set(filedialog.askopenfilename(title="Select Expenses to Import"))
    # expenses, rowcount = handlers.readImportFile(importfile.get())  # Swaping to the new CSV importer
    expenses, rowcount = handlers.csvImporter(importfile.get())
    # Passes processed row count and expense list to update textboxes
    update_TextBox(expenses, rowcount)
    if not importfile:
        return
    
def update_TextBox(expenses, rowcount):
    # Call make_boxes which parses the imported file and creates enough rows for the data
    BoxObjects = BoxMaking.make_boxes(rowcount)
    # Call populateBoxes which populates each created box with the parsed data
    BoxMaking.populateBoxes(expenses, BoxObjects)

def leave():
    try:
        quit()
    except Exception as e:
        print(f"I have no idea how this failed but it was because of: {e}")

# Create instance of the class to build rows with
BoxMaking = handlers.EntryBoxBuilder(mainframe)

def main():

    # Moved all functions and setup outside main function.

    ttk.Button(mainframe, text="View Expense Summary", command="").grid(column=8, row=2, sticky=(E, S))
    ttk.Button(mainframe, text="View Budget Report", command="").grid(column=8, row=3, sticky=(E, S))
    ttk.Button(mainframe, text="Modify Expenses", command="").grid(column=8, row=4, sticky=(E, S))
    ttk.Button(mainframe, text="Import Expenses", command=file_import).grid(column=8, row=5, sticky=(E, S))
    ttk.Button(mainframe, text="Quit", command=leave).grid(column=8, row=6, sticky=(E, S))
    # These were just for troubleshooting
    # rowcount = ttk.Entry(mainframe, width=5)
    # rowcount.grid(column=8, row=7, padx=10, pady=10)
    # ttk.Button(mainframe, text="make rows", command=lambda: BoxMaking.make_boxes(rowcount)).grid(column=7, row=7, sticky=(E, S), padx=5, pady=10)
    # ttk.Button(mainframe, text="Print Box content", command=lambda: BoxMaking.print_box_data()).grid(column=8, row=8, padx=5, pady=5)
    
    # TextBoxBuilder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
