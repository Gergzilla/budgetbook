#!/usr/bin/python
# This file is a copy of db_handlers.py but is being modified for django integration and testing
import sqlite3
import os
import vars.dj_settings as settings

#### Database Setup Functions #####
mydb=settings.mydb
mytable=settings.mytable

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
    # this is disabled for now due to django integration
    dbconn = sqlite3.connect(mydb)
    writeCursor = dbconn.cursor()
    tableCheck = pollMasterTable(writeCursor, year)
    print(tableCheck)
    if tableCheck == False:
        print("Table check is False, meaning table needs to be made")
        print("do nothing")
        # writeCursor.executescript("CREATE TABLE database_budget(date TEXT, charge_name TEXT, expense REAL, tag TEXT, notes TEXT)")
        # dbconn.commit()
        # if pollMasterTable:
        #     print("Table created")
        # else:
        #     print("table still not found - something broke")
    else:
        print("Table check passed, nothing to do")
        return

def pollMasterTable(cur, year="2024",mytable=mytable):
    # checks the master table if our table exists
    createtable = "SELECT name FROM sqlite_master WHERE name='{0}'".format(mytable)
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
    
def addExpenses(expensedata, year="2024",mytable=mytable):
    # this is the proper format for insertion and works to auto increment ROWID
    # otherwise you can get a 'table has x columns but y supplied' unless you specificy the ROWID as well which isnt needed
    insertString = "INSERT INTO {0} (charge_date, charge_name, amount, tag_id, notes) VALUES ({1})" .format(mytable, expensedata)
    print(insertString)
    writeToExpenses(insertString)
    
def addTag(expensdata, tag, year="2024",mytable=mytable):
    # more learning, the for loop for a tuple doesnt work on a single item because there is nothing to iterate over
    # so here it is just a,b,c,y,z = tuple
    date, entity, charge, activetag, note = expensdata
    #activetag and note not needed here but allocated anyways to prevent ValueError
    tagUpdate = "UPDATE {0} SET tag='{1}' WHERE date='{2}' AND charge_name='{3}' AND amount={4}" \
        .format(mytable, tag, date, entity, charge)
    result = writeToExpenses(tagUpdate)
    return result

##### read-only database functions  ########

def queryByMonth(month,year="2024", mydb=mydb, mytable=mytable):
    dbconn = sqlite3.connect(mydb)
    readCursor = dbconn.cursor()
    monthQuery = "SELECT date, charge_name, amount, tag_id, notes FROM {0} WHERE date LIKE '{1}%'".format(mytable,month)
    try:
        readCursor.execute(monthQuery)
        monthlyExpenses = readCursor.fetchall()
    except Exception as e:
        print("Unable to execute for for reason: ", e)
        monthlyExpenses = e
    readCursor.close()
    return monthlyExpenses


def queryByYearlyTable(mytable=mytable,year="2024", mydb=mydb):
    dbconn = sqlite3.connect(mydb)
    readCursor = dbconn.cursor()
    # Specify exact columns so you always know what you are getting back and dont get 'too many values' errors
    recordquery = "SELECT date, charge_name, amount, tag_id, notes FROM {0}".format(mytable)
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

def removeDuplicates(mydb=mydb, mytable=mytable, year="2024"): #Not currently used
    dbconn = sqlite3.connect(mydb)
    writeCursor = dbconn.cursor()
    rowquery = "SELECT MIN(rowid) FROM {0} group by date, charge_name, expense".format(mytable)
    deletedupes = "DELETE FROM {0} WHERE rowid not in({1}".format(mytable, rowquery)
    removalResult = writeCursor.execute(deletedupes)
    print(removalResult)

if __name__ == "__main__":

    print("I'm a library of database functions.  I dont think you meant to run this directly")
