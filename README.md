# pybudget

My attempt at creating my own budgeting software in python

## Overview

This is my attempt at expanding my knowledge of python and other components in order to create a tool for budget and expense reporting for myself.  And because I found available tools to be frustrating and using google sheets is boring

## Goals

I expect the end state to be able to:

- Import transactions from common file formats (CSV for now)
- Compile this data into a single file for simplicity
- Allow custom labelling or tagging for budget and expense categories
- User friendly interface for validating and correcting import issues
- Provide a nice UI for viewing transactions, reports, summaries and charts
- System can be run on a private hosted web system with minimal footprint

Future roadmap:

- secure login capabilities for data protection
- extend support for other file formats such as PDF
- A possible desktop client alternative with GUI
- ~Use a database like SQLite to store all transaction data for more robust options~ Implemented

## Current Features

- Functional GUI using TKinter
- Able to import CSV expense files
- Dynamically update GUI with imported data

## TODO List

Tracking for what I need to change, fix or implement

- ~Setup base landing page templates~
- Improve UI layout and widget alignment
- Setup multiple UI pages for different actions ie, importing, editing, reports, charts, etc
- Update the SQL functions to support the TKinter version
- ~Modify original POC scripts to interact with Django's SQLite DB~
- ~Import test data~
- ~Correct formatting of import data <sup>The date format is causing issues</sup>~ Resolved 5-7-2025
- ~Create budget summary page template~
- Update links, filters and buttons for summary browsing <sup> on hold until Django development resumes</sup>
- Create a page to edit the budget data to add tags and make corrections <sup> on hold until Django development resumes</sup>
- Add ability to upload CSV/TSV files for easier import <sup>CSV file import added 5-7-2025</sup>
- Setup tagging in a more friendly way, inline editing of a table perhaps
- Add a reliable storage method for tags to be used to to correlate common names with a tag to 'learn' how things get tagged

## Bugs or Issues

- ~Despite the table having a date field the SQL query object doesnt have it so no date is displayed~ Resolved 4-17-2025
- App crashes if you cancel the import file dialogue box without selecting a file
- The dynamic entry boxes do not always properly reset when importing different data or changing sources
