# pybudget

![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54) ![Black](https://img.shields.io/badge/code%20style-black-000000.svg) ![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=flat&logo=sqlite&logoColor=white)

My attempt at creating my own budgeting software in python

## Overview

This is my attempt at expanding my knowledge of python and other components in order to create a tool for budget and expense  
reporting for myself.  And because I found available tools to be frustrating and using google sheets is boring

## Goals

I expect the end state to be able to:

- Import transactions from common file formats (CSV for now)
- Compile this data into a single file/database for simplicity
- Allow custom labelling or tagging for budget and expense categories
- User friendly interface for validating and correcting import issues
- Provide a nice UI for viewing transactions, reports, summaries and charts
- Application can be run on a local system for privacy and security with a small footprint
- Allow for manual goal and target setting for budgets and savings
- Long term data tracking and analytics for spending trends and other data points

Future roadmap:

- Secure login capabilities for data protection
- Extend support for other file formats such as PDF and exports from other financial institutions (Basic PDF support added)
- ~A possible desktop client alternative with GUI (WIP)~ Desktop client built using PyQt6 is well underway 6-19-2025
- ~Use a database like SQLite to store all transaction data for more robust options~ Implemented

## Current Features

- ~Functional GUI using TKinter~ Gui has been converted to PyQt6
- Able to import CSV expense files
  - and now also certain PDFs
- Dynamically update GUI with imported data
- Able to import transactions from capital one pdf files as pandas dataFrames
- PDF parsing converted to a class for better page and document handling

## TODO List

Tracking for what I need to change, fix or implement

- Major next step is I need to finish converting the imported PDF into usable CSV and switch the 'import expenses' to use multiple
  file formats and parse which ones should be used.  aka selecting back type along with file to call correct importers/parsers
- Update the SQL functions to support the TKinter version
- In addition to updating SQL functions I need to rework the database again after splitting the systems. ~ I plan to use the same
  format but need to decouple it from Django components~ Database has been reworked again, full decouple from Django as well.
  - I do not feel its a good idea to use the same DB but plan to add a feature later to import/export data between the two app versions
- Create library for parsing pdf import files for transactions
  - ~Create Capital One functions~ Completed 5/16/2025
  - ~Create template and tools for adding Pdf parse functions~ Completed 5/16/2025
- Create library for parsing imported dataframes into database entries
- ~Import test data~
- ~Correct formatting of import data <sup>The date format is causing issues</sup>~ Resolved 5-7-2025
- ~Create budget summary page template~
- Update links, filters and buttons for summary browsing <sup>Django development moved to [Budget Book Web Repository](https://github.com/Gergzilla/budgetbook-web)</sup>
- Create a page to edit the budget data to add tags and make corrections <sup>Django development moved to [Budget Book Web Repository](https://github.com/Gergzilla/budgetbook-web)</sup>
- Add ability to upload CSV/TSV files for easier import <sup>CSV file import added 5-7-2025</sup>
  - CSV import needs to be updated for better parsing of pandas dataframes from pdf imports
- ~Setup tagging in a more friendly way, inline editing of a table perhaps~ Completed for now via tkinter display
- Add a reliable storage method for tags to be used to to correlate common names with a tag to 'learn' how things get tagged

## Rlease Notes

- Moving future commits to dev branch for better sanity checks and logic control - 5/15/2025
  - Branch mismatch caused most recent commits to master, more clenaup is needed of original code before separating the branches again (6-19-2025)
- Split development of Django to new repository: [Budget Book Web Repository](https://github.com/Gergzilla/budgetbook-web) - 5-16-2025

## Bugs or Issues

- ~Despite the table having a date field the SQL query object doesnt have it so no date is displayed~ Resolved 4-17-2025
- ~App crashes if you cancel the import file dialogue box without selecting a file~ Resolved 5-8-2025
- ~The dynamic entry boxes do not always properly reset when importing different data or changing sources~ Not an issue in PyQt6 6-19-2025
- There is a weird crash caused by running the program with -h for the logging config.  temp fix applied in main.py
