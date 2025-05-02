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

class EntryBoxBuilder:
    # original test moved to TextBoxBuilder_test.py
    
    def __init__(self, mainframe):
        self.mainframe = mainframe
        #stringVar not currently used
        self.dateBoxValue = StringVar()
        self.chargeBoxValue = StringVar()
        self.amountBoxValue = StringVar()
        self.tagBoxValue = StringVar()
        self.noteBoxValue = StringVar()
        

    def createEntryBoxRow(self, expenses, rowNumber):
        BoxObjectList = []
        self.BoxObjectList = BoxObjectList
        dateBox = ttk.Entry(self.mainframe, width=12)
        chargeBox = ttk.Entry(self.mainframe, width=30)
        amountBox = ttk.Entry(self.mainframe, width=5)
        tagBox = ttk.Entry(self.mainframe, width=15)
        noteBox = ttk.Entry(self.mainframe, width=40)

        entryBoxArray = [dateBox, chargeBox, amountBox, tagBox, noteBox]
        # i = 0
        for r in range(rowNumber):
            rowSpacing = r+1
            # print(f"row number: {r} and rowcount var {rowNumber}")
            dateBox.grid(column=1, row=rowSpacing, sticky=N, padx=1)
            chargeBox.grid(column=2, row=rowSpacing, sticky=N, padx=1)
            amountBox.grid(column=3, row=rowSpacing, sticky=N, padx=1)
            tagBox.grid(column=4, row=rowSpacing, sticky=N, padx=1)
            noteBox.grid(column=5, row=rowSpacing, sticky=N, padx=1)
        BoxObjectList.append(dateBox)
        BoxObjectList.append(chargeBox)
        BoxObjectList.append(amountBox)
        BoxObjectList.append(tagBox)
        BoxObjectList.append(noteBox)
        self.BoxObjectList = BoxObjectList
        # print(f"dateBox is {dateBox}")
        print(f"Inside createEntryBoxRow BoxObjectList is {BoxObjectList}")
        # return BoxObjectList
        #self.populateBoxes(expenses, entryBoxArray)

    def make_boxes(self, rowcount):
        totalrows = int(rowcount.get())

        for row in range(totalrows+1):
            self.createEntryBoxRow("dummydata", row)  #this finally works. I was calling the class totally wrong


    def print_box_data(self):
        BoxObjectList = self.BoxObjectList
        print(f"Contexts of the Box var is {BoxObjectList}")
        print(f"Inside print_box_data {dir(BoxObjectList)}")
        for object in BoxObjectList:
            print(object.get())

    def populateBoxes(self, expenses, boxes):
        # This needs to be changed for entry not text boxes, currently doesn't work
        # print(self.instance_count)
        # This parses and populates each text box from the provided list
        date = expenses[0].strip("'")
        charge_name = expenses[1].strip("'").strip()
        charge_amount = expenses[2].strip("'")
        tag = expenses[3].strip("'")
        notes = expenses[4].strip("'")
        boxes[0].insert(0, "1.0", date)
        boxes[1].insert(0, "1.0", charge_name)
        boxes[2].insert(0, "1.0", charge_amount)
        boxes[3].insert(0, "1.0", tag)
        boxes[4].insert(0, "1.0", notes)

# End EntryBoxBiulder Class ================================================

# this works but isnt needed anymore
# def testcreateEntryBoxRow(mainframe, expenses, rowcount):
#     for y in range(5):
#         for x in range(rowcount):
#             my_entry = Entry(mainframe)
#             my_entry.grid(row=y, column=x, pady=10, padx=5)


def dateCheck(datestring, fuzzy=False):
    try:
        dateparse(datestring, fuzzy=fuzzy)
        return True
    except:
        return False
    
def file_import():
    importfile.set(filedialog.askopenfilename(title="Select Expenses to Import"))
    # the StringVar.get() returns the value
    # expenses = parse_imports(importfile.get())
    expenses, rowcount = handlers.readImportFile(importfile.get())
    print(f"processed expenses: {expenses}")
    print(f"processed row count: {rowcount}")
    # print(type(expenses))
    # for i in expenses:
    #     print(expenses[i])
    # print("Stopping here")
    # quit()

    update_TextBox(expenses, rowcount)
    if not importfile:
        return
    
def update_TextBox(expenses, rowcount):
    # displayExpenses = handlers.EntryBoxBuilder(mainframe)
    # displayExpenses.createEntryBoxRow(expenses, rowcount)
    BoxMaking.createEntryBoxRow(expenses, rowcount)

def leave():
    try:
        quit()
    except Exception as e:
        print(f"I have no idea how this failed but it was because of: {e}")

# Create instance of the class to build rows with
BoxMaking = EntryBoxBuilder(mainframe)

def main():

    # Moved all functions and setup outside main function.
    rowcount = ttk.Entry(mainframe, width=5)
    rowcount.grid(column=8, row=7, padx=10, pady=10)
    ttk.Button(mainframe, text="View Expense Summary", command="").grid(column=8, row=2, sticky=(E, S))
    ttk.Button(mainframe, text="View Budget Report", command="").grid(column=8, row=3, sticky=(E, S))
    ttk.Button(mainframe, text="Modify Expenses", command="").grid(column=8, row=4, sticky=(E, S))
    ttk.Button(mainframe, text="Import Expenses", command=file_import).grid(column=8, row=5, sticky=(E, S))
    ttk.Button(mainframe, text="Quit", command=leave).grid(column=8, row=6, sticky=(E, S))
    ttk.Button(mainframe, text="make rows", command=lambda: BoxMaking.make_boxes(rowcount)).grid(column=7, row=7, sticky=(E, S), padx=5, pady=10)
    ttk.Button(mainframe, text="Print Box content", command=lambda: BoxMaking.print_box_data()).grid(column=8, row=8, padx=5, pady=5)
    
    
    # TextBoxBuilder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
