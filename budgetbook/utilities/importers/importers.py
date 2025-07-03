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

"""my doc is my string, verify me"""
# Class is fully functional as is joining all discovered tables for the following institutions:
# Capital One, Other
# Future insitutions will be added as I need them but the core functions should be universal in
# general.  A helper file has also been created to guide future importer creation.
# Helper File: import_template_tool.py
logger = LoggingHandler(str(os.path.basename(__file__))).log


class Page:
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
            self.logger.debug("rect of needle: {end_of_table}")
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
        self.logger.debug("Table end not found on page")
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
            # print(df)
            # there is an error handling issue here, if the function incorrectly identifies a table
            # it can have the wrong number of columns which causes the next part to fail/hang
            # TODO I need to make column relabelling dynamic later
            # print(len(df.columns))
            if len(df.columns) != 5:
                df = pd.DataFrame(columns=["Col1", "Col2", "Col3", "Col4", "Col5"])
            else:
                df.columns = ["Col1", "Col2", "Col3", "Col4", "Col5"]

            # print(2)
            df = df.replace("", np.nan)
            # print(3)
            df = df.dropna()
            # print(4)
            # print(f"Page: {self.page.number} end of parse_transaction_table function?")
            return df
        df = ""
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
                "Page {self.page.number} appears to have a transaction table"
            )
            new_clip_y1 = self.find_table_end(end_of_trans_needle)
            if new_clip_y1 == 0:
                self.parsed_dataframe = self.parse_transaction_table(default_clip)
            else:
                clip_list = list(alt_clip)
                clip_list[3] = new_clip_y1
                alt_clip = tuple(clip_list)
                self.logger.debug("parsed alt_clip is {alt_clip}")
                self.parsed_dataframe = self.parse_transaction_table(alt_clip)
            return self.parsed_dataframe
        # df = pd.DataFrame()
        # print(f"Page: {self.page.number} into the else for empty table?")
        return self.parsed_dataframe

    # Add more bank specific functions here

    def __str__(self):
        return self.name


######## Begin import handler functions ########


class file_import_handlers(object):
    # these funcitons moved from handlers to consolidate all file import components to one module
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
            formated_transaction_date = file_import_handlers.format_date(
                import_frame.iloc[index_num, 0], import_year
            )
            formated_post_date = file_import_handlers.format_date(
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
    def dateCheck(datestring, fuzzy=False):
        """my doc is my string, verify me"""
        print(f"datestring in dateCheck() method: {datestring}")
        try:
            dateparser.parse(datestring, fuzzy=fuzzy)
            return True
        except dateparser.ParserError as e:
            logger.debug(e)
            # e isnt technically used but caught for proper handling, this just needs to evaluate
            # as false if datestring is not a date
            return False

    @staticmethod
    def format_date(datestring, year):
        """my doc is my string, verify me"""
        formated_date = f"'{datestring}'"
        print(f"1: formated_date in format_date: {formated_date}")
        formated_date = year + " " + str(formated_date).strip("'")
        print(f"2: formated_date in format_date: {formated_date}")
        date_to_string = str(datetime.strptime(formated_date, "%Y %b %d").date())
        print(f"Did this break? {date_to_string}")
        formated_date = f"{date_to_string}"
        print(f"3: formated_date in format_date: {formated_date}")
        return formated_date

    @staticmethod
    def csvImporter(input_file_name, year: int = 2025):
        """my doc is my string, verify me"""
        # Works perfectly!  results in a joined list of formatted data and converted to dataframe
        joined_csv = []
        try:
            with open(input_file_name, newline="") as infile:
                infilereader = csv.reader(
                    filter(lambda line: line.strip(), infile), delimiter=","
                )
                for row in infilereader:
                    parsedRow = file_import_handlers.parseCSV(row, year)
                    joined_csv.append(parsedRow)
            infile.close()
            joined_df = pd.DataFrame(
                joined_csv,
                columns=[
                    "Transaction Date",
                    "Post Date",
                    "Charge Name",
                    "Charge Amount",
                    "Tags",
                    "Notes",
                ],
            )
            return joined_df
        except FileNotFoundError:
            logger.critical("No valid file was found to import")

    @staticmethod
    def parseCSV(row, year):  # Works perfect!
        """my doc is my string, verify me"""
        expenses = []
        i = 0
        date, charge_name, expense, tag, notes = "", "", "", "", ""
        while i < len(row):
            if row[i] != "":
                if file_import_handlers.dateCheck(row[i], fuzzy=False) is True:
                    date = file_import_handlers.format_date(
                        row[i], year
                    )  # this is shitting itself somewhere
                    print(f"date in parseCSV(): {date}")
                    print(f"loop count is: {i}")
                    # date = "'{}'".format(row[i])
                    # date = year + " " + str(date).strip("'")
                    # date = "{}".format(str(datetime.strptime(date, "%Y %b %d").date()))
                    expenses.append(date)
                elif "$" in row[i]:
                    expense = row[i].replace("$", "").strip("\n")
                    print(f"expense in parseCSV(): {expense}")
                    expenses.append(expense)
                    # adds empty list elements to the end as placeholders
                    expenses.append(tag)
                    expenses.append(notes)
                else:
                    charge_name = f"{row[i]}"
                    print(f"charge_name in parseCSV(): {charge_name}")
                    # charge_name = "'{}'".format(row[i])
                    expenses.append(charge_name)
                i += 1
            else:
                i += 1
        return expenses

    @staticmethod
    def cap_one_import(pdf_path, import_year):
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
                frame_list.append(imports)
            elif imports.empty:
                # print("DEBUG: elif imports.empty")
                pass
            else:
                # print("DEBUG: else pass")
                pass
        # Join all tables into one DataFrame and reset the index before cleanup
        all_imports = pd.concat(frame_list)
        all_imports = all_imports.reset_index(drop=True)
        # valid rows should have a Date in the first column, removing ones that dont
        for row in all_imports.itertuples():
            try:
                datecheck = dateparser.parse(row[1], fuzzy=True)
                # print(datecheck)
                if datecheck:
                    pass
                else:
                    all_imports.drop(index=row[0], inplace=True)
            except TypeError:
                # any reason it is not a valid date should remove the row
                all_imports.drop(index=row[0], inplace=True)
        # Now join col 2 and 3 due to pdf parsing issues and drop the old ones
        all_imports["Col6"] = all_imports["Col2"].str.cat(all_imports["Col3"], sep=" ")
        all_imports.drop(["Col2", "Col3"], axis=1, inplace=True)
        # Reorder the dataframe
        all_imports = all_imports[["Col1", "Col6", "Col4", "Col5"]]
        # Relabel for clarity
        all_imports.columns = [
            "Transaction Date",
            "Post Date",
            "Charge Name",
            "Charge Amount",
        ]
        all_imports["Tags"] = ""
        all_imports["Notes"] = ""
        # check for missaligned columns, in testing it would happen where negative values greater
        # than ###.## would lose the minus sign to the previous column, check for this trailing
        # minus sign (-) and move it to the right column
        for row in all_imports.itertuples():
            if row[3][-1] == "-":
                print(f"Minus sign found in charge_name at index {row[0]}")
                all_imports.loc[row[0], "Charge Name"] = row[3][:-1].strip()
                all_imports.loc[row[0], "Charge Amount"] = "- " + row[4]
            else:
                pass
        all_imports = file_import_handlers.format_import_dataframe(
            all_imports, import_year
        )
        return all_imports


######## End import handler functions ########


def main():
    print("this is main")
    selection = input("1 for embedded class \n2 to exit\n ")
    if selection == "1":
        pdf_path = os.path.join("statements", "2page-statement.pdf")
        csv_path = os.path.join("statements", "converted.csv")
        # pymu_pdf(pdf_path, csv_path) swapped to cap one function
        file_import_handlers.cap_one_import(pdf_path)
    if selection == "2":
        print("Exiting...")
        sys.exit(1)


if __name__ == "__main__":
    main()
