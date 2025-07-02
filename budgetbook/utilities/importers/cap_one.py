#!/usr/bin/python
import csv
import datetime
from dateutil.parser import parse as dateparse
import logging


# copy pasted from handler, no changes made yet
def dateCheck(datestring, fuzzy=False):
    try:
        dateparse(datestring, fuzzy=fuzzy)
        return True
    except:
        return False


def csvImporter(inputFileName, year="2025"):
    # Works perfectly!  results in a joined list of formatted data
    joinedCsv = []
    # For now we hardcode tab delim, need to do better handling later
    with open(inputFileName, newline="") as infile:
        infilereader = csv.reader(
            filter(lambda line: line.strip(), infile), delimiter=","
        )
        for row in infilereader:
            parsedRow, rowCount = parseCSV(row, year)
            for i in parsedRow:
                joinedCsv.append(i)
    infile.close()
    return joinedCsv, rowCount


####### Parsers and Writers ########


def parseCSV(row, year):  # Works perfect!
    # New function to parse the csv one row at a time and reformat the data into a list of strings
    expenses = []
    i = 0
    date, charge_name, expense, tag, notes = "", "", "", "", ""
    while i < len(row):
        if row[i] != "":
            if dateCheck(row[i], fuzzy=False) is True:
                date = "'{}'".format(row[i])
                date = year + " " + str(date).strip("'")
                date = "'{}'".format(str(datetime.strptime(date, "%Y %b %d").date()))
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
