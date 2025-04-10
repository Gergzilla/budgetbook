#!/usr/bin/python

import sqlite3
import os
import vars.settings as settings

#### Database Setup Functions #####
mydb=settings.mydb
def createDB(mydb): 
    #can prompt for db name in the future, for now its hard set
    if os.path.exists(mydb):
        #print("File exists, establishing connection to " + mydb)
        dbconnect = sqlite3.connect(mydb)
    else:
        print("File doesnt exist, creating file")
        try:
            dbconnect = sqlite3.connect(mydb)
        except:
            print("could not create file for some reason at "+ mydb)
            dbconnect = ""
    return dbconnect

def createBudgetTable(year="2024"):
    # create expenses table if it doesnt exist
    dbconn = sqlite3.connect(mydb)
    writeCursor = dbconn.cursor()
    tableCheck = pollMasterTable(writeCursor, year)
    print(tableCheck)
    if tableCheck == False:
        print("Table check is False, meaning table needs to be made")
        writeCursor.executescript("CREATE TABLE expenses"+year+"(date TEXT, charge_name TEXT, expense REAL, tag TEXT, notes TEXT)")
        dbconn.commit()
        if pollMasterTable:
            print("Table created")
        else:
            print("table still not found - something broke")
    else:
        print("Table check passed, nothing to do")
        return

def pollMasterTable(cur, year):
    # checks the master table if our table exists
    createtable = "SELECT name FROM sqlite_master WHERE name='expenses{}'" .format(year)
    masterdblist = cur.execute(createtable)
    try:
        checktables = masterdblist.fetchone()
    except:
        checktables = None
    if checktables is None:
        return False
    else:
        return True
    
##### Data add/remove functions  ######

def writeToExpenses(writedata="", mydb=mydb):
    dbconn = sqlite3.connect(mydb)
    writeCursor = dbconn.cursor()
    try:
        writeCursor.execute(writedata)
        dbconn.commit()
    except Exception as e:
        print("Error executing query: ", e)
    writeCursor.close()
    
def addExpenses(expensedata, year):
    insertstring = "INSERT INTO expenses{0} VALUES ({1})" .format(year, expensedata)
    writeToExpenses(insertstring)
    
def addTag(expensdata, tag, year):
    updatestring = ""
    print("addTag")

##### read-only database functions  ########

def queryByMonth(month, year="2024", mydb=mydb):
    dbconn = sqlite3.connect(mydb)
    readCursor = dbconn.cursor()
    monthQuery = "SELECT * FROM expenses{0} WHERE date LIKE '{1}%'".format(year,month)
    try:
        readCursor.execute(monthQuery)
        monthlyExpenses = readCursor.fetchall()
    except Exception as e:
        print("Unable to execute for for reason: ", e)
        monthlyExpenses = e
    readCursor.close()
    return monthlyExpenses


def queryByYearlyTable(year="2024", mydb=mydb):
    dbconn = sqlite3.connect(mydb)
    readCursor = dbconn.cursor()
    #recordquery = "SELECT date, charge_name, expense, tag, notes FROM expenses{0}" .format(year)
    recordquery = "SELECT * FROM expenses{0}".format(year)
    # print(recordquery)
    try:
        readCursor.execute(recordquery)
        fulltable = readCursor.fetchall()
    except Exception as e:
        print("unable to execute query for reason: ", repr(e))
        fulltable = e
    readCursor.close()
    return fulltable

##### maintenance functions ######

def removeDuplicates(mydb=mydb,year="2024"): #Not currently used
    dbconn = sqlite3.connect(mydb)
    writeCursor = dbconn.cursor()
    rowquery = "SELECT MIN(rowid) FROM expenses{0} group by date, charge_name, expense".format(year)
    deletedupes = "DELETE FROM expenses{0} WHERE rowid not in({1}".format(year, rowquery)
    removalResult = writeCursor.execute(deletedupes)
    print(removalResult)

if __name__ == "__main__":

    print("I'm a collection of database functions.  I dont think you meant to run this directly")
