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
    """my doc is my string, verify me"""

    def __init__(self, page: pymupdf.Page, page_number):
        self.name = __name__
        self.page = page
        self.page_number = page_number
        self.logger = LoggingHandler(__class__).log
        self.clip_y1 = 0
        self.parsed_dataframe = pd.DataFrame()
        # moved this for lint, havent tested

    def find_transaction_table(self, needle):
        """my doc is my string, verify me"""
        end_of_table = self.get_rect(needle)  # for capitalOne only
        if end_of_table:
            self.logger.debug(f"Calculated rect of needle: {end_of_table}")
            return True
        return False

    def find_table_end(self, needle):
        """my doc is my string, verify me"""
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
        """my doc is my string, verify me"""
        found_rect = self.page.search_for(needle)
        return found_rect

    def parse_transaction_table(self, new_clip):
        """my doc is my string, verify me"""
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
        """my doc is my string, verify me"""
        # This is specific to capital One credit card PDF statements which is what the needles
        # and rect reference
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
    """my doc is my string, verify me"""

    # these functions moved from handlers to consolidate all file import components to one module
    def __init__(self):
        self.name = __name__
        self.logger = LoggingHandler(__class__).log

    def __str__(self):
        return self.name

    @staticmethod
    def format_import_dataframe(import_frame: pd.DataFrame, import_year):
        """my doc is my string, verify me"""
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
        """my doc is my string, verify me"""
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
        """my doc is my string, verify me"""
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
        """my doc is my string, verify me"""
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
        """my doc is my string, verify me"""
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
        """my doc is my string, verify me"""
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
        # forcing exit here while troubleshooting
        # sys.exit(1)
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
            all_imports, parse_transaction_table
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
