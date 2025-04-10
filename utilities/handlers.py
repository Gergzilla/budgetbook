#!/usr/bin/python
# Collection of handler functions
import os
from dateutil.parser import parse as dateparse
import sqlite3
try: 
    import utilities.db_handlers as db_handlers
except:
    import db_handlers
import settings.settings as settings

mydb = settings.mydb
#dbconnect = db_handlers.createDB()
#cur = dbconnect.cursor()

####### Misc utilities  #######
def dateCheck(datestring, fuzzy=False):
    try:
        dateparse(datestring, fuzzy=fuzzy)
        return True
    except:
        return False

####### File hanlding ########
def createOutputFile(FileName):
    outputFile = os.path.join("database", FileName)
    return outputFile

def writeoutputfile(rawimport): #deprecated, use wrteExpenseToDB() for output
    outFile = createOutputFile("output.csv")
    with open(outFile, "a+") as outputFile:
        processedstring = parseTabbedInputs(rawimport)
        print(processedstring, file=outputFile)

####### Parsers and Writers ########
def csvImporter(inputFileName):
    with open(inputFileName,"r", encoding="utf-8") as infile:
        for line in infile:
            #writeoutputfile(line)
            #writeExpenseToDB(line, mydb)
            parseTabToSQL(line)
    infile.close()
    
def parseTabToSQL(rawimport):
    # parse input data to sql data and call writeToDB
    i = 0
    date, charge_name, expense = "","",""
    csvline = rawimport.split("  ")
    while i < len(csvline):
        if csvline[i] != "":
            if dateCheck(csvline[i], fuzzy=False) is True:
                date = "'{}'".format(csvline[i])
            elif "$" in csvline[i]:
                expense = csvline[i].replace("$", "")
            else:
                charge_name = "'{}'".format(csvline[i])
            i = i + 1
        else:
            i = i + 1
    #print(date + charge_name + expense)
    writeExpenseToDB(date, charge_name, expense)

def parseTabbedInputs(rawimport): #deprecated by parseTabToSQL() - not used
    # writting a new combination of this that keeps each item apart for db entry
    # designed to handle tab delimited, need other options later
    i = 0
    a,b,c = "","",""
    csvline = rawimport.split("  ")
    while i < len(csvline):
        if csvline[i] != "":
            if dateCheck(csvline[i], fuzzy=False) is True:
                #print(csvline[i] + " is a date")
                a = csvline[i]
            elif "$" in csvline[i]:
                #print(csvline[i].strip("\n") +" is a price")
                c = csvline[i]
            else:
                #print(csvline[i].strip("\n") + " is the charge name")
                b = csvline[i].strip()
            i = i + 1
        else:
            i = i + 1
        parsedstring = a.strip("\n") + "," + b.strip("\n") + "," + c.strip("\n")
    return parsedstring

def writeExpenseToDB(date, charge_name, expense, tag="' '", notes="' '"):
    expensedata = date + "," + charge_name + "," + expense + "," + tag + "," + notes
    db_handlers.addExpenses(expensedata, "2024")

if __name__ == "__main__":
    print("I'm a collection of functions.  I dont think you meant to run this directly")