#!/usr/bin/python
"""
The purpose of this module is to be used as a test bed for creating new class functions based on
the boilerplate function.  How useful this may be is yet to be determined but it was a copy paste
from how I got the first imports working.

How To Use
1. Put your pdf in the same folder as the tool for ease of use
2. Modify pdf_path variable with your pdf name
3. Execute this script choosing option 2 to get a page by page display of the pdf with a grid line
3a. The goal here is to try and determine the best grid size for your document to minimize area
    outside the transaction tables as well as to determine a good set of string to use for
    table_title_needle and end_of_trans_needle which are explained later
4. Update the variables in the import_pdf_boilerplate class function
5. Execute the script again and choose option 1 and in theory you should get a print to console of
    a nearly usable set of dataframes of all the desired transactions in your document.
6. If the data looks good ( random text in some columns is fine but in general it should be 4-5
    columns containing charge dates, charge amounts and the entitity in the transaction)
7.  Now copy the class function import_pdf_boilerplate() into the pdf_importers.py within the class
    and name it like import_yourbank_pdf().  Next do the same for test_boilerplate(pdf_path) into
    the same file but outside of the class just like the existing functions.  Finally add import
    imports = pages.import_pdf_boilerplate() line to the name of the class function.  Now you
    should have support for the new bank within this application.

Begin detailed explanation of how the class and related functions are supposed to operate together.

-class Page-
Creates objects out of each page of the imported pdf, its much easier to manipulate each page of a
pdf this way.  The object is generated via import_pages =[Page(page, page_num) for page_num, page
in enumerate(pdf)] in the base boilerplate function.  Assigning basic attributes such as the page
object itself, and page number.

-find_transaction_table()/find_table_end()/get_rect() functions-
These are used to search the pdf pages and find transactions tuned using the needle variables which
are set within the import_pdf_boilerplate() function example in the class.  These will search the
pages to find the ones with transaction tables and also set the rectangle clip coordinates for what
should be the last transaction entry in the document and return these to the parser.

-import_pdf_boilerplate()-
This function actually parses through the pdf pages looking for transaction tables which it then
extracts each table and returns the data as a pandas dataframe to the test_boilerplate().  Ideally
all the data is of the same format and column count to allow for reliable parsing via the related
modules.  Several variables here need to be populated as noted in the How To Use section.

Args:
    table_title_needle: A string such as table title unique to the transaction tables in your pdf
    end_of_trans_needle: A string that occurs exactly once in the whole document and is as close to
                        the last transaction in the transaction table. this is to avoid erroneous
                        data or prevent the tool from finding extra random tables
    default_clip: This is a rect object used as the default area to find tables in the document.
                    This should be limited as much as possible to how a table of transactions is
                    displayed on a page
    alt_clip = This is another rect object that functions the same as the default but it is also
                modified by the 'end_of_trans_needle' to function as a sort of bottom stop to the
                table especially if it spans multiple pages.  If you know that a multipage table
                has different boundaries than the first page you can account for that here as well.

-test_boilerplate()-
This function simply calls the class function to process the table and receives the resulting
merged dataframe.  The reason this function must be unique to each bank statement is because
that the class function it calls is unique to the bank and because it will be referenced and
executed from other components in the application based on the selected source bank type when
importing.  I have plans to make this function more generic and able to dynamically call the
correct class function but for now since I only have one support institution I have nothing else
to test with.

All that needs to be done when adding new imports is change
imports = pages.import_pdf_boilerplate() to the name of the class
function you create and comment out the print(all_imports) line.

Notes: Currently this has only been tested with tables spanning 1-3 pages so there is no guarantee
that it can do more than that currently.

"""

import os
import pymupdf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging as logger

pdf_path = os.path.join("relative", "path", "to", "pdf")


class Page:
    """my doc is my string, verify me"""

    def __init__(self, page: pymupdf.Page, page_number):
        self.name = __name__
        self.page = page
        self.page_number = page_number
        self.logger = logger()
        self.parsed_dataframe = pd.DataFrame()
        self.clip_y1 = 0

    def find_transaction_table(self, needle):
        """my doc is my string, verify me"""
        end_of_table = self.get_rect(needle)  # for capitalOne only
        if end_of_table:
            self.logger.DEBUG("rect of needle: {end_of_table}")
            return True
        return False

    def find_table_end(self, needle):
        """my doc is my string, verify me"""
        end_of_table = self.get_rect(needle)
        if end_of_table:
            self.clip_y1 = round(end_of_table[0].y1, 0) - 5
            # This sets the rectable up a few units to avoid including the end of table keyword in
            # the rectangle, you may need to adjust this depending on your specific import files.
            return self.clip_y1
        self.logger.DEBUG("Table end not found on page")
        return self.clip_y1

    def get_rect(self, needle):
        """my doc is my string, verify me"""
        found_rect = self.page.search_for(needle)
        return found_rect

    def parse_transaction_table(self, new_clip):
        """my doc is my string, verify me"""
        tabs = self.page.find_tables(
            clip=new_clip, strategy="text", join_x_tolerance=5, text_x_tolerance=5
        )
        if tabs.tables:
            df = tabs[0].to_pandas()
            # TODO I need to make column relabelling dynamic later
            df.columns = ["Col1", "Col2", "Col3", "Col4", "Col5"]
            df = df.replace("", np.nan)
            df = df.dropna()
        return df

    def import_pdf_boilerplate(self):
        """my doc is my string, verify me"""
        table_title_needle = "Title of transaction tables"
        end_of_trans_needle = (
            "Unique line found only after the last transaction in the document"
        )
        default_clip = ()
        alt_clip = ()
        # empty dataframe for processing
        if not alt_clip:
            alt_clip = default_clip
        if self.find_transaction_table(table_title_needle):
            new_clip_y1 = self.find_table_end(end_of_trans_needle)
            if new_clip_y1 == 0:
                self.parsed_dataframe = self.parse_transaction_table(default_clip)
            else:
                alt_clip[3] = new_clip_y1
                self.parsed_dataframe = self.parse_transaction_table(alt_clip)
            return self.parsed_dataframe
        return self.parsed_dataframe


#### End boilerplate class####
def test_boilerplate(pdf_path):
    """my doc is my string, verify me"""
    frame_list = []
    all_imports = pd.DataFrame
    pdf = pymupdf.open(pdf_path)
    import_pages = [Page(page, page_num) for page_num, page in enumerate(pdf)]
    for pages in import_pages:
        imports = pages.import_pdf_boilerplate()
        if not imports.empty:
            # print(imports)
            frame_list.append(imports)
        else:
            pass
    all_imports = pd.concat(frame_list)
    print(all_imports)
    return all_imports


def pymu_render(chosen_page):
    # This was copied from the pymupdf git repo designed for testing df joining, not really needed
    # for now.  Reference:
    # https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/table-analysis/join_tables.ipynb
    """Display a pixmap.

    Just to display Pixmap image of "item" - ignore the man behind the curtain.

    Args:
        item: any PyMuPDF object having a "get_pixmap" method.
        title: a string to be used as image title

    Generates an RGB Pixmap from item using a constant DPI and using matplotlib
    to show it inline of the notebook.
    """
    DPI = 150
    pix = chosen_page.get_pixmap(dpi=DPI)
    img = np.ndarray([pix.h, pix.w, 3], dtype=np.uint8, buffer=pix.samples_mv)
    plt.figure(dpi=DPI)  # set the figure's DPI
    plt.title("title")  # set title of image
    plt.grid(True)
    # plt.grid(markevery=10)
    plt.minorticks_on()
    plt.grid(color="gray", linestyle="--", linewidth=0.5)
    _ = plt.imshow(img, extent=(0, pix.w * 72 / DPI, pix.h * 72 / DPI, 0))
    plt.show()


def main():
    selection = input(
        "1 Test boilerplate extraction \n"
        "2 Render PDF pages with grid for rectangle visualization \n "
    )
    if selection == "1":
        test_boilerplate(pdf_path)
    elif selection == "2":
        pdf = pymupdf.open(pdf_path)
        for i in pdf:
            chosen_page = pdf[i]
            pymu_render(chosen_page)


if __name__ == "__main__":
    main()
