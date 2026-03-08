#!/usr/bin/python
"""my doc is my string, verify me"""

import os
from datetime import datetime
import csv
import sys
import pymupdf
import numpy as np
import pandas as pd
import dateutil.parser as dateparser

# from dateutil.parser import parse as dateparse

# this stuff below is only really needed for testing, not for prod
from utilities.logger import (
    LoggingHandler,
)  # temporary local utilities until packaging later


# import matplotlib.pyplot as plt

# Class is fully functional as is joining all discovered tables for the following institutions:
# Capital One, Other
# Future institutions will be added as I need them but the core functions should be universal in
# general.  A helper file has also been created to guide future importer creation.
# Helper File: import_template_tool.py
logger = LoggingHandler(str(os.path.basename(__file__))).log


class Page:
    """Page is a custom class for the pymupdf Page object along with needed attributes for parsing
    and processing imported pdfs.  It parses out the input pdf into numbbered pages for tracking
    which are then used by a set of functions to look for transaction tables for import.  Each
    financial institution requires its own import function due to the unique formatting of their
    monthly statements."""

    def __init__(self, page: pymupdf.Page, page_number):
        self.name = __name__
        self.page = page
        self.page_number = page_number
        self.logger = LoggingHandler(__class__).log
        self.clip_y1 = 0
        self.parsed_dataframe = pd.DataFrame()
        # moved this for lint, havent tested

    def find_transaction_table(self, needle):
        """scans the pdf within the page object using the 'needle' which is the name for a string
        of text unique to the start of the transaction table.  This is sourced ia the unique
        function for a given institution.  More details can be found on the pymupdf documentation
        here https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.search"""
        end_of_table = self.get_rect(needle)  # for capitalOne only
        if end_of_table:
            self.logger.debug(f"Calculated rect of needle: {end_of_table}")
            return True
        return False

    def find_table_end(self, needle):
        """This works basically the same as the find_transaction_table function except that the
        needle is a unique string for the end of a given transaction table.  Also unique to the
        institution specific function."""
        # print(f"Page: {self.page.number} into the find_table_end function?")
        end_of_table = self.get_rect(needle)
        if end_of_table:
            self.clip_y1 = round(end_of_table[0].y1, 0) - 5
            # this sets the rectable up a few units to avoid including the end of table keyword
            # in the rectangle
            return self.clip_y1
        self.logger.debug(f"Table end not found on page {self.page.number}")
        return self.clip_y1

    def get_rect(self, needle):
        """This function returns the rect or rectangle of an area where the needle was found.
        These are basically coordinates of the table we want on the given page of a pdf we are
        parsing.  More info here https://pymupdf.readthedocs.io/en/latest/rect.html#rect
        """
        found_rect = self.page.search_for(needle)
        return found_rect

    def parse_transaction_table(self, new_clip):
        """This function is the real work horse of the imports.  It loops through each page to
        record each one that has a transaction table.  Then it parses through all of them and
        converts them to pandas dataframes.  Then unifies their columns, drops empty entries
        and merges them all into one single dataframe for the next processing step."""
        tabs = self.page.find_tables(
            clip=new_clip, strategy="text", join_x_tolerance=3, text_x_tolerance=5
        )
        # print(f"Page: {self.page.number} into the parse_transaction_table function?")
        if tabs.tables:
            # print(f"Page: {self.page.number} if tabs.tables in function?")
            df = tabs[0].to_pandas()

            # there is an error handling issue here, if the function incorrectly identifies a table
            # it can have the wrong number of columns which causes the next part to fail/hang
            # TODO I need to make column relabelling dynamic later

            # converting the column length handler to a match case
            column_count = len(df.columns)

            match column_count:
                # In testing there are cases where valid data returns with 4 or 5 columns
                # The purpose here is to rename the columns in those cases and in any other case
                # purge the dataframe as it is unlikely to have correct information and it could
                # cause merge errors later
                case 4:
                    # 4 columns means all data was found properly and ready for next steps.
                    df.columns = ["Col1", "Col2", "Col3", "Col4"]
                case 5:
                    # 5 columns means the transaction date is probably split between col 2 and 3
                    df.columns = ["Col1", "Col2", "Col3", "Col4", "Col5"]
                case _:
                    # If the column count is not 4 or 5, replace the dataframe 5 empty columns
                    df = pd.DataFrame(columns=["Col1", "Col2", "Col3", "Col4", "Col5"])

            # replaces empty or null rows with nan and drops all nan/null rows
            df = df.replace("", np.nan)
            df = df.dropna()

            # print(f"Page: {self.page.number} end of parse_transaction_table function?")
            print(f"All cleanup is done and the final dataframe is \n: {df}")
            return df
        df = ""
        # print("why am I always returning empty dataframes?")
        return df

    def import_cap_one_pdf(self):
        """This is the Capital One specific function for PDF processing that has the unique strings
        for finding the start and end of the transaction tables as well as the default clip size
        of the rect on the page that could contain the transaction details."""
        # note for myself I feel this would better serve logical and functional separation by not
        # having the institution specific functions inside the page class but I currently lack the
        # know-how to do this effectively.  Ideally there will be a module for each institution
        # to make it easier to maintain and having all universal functions consolidated here for
        # example.
        table_title = "Trans Date"
        end_of_trans_needle = "Total Transactions for This Period"
        # self.parsed_dataframe = pd.DataFrame()
        default_clip = (30, 100, 600, 740)
        alt_clip = (30, 85, 600, 740)
        if not alt_clip:
            alt_clip = default_clip
        if self.find_transaction_table(table_title):
            # print(f"Page: {self.page.number} into the find transaction loop?")
            self.logger.debug(
                f"Page {self.page.number} appears to have a transaction table"
            )
            new_clip_y1 = self.find_table_end(end_of_trans_needle)
            if new_clip_y1 == 0:
                self.parsed_dataframe = self.parse_transaction_table(default_clip)
            else:
                clip_list = list(alt_clip)
                clip_list[3] = new_clip_y1
                alt_clip = tuple(clip_list)
                self.logger.debug(f"parsed alt_clip is {alt_clip}")
                self.parsed_dataframe = self.parse_transaction_table(alt_clip)
            return self.parsed_dataframe
        # df = pd.DataFrame()
        # print(f"Page: {self.page.number} into the else for empty table?")
        return self.parsed_dataframe

    # Add more bank specific functions here

    def __str__(self):
        return self.name


######## Begin import handler functions ########


class FileImportHandlers(object):
    """This class is a collection of static methods for various import functions as well as the
    import formatters for the specific types of imports, such as csv or specific financial
    institutions.  The generic handlers go first and the custom ones at the end for readability.
    """

    # these functions moved from handlers to consolidate all file import components to one module
    def __init__(self):
        self.name = __name__
        self.logger = LoggingHandler(__class__).log

    def __str__(self):
        return self.name

    @staticmethod
    def format_import_dataframe(import_frame: pd.DataFrame, import_year):
        """This formatter is basically designed to handle looping through all rows in the incoming
        dataframe to fix the formatting of it, mainly the dates, to a unified format for import
        into the database.  Although all it currently does is call date formatting it is still
        a generic 'loop through the rows' function and thus serves its purpose."""
        index_num = 0
        row_count = len(import_frame)
        print(f"Processing {row_count} rows.")
        # fix the date format
        while 0 <= index_num < row_count:
            # print(row_count)
            formated_transaction_date = FileImportHandlers.format_date(
                import_frame.iloc[index_num, 0], import_year
            )
            formated_post_date = FileImportHandlers.format_date(
                import_frame.iloc[index_num, 1], import_year
            )

            try:
                import_frame.iloc[index_num, 0] = formated_transaction_date
                import_frame.iloc[index_num, 1] = formated_post_date
            except IndexError as e:
                print(e)
            index_num += 1
        return import_frame

    @staticmethod
    def date_check(datestring, fuzzy=False):
        """This is used to validate dates.  This serves two main purposes.  The first is to check
        that data contained within a given row actually has a date where one is expected when
        parsing an import file.  This is also used to check what kind of data or pdf may have beenedswwww[']xdsssssssz20p4o
        imported.  As which rows have valid dates in them can determine the format style of the
        given data and allow for corrections."""
        # print(f"datestring in date_check() method: {datestring}")
        try:
            dateparser.parse(datestring, fuzzy=fuzzy)
            return True
        except dateparser.ParserError as e:
            logger.debug(f"date_check Parse Error: {e}")
            # e isnt technically used but caught for proper handling, this just needs to evaluate
            # as false if datestring is not a date
            return False

    @staticmethod
    def format_date(datestring, year):
        """This function is designed to convert a given date to a specific format to unify all
        imported data to the same style for useful data handling.  It is not currently as
        robust as it likely will need to be going forward but currently works for dates in
        the 'MM DD' format and updates them to 'YYYY-MM-DD' format based on the import year chosen.
        """
        formated_date = f"'{datestring}'"
        # print(f"1: formated_date in format_date: {formated_date}")
        formated_date = year + " " + str(formated_date).strip("'")
        # print(f"2: formated_date in format_date: {formated_date}")
        date_to_string = str(datetime.strptime(formated_date, "%Y %b %d").date())
        # print(f"Did this break? {date_to_string}")
        formated_date = f"{date_to_string}"
        # print(f"3: formated_date in format_date: {formated_date}")
        return formated_date

    @staticmethod
    def importer_csv(input_file_name, year: int = 2025):
        """This is the actual import function for CSV files, it opens a provided csv, runs each
        row into through the parse_csv function and combines all the results into a pandas
        dataframe designed to be imported later.  As noted in the parse function this does not
        actually make it to the database currently due to lack of implementation for the needed
        functions but should be easy to implement now that the rest of the db handlers work well.
        """
        # Works perfectly!  results in a joined list of formatted data and converted to dataframe
        joined_csv = []
        try:
            with open(input_file_name, newline="", encoding="utf-8") as infile:
                infilereader = csv.reader(
                    filter(lambda line: line.strip(), infile), delimiter=","
                )
                for row in infilereader:
                    parsed_row = FileImportHandlers.parse_csv(row, year)
                    joined_csv.append(parsed_row)
            infile.close()
            joined_df = pd.DataFrame(
                joined_csv,
                columns=[
                    "transaction_date",
                    "post_date",
                    "transaction_name",
                    "transaction_amount",
                    "tags",
                    "notes",
                ],
            )
            return joined_df
        except FileNotFoundError:
            logger.critical("No valid file was found to import")
            return None

    @staticmethod
    def parse_csv(row, year):  # Works perfect!
        # note that this function  does work but the import of csv currently doesnt support
        # the pandas formatting needed to complete the import 3-2-2026
        """This parses raw CSV for import and is called from the import_csv static method.
        Currently it assumes a certain formatting, mainly for efirst bank or amazon.  However it
        is no longer fully implemented since the move to the new database format and structure.
        The parsing all still works but it does not call the next steps correctly to actually get
        the data into the program and DB.  This is primarily due to the fact that it just doesn't
        call the rest of the functions and methods required to actually finish the import.  So
        currently a new work in progress. 3-8-2026"""
        expenses = []
        i = 0
        date, charge_name, expense, tag, notes = "", "", "", "", ""
        while i < len(row):
            if row[i] != "":
                if FileImportHandlers.date_check(row[i], fuzzy=False) is True:
                    date = FileImportHandlers.format_date(
                        row[i], year
                    )  # this is shitting itself somewhere
                    print(f"date in parse_csv(): {date}")
                    print(f"loop count is: {i}")
                    # date = "'{}'".format(row[i])
                    # date = year + " " + str(date).strip("'")
                    # date = "{}".format(str(datetime.strptime(date, "%Y %b %d").date()))
                    expenses.append(date)
                elif "$" in row[i]:
                    expense = row[i].replace("$", "").strip("\n")
                    print(f"expense in parse_csv(): {expense}")
                    expenses.append(expense)
                    # adds empty list elements to the end as placeholders
                    expenses.append(tag)
                    expenses.append(notes)
                else:
                    charge_name = f"{row[i]}"
                    print(f"charge_name in parse_csv(): {charge_name}")
                    # charge_name = "'{}'".format(row[i])
                    expenses.append(charge_name)
                i += 1
            else:
                i += 1
        return expenses

    @staticmethod
    def cap_one_import(pdf_path: str, import_year: int):
        """This is basically the front end to the import_cap_one_pdf function in the Page class and
        also serves as main handler for formatting and labelling all the Capital One institution
        specific data formats.  This is the other side of the institution specific template that is
        needed when adding support for a new source.  refer to the template documentation for more
        explicit details in that regard."""
        frame_list = []
        all_imports = pd.DataFrame
        pdf = pymupdf.open(pdf_path)
        # I had this backwards before in the for section, not sure why it
        # broke but likely due to object order
        import_pages = [Page(page, page_num) for page_num, page in enumerate(pdf)]
        for pages in import_pages:
            imports = pages.import_cap_one_pdf()
            if not imports.empty:
                # print(f"DEBUG: appended page {imports} to list")
                frame_list.append(imports)
            elif imports.empty:
                # print("DEBUG: elif imports.empty")
                pass
            else:
                print("DEBUG: else pass")
                pass
        # Join all tables into one DataFrame and reset the index before cleanup

        all_imports = pd.concat(frame_list)
        all_imports = all_imports.reset_index(drop=True)
        # valid rows should have a Date in the first column, removing ones that dont
        for row in all_imports.itertuples():
            try:
                if FileImportHandlers.date_check(row[1], fuzzy=False) is True:
                    pass
                else:
                    all_imports.drop(index=row[0], inplace=True)
            except TypeError:
                # any reason it is not a valid date should remove the row
                all_imports.drop(index=row[0], inplace=True)

        row_spot_check = all_imports.iloc[1]
        # takes the first row for column spot check
        try:
            # check if the contents of the 2nd column is a valid date, if not it means columns
            # need to be merged otherwise they are good to go.
            if (
                FileImportHandlers.date_check(str(row_spot_check.iloc[2]), fuzzy=False)
                is True
            ):
                row_check_merge_required = False
            else:
                row_check_merge_required = True
        except TypeError:
            print(
                f"something else broke in date_check spot check for col3, might need catchall"
            )
        if row_check_merge_required:
            # Relabel for clarity
            print(
                f"The spot check passed, no column swap needed, continuing with rename"
            )
            all_imports.columns = [
                "transaction_date",
                "post_date",
                "transaction_name",
                "transaction_amount",
            ]
        else:
            all_imports["Col6"] = all_imports["Col2"].str.cat(
                all_imports["Col3"], sep=" "
            )
            all_imports.drop(["Col2", "Col3"], axis=1, inplace=True)
            # Reorder the dataframe
            all_imports = all_imports[["Col1", "Col6", "Col4", "Col5"]]
            # Relabel for clarity
            all_imports.columns = [
                "transaction_date",
                "post_date",
                "transaction_name",
                "transaction_amount",
            ]

        # add the extra columns for tags and notes
        all_imports["tags"] = ""
        all_imports["notes"] = ""
        # check for missaligned columns, in testing it would happen where negative values greater
        # than ###.## would lose the minus sign to the previous column, check for this trailing
        # minus sign (-) and move it to the right column
        for row in all_imports.itertuples():
            if row[3][-1] == "-":
                print(f"Minus sign found in charge_name at index {row[0]}")
                all_imports.loc[row[0], "transaction_name"] = row[3][:-1].strip()
                all_imports.loc[row[0], "transaction_amount"] = "- " + row[4]
            else:
                pass
        all_imports = FileImportHandlers.format_import_dataframe(
            all_imports, import_year
        )
        return all_imports


######## End import handler functions ########


def main():
    """The main function is used for testing the import functions directly.  Mainly in cases
    where troubleshooting of pdf changes are needed or similar parsing related issues.
    """
    print("This is main for direct testing")
    selection = input("1 for embedded class \n2 to exit\n ")
    if selection == "1":
        pdf_path = os.path.join("statements", "2page-statement.pdf")
        # csv_path = os.path.join("statements", "converted.csv")
        # pymu_pdf(pdf_path, csv_path) swapped to cap one function
        FileImportHandlers.cap_one_import(pdf_path)
    if selection == "2":
        print("Exiting...")
        sys.exit(1)


if __name__ == "__main__":
    main()
