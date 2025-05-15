# import utilities.handlers as handlers
# import utilities.db_handlers as db_handlers
# local testing to evaluate methods of using the csv reader for better parsing
import os
from dateutil import parser as dateparse
from datetime import datetime
from utilities.logger import LoggingHandler as logger
import csv

from utilities.importers.import_entries import ImportRecord
# mydb = settings.mydb not needed currently

#this function not used, just reference
def import_transactions(csv_path):
    lines = []
    with open(csv_path, encoding='latin-1') as csv_file:
        for line in csv.reader(csv_file, delimiter=';'):
            if len(line) < 5:
                continue
            try:
                lines.append(ImportRecord(
                    transaction_date=datetime.datetime.strptime(line[0], '%d.%m.%Y').date(),
                    post_date=datetime.datetime.strptime(line[1], '%d.%m.%Y').date(),
                    charge_name=line[2],
                    amount=float(line[3].replace("$",""))
                    ))
            except ValueError:
                # first line contains headers
                pass
    return lines

main_menu = {
    "1": "Import new expense",
    "0": "Exit"
}

def dateCheck(datestring, fuzzy=False):
    try:
        dateparse(datestring, fuzzy=fuzzy)
        return True
    except Exception as e:
        #e isnt used but its caught for proper coding, this merely needs to return false if it cant parse the date for any reason
        return False
    
def csvImporter(inputFileName, year="2025"):
    # Works perfectly!  results in a joined list of formatted data
    joinedCsv = []
    lines = []
    rowCount = 1
    # For now we hardcode tab delim, need to do better handling later
    try:
        with open(inputFileName, newline="") as infile:
            # infilereader = csv.reader(filter(lambda line: line.strip(), infile), delimiter=",")        
            for line in csv.reader(filter(lambda line: line.strip(), infile), delimiter=","):
                print(f"length count is {len(lines)}")
                print(f"line 0 is: {line[0]}")
                print(f"line 1 is: {line[1]}")
                print(f"line 2 is: {line[2]}")
                #the errrors here are due to needing the year in the string which isnt in the statement by default
                lines.append(ImportRecord(
                transaction_date=str(datetime.strptime(year + " " + line[0], "%Y %b %d").date()),
                post_date=str(datetime.strptime(year + " " + line[1], "%Y %b %d").date()),
                charge_name=line[2],
                amount=float(line[3].replace("$",""))
                ))
        infile.close()
        return lines, rowCount
    except FileNotFoundError:
        logger.critical("No valid file was found to inport")

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
                date = "{}".format(str(datetime.strptime(date,"%Y %b %d").date()))
                expenses.append(date)
            elif "$" in row[i]:
                expense = row[i].replace("$", "").strip("\n")
                expenses.append(expense)
                # adds empty list elements to the end as placeholders
                expenses.append(tag)
                expenses.append(notes)
            else:
                charge_name = "{}".format(row[i])
                # charge_name = "'{}'".format(row[i])
                expenses.append(charge_name)
            i += 1
        else:
            i += 1
    return expenses, i
    # print(f"Espenses prior to return: {expenses}")


def fileImport():
    importFile = os.path.join("statements", "sample_data.csv") #full path doesnt work because you need absolute path, use os.path.dirname(__file__)
    # handlers.csvImporter(inputfile)
    expenses, rowcount = csvImporter(importFile)
    for data in expenses:
        print(data.charge_name)
    # print(expenses)
        # Passes processed row count and expense list to update textboxes
    # BoxMaking.updateTextBox(expenses, rowcount)

def main():
    mainMenu()

def parseUserChoice(menuContext, user_choice):
    # Currently only handles main menu, might be necessary to make new library for menu navigation
    if menuContext == "mainMenu" and user_choice == 1:
        fileImport()
    if menuContext == "mainMenu" and user_choice == 0:
        print("Exiting...")
        exit()

def mainMenu():
    user_selection = 99
    # os.system('cls' if os.name == 'nt' else 'clear') disabled for debug for now
    print("Welcome to my budget, choose an action below")
    for key, value in main_menu.items():
        print(key, value)
    while -1 > user_selection or len(main_menu.keys()) < user_selection:
        try:
            user_selection = int(input("Choose an option from the list: "))
        except ValueError:
            print("You must enter a valid choice from above")
    parseUserChoice("mainMenu", user_selection)

if __name__ == "__main__":
    main()