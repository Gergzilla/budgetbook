#!/usr/bin/python
# This file is a copy of handlers.py but is being modified for django integration and testing
import os
import csv
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from dateutil.parser import parse as dateparse
from datetime import datetime
from collections import defaultdict


try: 
    import utilities.db_handlers as db_handlers
except:
    import db_handlers as db_handlers
import vars.settings as settings

month_selector = settings.month_selector

#the old TextBoxBuilder has been replaced with entry box handling because that is better.  The original POC is in its own file
class EntryBoxBuilder:
    # original test moved to TextBoxBuilder_test.py

    def __init__(self, mainframe):
        self.mainframe = mainframe
        self.dateBoxValue = StringVar()
        self.chargeBoxValue = StringVar()
        self.amountBoxValue = StringVar()
        self.tagBoxValue = StringVar()
        self.noteBoxValue = StringVar()
        # TextBoxBuilder.instance_count += 1

    def createEntryBoxRow(self, expenses, rowcount):
        for y in range(5):
            for x in range(rowcount):
                my_entry = Entry(self.mainframe)
                my_entry.grid(row=y, column=x, pady=10, padx=5)


        # dateBox = ttk.Entry(self.mainframe, width=12)
        # chargeBox = ttk.Entry(self.mainframe, width=30)
        # amountBox = ttk.Entry(self.mainframe, width=5)
        # tagBox = ttk.Entry(self.mainframe, width=15)
        # noteBox = ttk.Entry(self.mainframe, width=40)
        # dateBox = ttk.Entry(self.mainframe, width=12, textvariable=self.dateBoxValue)
        # chargeBox = ttk.Entry(self.mainframe, width=30, textvariable=self.chargeBoxValue)
        # amountBox = ttk.Entry(self.mainframe, width=5, textvariable=self.amountBoxValue)
        # tagBox = ttk.Entry(self.mainframe, width=15, textvariable=self.tagBoxValue)
        # noteBox = ttk.Entry(self.mainframe, width=40, textvariable=self.noteBoxValue)

        # entryBoxArray = [dateBox, chargeBox, amountBox, tagBox, noteBox]
        # i = 0
        # for r in range(rowcount):
        #     rowSpace = r +1
        #     dateBox = ttk.Entry(self.mainframe, width=12, textvariable=self.dateBoxValue)
        #     chargeBox = ttk.Entry(self.mainframe, width=30, textvariable=self.chargeBoxValue)
        #     amountBox = ttk.Entry(self.mainframe, width=5, textvariable=self.amountBoxValue)
        #     tagBox = ttk.Entry(self.mainframe, width=15, textvariable=self.tagBoxValue)
        #     noteBox = ttk.Entry(self.mainframe, width=40, textvariable=self.noteBoxValue)
        #     dateBox.grid(column=1, row=rowSpace, sticky=N, padx=1)
        #     chargeBox.grid(column=2, row=rowSpace, sticky=N, padx=1)
        #     amountBox.grid(column=3, row=rowSpace, sticky=N, padx=1)
        #     tagBox.grid(column=4, row=rowSpace, sticky=N, padx=1)
        #     noteBox.grid(column=5, row=rowSpace, sticky=N, padx=1)
            # self.dateBoxValue.set("a")
            # self.chargeBoxValue.set("b")
            # self.amountBoxValue.set("c")
            # self.tagBoxValue.set("")
            # self.noteBoxValue.set("e")
            # for entry in entryBoxArray:
                # print(entryBoxArray[i])
                # entryBoxArray[i].grid(column=i+1, row=entry, sticky=N, padx=1)
                # entry.grid(column=i, row=r, sticky=N, padx=1)

                # i += 1

        # for r in range(rowcount): #still only makes one damn row?
            # print(f"row count is: {r}")
            # dateBox.grid(column=1, row=rowSpace, sticky=N, padx=1)
            # chargeBox.grid(column=2, row=rowSpace, sticky=N, padx=1)
            # amountBox.grid(column=3, row=rowSpace, sticky=N, padx=1)
            # tagBox.grid(column=4, row=rowSpace, sticky=N, padx=1)
            # noteBox.grid(column=5, row=rowSpace, sticky=N, padx=1)

        # i = 0  this used to use the instance_count number to generate rows, however moving it to the utilities file seemed to break it because it was no longer
        # aware of how often it was initialized  working on a way to pass row count of the source data to use.
        # while 0 <= i < len(entryBoxArray):
        #     entryBoxArray[i].grid(column=i+1, row=instance_count, sticky=N, padx=1)
        #     i += 1

        # self.populateBoxes(expenses, entryBoxArray)
    
    def populateBoxes(self, expenses, boxes):
        # This needs to be changed for entry not text boxes, currently doesn't work
        # print(self.instance_count)
        # This parses and populates each text box from the provided list
        date = expenses[0].strip("'")
        charge_name = expenses[1].strip("'").strip()
        charge_amount = expenses[2].strip("'")
        tag = expenses[3].strip("'")
        notes = expenses[4].strip("'")
        boxes[0].insert("1.0", date)
        boxes[1].insert("1.0", charge_name)
        boxes[2].insert("1.0", charge_amount)
        boxes[3].insert("1.0", tag)
        boxes[4].insert("1.0", notes)

# mydb = settings.mydb - shouldnt be needed same as sqlite import

####### Misc utilities  #######
def dateCheck(datestring, fuzzy=False):
    try:
        dateparse(datestring, fuzzy=fuzzy)
        return True
    except:
        return False

####### File hanlding ########
# def createOutputFile(FileName):  #this function isnt needed, output is sqlite DB
#     outputFile = os.path.join("database", FileName)
#     return outputFile

# def writeoutputfile(rawimport): #deprecated, use writeExpenseToDB() for output
#     outFile = createOutputFile("output.csv")
#     with open(outFile, "a+") as outputFile:
#         processedstring = parseTabbedInputs(rawimport)
#         print(processedstring, file=outputFile)

####### Parsers and Writers ########

def csvImporter(inputFileName, year="2025"):
    # Works perfectly!  results in a joined list of formatted data
    joinedCsv = []
    # For now we hardcode tab delim, need to do better handling later
    with open(inputFileName, newline="") as infile:
        infilereader = csv.reader(filter(lambda line: line.strip(), infile), delimiter=",")        
        for row in infilereader:
            parsedRow, rowCount = parseCSV(row, year)
            for i in parsedRow:
                joinedCsv.append(i)
        # print(f"the Joined CSV is: {joinedCsv}")
        # print(f"Parsed rows: {rowCount}")
                # parseTabToSQL(line)
    infile.close()
    return joinedCsv, rowCount

def parseCSV(row, year):  # Works perfect!
    # New function to parse the csv one row at a time and reformat the data into a list of strings
    expenses = []
    i = 0
    date, charge_name, expense, tag, notes = "","","","",""
    while i < len(row):
        if row[i] != "":
            if dateCheck(row[i], fuzzy=False) is True:
                date = "'{}'".format(row[i])
                date = year + " " + str(date).strip("'")
                date = "'{}'".format(str(datetime.strptime(date,"%Y %b %d").date()))
                expenses.append(date)
            elif "$" in row[i]:
                expense = row[i].replace("$", "").strip("\n")
                expenses.append(expense)
                # adds empty list elements to the end as placeholders
                expenses.append(tag)
                expenses.append(notes)
            else:
                charge_name = "'{}'".format(row[i])
                expenses.append(charge_name)
            i += 1
        else:
            i += 1
    return expenses, i
    # print(f"Espenses prior to return: {expenses}")   

def readImportFile(importfile, year="2025"): #This works now, don't change it
    #This still works but bypassing for testing, redirecting to csvImporter
    # This is functionally replaced by the csvImporter/parseCSV functions, leaving for now as
    # csvImporter(importfile)
    # quit()
    #stopped here for testing
    expenseDict = defaultdict(list)
    expenses = []
    k=0
    with open(importfile, "r", encoding="utf-8") as raw:
        for line in raw:
            if line == "\n":
                pass
            else:                
                # print(f"Raw line is: {line}")
                expenses, i=parseImportData(line, year)
                # print(f"Expenses in readImportFile is: {expenses}")
                for item in expenses:
                    expenseDict[k].append(item)
                k += 1
                # print(f"ExpensDict in readImportFile is: {expenseDict}")
    # do I really need a dictList here?
    return expenseDict, i
    # return expenses, i

def parseImportData(line, year): #This works now, don't change it
    # This is functionally replaced by the csvImporter/parseCSV functions, leaving for now as
    imports = []
    expenses = []
    i = 0
    date, charge_name, expense, tag, notes = "","","","",""
    imports = line.split("  ")
    while i < len(imports):
        if imports[i] != "":
            if dateCheck(imports[i], fuzzy=False) is True:
                date = "'{}'".format(imports[i])
                date = year + " " + str(date).strip("'")
                date = "'{}'".format(str(datetime.strptime(date,"%Y %b %d").date()))
                expenses.append(date)
            elif "$" in imports[i]:
                expense = imports[i].replace("$", "").strip("\n")
                expenses.append(expense)
                # adds empty list elements to the end as placeholders
                expenses.append(tag)
                expenses.append(notes)
            else:
                charge_name = "'{}'".format(imports[i])
                expenses.append(charge_name)
            i += 1
        else:
            i += 1
    print(f"Espenses prior to return: {expenses}")   
    return expenses, i


def parseTabToSQL(rawimport, year="2025"):
    # parse input data to sql data and call writeToDB
    i = 0
    date, charge_name, expense = "","",""
    csvline = rawimport.split("  ")
    while i < len(csvline):
        if csvline[i] != "":
            if dateCheck(csvline[i], fuzzy=False) is True:
                date = "'{}'".format(csvline[i])
                date = year + " " + str(date).strip("'")
                # Convert date to standard format for DB usage
                date = "'{}'".format(str(datetime.strptime(date,"%Y %b %d").date()))
                # print(date)
            elif "$" in csvline[i]:
                expense = csvline[i].replace("$", "")
            else:
                charge_name = "'{}'".format(csvline[i])
            i = i + 1
        else:
            i = i + 1
    #print(date + charge_name + expense)
    writeExpenseToDB(date, charge_name, expense)

def monthlyQueryBuilder(): #rewriting for error handling on bad input
    month = ""
    month = input("Enter the name of the Month to modify: ").capitalize()
    while month not in month_selector:
        month = input("That was not a valid choice.  Month must be a name or abbrev, e.g. Mar or March: ").capitalize()
        month = "" + month[0:3]
        # print(month)
    else:
        print("looks fine, calling query")
        listByMonth = db_handlers.queryByMonth(month)
    return listByMonth

# def monthlyQueryBuilder(): original, works ok
#     month = input("Enter the name of the Month to modify: ").capitalize()
#     month = "" + month[0:3]
#     if month not in month_selector:
#         print("Month must be a name or abbrev, e.g. Mar or March")
#     else:
#         print("looks fine, calling query")
#         listByMonth = db_handlers.queryByMonth(month)
#     return listByMonth

def chooseExpenseToTag():
    print("nothing here yet")

def displayPrettyExpenses(queryresult):
    os.system('cls' if os.name == 'nt' else 'clear')
    i = 1
    for date, entity, expense, tag, notes in queryresult:
        print(i, date, entity, expense, tag, notes)
        i = i +1

def writeExpenseToDB(date, charge_name, expense, tag="' '", notes="' '"):
    expensedata = date + "," + charge_name + "," + expense + "," + tag + "," + notes
    print(expensedata)
    db_handlers.addExpenses(expensedata, "2024")

if __name__ == "__main__":
    print("I'm a collection of functions.  I dont think you meant to run this directly")