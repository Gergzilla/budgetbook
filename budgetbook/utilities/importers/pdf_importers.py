import pandas as pd
import os
import pymupdf
import numpy as np
# this stuff below is only really needed for testing, not for prod
from utilities.logger import LoggingHandler #temporary local utilities until packaging later
import pprint
import matplotlib.pyplot as plt

# Class is fully functional as is joining all discovered tables for the following institutions: Capital One
# future insitutions will be added as I need them but the core functions should be universal in general
# Also planning to create a helper file for adding new institutions with functions as well
logger = LoggingHandler(str(os.path.basename(__file__))).log

class Page:
    def __init__(self, page : pymupdf.Page, page_number):
        self.name = __name__
        self.page = page
        self.page_number = page_number
        self.logger = LoggingHandler(__class__).log

    def find_transaction_table(self, needle):
        end_of_table = self.get_rect(needle)#for capitalOne only
        if end_of_table:
            self.logger.debug("rect of needle: {end_of_table}")
            return True
        else: 
            return False
        
    def find_table_end(self, needle):
        self.clip_y1 = 0
        end_of_table = self.get_rect(needle)
        if end_of_table:
            self.clip_y1 = round(end_of_table[0].y1,0)-5
            # this sets the rectable up a few units to avoid including the end of table keyword in the rectangle
            return self.clip_y1
        else:
            self.logger.debug("Table end not found on page")
            return self.clip_y1
    
    def get_rect(self, needle):
        found_rect = self.page.search_for(needle)
        return found_rect
    
    def parse_transaction_table(self, new_clip):
        tabs = self.page.find_tables(clip=new_clip, strategy="text", join_x_tolerance=5, text_x_tolerance=5)
        if tabs.tables:
            df = tabs[0].to_pandas()
            #TODO I need to make column relabelling dynamic later
            df.columns = ["Col1","Col2","Col3","Col4","Col5"]
            df = df.replace("", np.nan)
            df = df.dropna()
        return df    
        
    def import_cap_one_pdf(self): 
        # This is specific to capital One credit card PDF statements which is what the needles and rect reference
        table_title = "Trans Date"
        end_of_trans_needle = "Total Transactions for This Period"
        self.parsed_dataframe = pd.DataFrame()
        default_clip = (30, 100, 600, 740)
        alt_clip = (30, 85, 600, 740)
        if alt_clip == ():
            alt_clip = default_clip
        if self.find_transaction_table(table_title):
            self.logger.debug("Page {self.page.number} appears to have a transaction table")
            new_clip_y1 = self.find_table_end(end_of_trans_needle)
            if new_clip_y1 == 0:
                self.parsed_dataframe = self.parse_transaction_table(default_clip)
            else:
                alt_clip[3] = new_clip_y1
                self.logger.debug("parsed alt_clip is {alt_clip}")
                self.parsed_dataframe = self.parse_transaction_table(alt_clip)
            return self.parsed_dataframe
        else:
            # df = pd.DataFrame()
            return self.parsed_dataframe
    
   # Add more bank specific functions here
        
    def __str__(self):
        return self.name
    
######## end classes ########
 
def cap_one_import(pdf_path):
    frame_list = []
    all_imports = pd.DataFrame
    pdf = pymupdf.open(pdf_path)
    #I had this backwards before in the for section, not sure why it broke but likely due to object order
    import_pages =[Page(page, page_num) for page_num, page in enumerate(pdf)]
    # print(page)
    for pages in import_pages:
        imports = pages.import_cap_one_pdf()
        if not imports.empty:
            # print(imports)
            frame_list.append(imports)
        else:
            pass
    # print(f"\n\n\nframe_list is \n: {frame_list}")
    all_imports = pd.concat(frame_list)
    print(all_imports)
    return all_imports

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