#!/usr/bin/python

import utilities.handlers as handlers
import utilities.db_handlers as db_handlers
import os

from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from dateutil.parser import parse as dateparse
from datetime import datetime
import tksheet
try:
    # Required as if -h is passed the program should exit cleanly
    from utilities.logger import LoggingHandler
except Exception:
    quit()

logger = LoggingHandler(str(os.path.basename(__file__))).log

root = Tk()
root.title("Welcome to MyPyBudget")
root.geometry("1024x800")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.configure(background="DarkGray")

nb = ttk.Notebook(root, padding="8 8 12 12")
mainframe = ttk.Frame(nb)
mainframe.grid(column=0, columnspan=9, row=0, rowspan=9, sticky=(N, W, E, S))

nb.add(mainframe, text="Main")
nb.pack()

importFilePrompt = StringVar()

def importFile(): #This works now, don't change it
    importFilePrompt.set(filedialog.askopenfilename(title="Select Expenses to Import"))
    importFile = importFilePrompt.get()
    if importFile == "":
        return
    else:
        expenses, rowcount = handlers.csvImporter(importFile)
        # Passes processed row count and expense list to update textboxes
        BoxMaking.updateTextBox(expenses, rowcount)
    
def saveExpenses():
    expenses = BoxMaking.getBoxContents()
    handlers.writeExpenseToDB(expenses)

def printBoxContents():
    try:
        print(BoxMaking.getBoxContents())
        # BoxMaking.print_box_data()
    except AttributeError:
        messagebox.showwarning(message="Error: No data has been loaded yet")
        # print("Error: No data has been loaded yet")

def deleteDupes():
    db_handlers.removeDuplicates()

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
    ttk.Button(mainframe, text="Print Expenses", command=printBoxContents).grid(column=8, row=4, sticky=(E, S))
    ttk.Button(mainframe, text="Import Expenses", command=importFile).grid(column=7, row=5, sticky=(E, S))
    ttk.Button(mainframe, text="Save Expenses", command=saveExpenses).grid(column=8, row=5, sticky=(E, S))
    ttk.Button(mainframe, text="Quit", command=leave).grid(column=8, row=6, sticky=(E, S))
    # These were just for troubleshooting
    # rowcount = ttk.Entry(mainframe, width=5)
    # rowcount.grid(column=8, row=7, padx=10, pady=10)
    ttk.Button(mainframe, text="delete duplicates", command=deleteDupes).grid(column=7, row=7, sticky=(E, S), padx=5, pady=10)
    # ttk.Button(mainframe, text="Print Box content", command=lambda: BoxMaking.print_box_data()).grid(column=8, row=8, padx=5, pady=5)
  
    # TextBoxBuilder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
