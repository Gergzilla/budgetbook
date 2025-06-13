import pandas as pd
import os
import pymupdf
import numpy as np
from dateutil.parser import parse as dateparse

# this stuff below is only really needed for testing, not for prod
from utilities.logger import (
    LoggingHandler,
)  # temporary local utilities until packaging later
import pprint

# import matplotlib.pyplot as plt

# Class is fully functional as is joining all discovered tables for the following institutions: Capital One
# future insitutions will be added as I need them but the core functions should be universal in general
# Also planning to create a helper file for adding new institutions with functions as well
# helper file in import_template_tool.py
logger = LoggingHandler(str(os.path.basename(__file__))).log


class Page:
    def __init__(self, page: pymupdf.Page, page_number):
        self.name = __name__
        self.page = page
        self.page_number = page_number
        self.logger = LoggingHandler(__class__).log

    def find_transaction_table(self, needle):
        end_of_table = self.get_rect(needle)  # for capitalOne only
        if end_of_table:
            self.logger.debug("rect of needle: {end_of_table}")
            return True
        else:
            return False

    def find_table_end(self, needle):
        # print(f"Page: {self.page.number} into the find_table_end function?")
        self.clip_y1 = 0
        end_of_table = self.get_rect(needle)
        if end_of_table:
            self.clip_y1 = round(end_of_table[0].y1, 0) - 5
            # this sets the rectable up a few units to avoid including the end of table keyword in the rectangle
            return self.clip_y1
        else:
            self.logger.debug("Table end not found on page")
            return self.clip_y1

    def get_rect(self, needle):
        found_rect = self.page.search_for(needle)
        return found_rect

    def parse_transaction_table(self, new_clip):
        tabs = self.page.find_tables(
            clip=new_clip, strategy="text", join_x_tolerance=3, text_x_tolerance=5
        )
        # print(f"Page: {self.page.number} into the parse_transaction_table function?")
        if tabs.tables:
            # print(f"Page: {self.page.number} if tabs.tables in function?")
            df = tabs[0].to_pandas()
            # print(df)
            # there is an error handling issue here, if the function incorrectly identifies a table it can have the wrong number
            # of columns which causes the next part to fail/hang
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
        else:
            df = ""
            return df

    def import_cap_one_pdf(self):
        # print("Did I get here each time?")
        # This is specific to capital One credit card PDF statements which is what the needles and rect reference
        table_title = "Trans Date"
        end_of_trans_needle = "Total Transactions for This Period"
        self.parsed_dataframe = pd.DataFrame()
        default_clip = (30, 100, 600, 740)
        alt_clip = (30, 85, 600, 740)
        if alt_clip == ():
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
        else:
            # df = pd.DataFrame()
            # print(f"Page: {self.page.number} into the else for empty table?")
            return self.parsed_dataframe

    # Add more bank specific functions here

    def __str__(self):
        return self.name


######## Begin import handler functions ########


def cap_one_import(pdf_path):
    # print("from:cap_one_import I got called")
    # print(f"filepath is: {pdf_path}")
    frame_list = []
    all_imports = pd.DataFrame
    pdf = pymupdf.open(pdf_path)
    # I had this backwards before in the for section, not sure why it broke but likely due to object order
    import_pages = [Page(page, page_num) for page_num, page in enumerate(pdf)]
    # print("Got to: 107")
    # print(len(import_pages))
    for pages in import_pages:
        imports = pages.import_cap_one_pdf()
        if not imports.empty:
            # print(imports)
            frame_list.append(imports)
            # print("Table parsed")
        elif imports.empty:
            # print("elif imports.empty")
            pass
        else:
            # print("else pass")
            pass
        # print(dir(pages))
    # print(frame_list)
    # print("Got to: 114")
    # Join all tables into one DataFrame and reset the index before cleanup
    all_imports = pd.concat(frame_list)
    all_imports = all_imports.reset_index(drop=True)
    # valid rows should have a Date in the first column, removing ones that dont
    for row in all_imports.itertuples():
        try:
            datecheck = dateparse(row[1], fuzzy=True)
            # print(datecheck)
            if datecheck:
                pass
                # print(f"{row[1]} is a valid date")
            else:
                all_imports.drop(index=row[0], inplace=True)
        except:
            # any reason it is not a valid date should remove the row
            all_imports.drop(index=row[0], inplace=True)
            pass
    # print("Got to: 132")
    # Now join col 2 and 3 due to pdf parsing issues and drop the old ones
    all_imports["Col6"] = all_imports["Col2"].str.cat(all_imports["Col3"], sep=" ")
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
    # print("Got to: 145")
    # check for missaligned columns, in testing it would happen where negative values greater than ###.## would lose
    # the minus sign to the previous column, check for this trailing - and move it
    for row in all_imports.itertuples():
        if row[3][-1] == "-":
            print(f"Minus sign found in charge_name at index {row[0]}")
            all_imports.loc[row[0], "transaction_name"] = row[3][:-1].strip()
            all_imports.loc[row[0], "transaction_amount"] = "- " + row[4]
        else:
            pass
    # print("Got to: 155")
    # print(all_imports)
    return all_imports


######## End import handler functions ########


def main():
    print("this is main")
    selection = input("1 for embedded class \n2 to exit\n ")
    if selection == "1":
        pdf_path = os.path.join("statements", "2page-statement.pdf")
        csv_path = os.path.join("statements", "converted.csv")
        # pymu_pdf(pdf_path, csv_path) swapped to cap one function
        cap_one_import(pdf_path)
    if selection == "2":
        print("Exiting...")
        quit()


if __name__ == "__main__":
    main()
