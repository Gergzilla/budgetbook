#!/usr/bin/python
import os
import sqlite3

#mydb = os.path.join(os.path.dirname(__file__), "", "data", "mybudget.db")
mydb = os.path.join("D:\\","scripts","pybudget", "data", "mybudget.db")
dbconnect = sqlite3.connect(mydb)

if __name__ == "__main__":
    print("I am a settings file, why did you run me?  LOL")