#!/usr/bin/python
import utilities.handlers as handlers
import utilities.db_handlers as db_handlers
import os
import vars.settings as settings

mydb = settings.mydb

main_menu = {
    "1": "View current expense summary",
    "2": "Modify category tags",
    "3": "Import new expense",
    "4": "Setup budget table",
    "0": "Exit"
}

def fileImport():
    inputfile = os.path.join("statements", "sample_data.csv") #full path doesnt work because you need absolute path, use os.path.dirname(__file__)
    handlers.csvImporter(inputfile)
    
def viewAllRecords():
    fullSummary = db_handlers.showYearlyTable()
    print(fullSummary)

def main():
    mainMenu()

def parseUserChoice(menuContext, user_choice):
    # Currently only handles main menu, might be necessary to make new library for menu navigation
    if menuContext == "mainMenu" and user_choice == 1:
        viewAllRecords()
        #print("View expense summary-NYI")
    if menuContext == "mainMenu" and user_choice == 2:
        print("Modify category tags-NYI")
        db_handlers.writeToExpenses()
    if menuContext == "mainMenu" and user_choice == 3:
        fileImport()
    if menuContext == "mainMenu" and user_choice == 4:
        db_handlers.createBudgetTable()
    if menuContext == "mainMenu" and user_choice == 0:
        print("Exiting...")
        exit()


def mainMenu():
    user_selection = 99
    os.system('cls' if os.name == 'nt' else 'clear')
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
    #mypath = os.path.abspath(__file__)
    #print(mypath)
    #mydir = os.path.dirname(__file__)
    #print(mydir)
    #exit()
    main()