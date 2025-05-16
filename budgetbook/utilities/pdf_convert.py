import pandas as pd
import os
import pymupdf
import numpy as np
# this stuff below is only really needed for testing, not for prod
import pprint
import matplotlib.pyplot as plt

# Class is fully functional as is joining all discovered tables for the following institutions: Capital One
# future insitutions will be added as I need them but the core functions should be universal in general

class Page:
    def __init__(self, page : pymupdf.Page, page_number):
        self.name = __name__
        self.page = page
        self.page_number = page_number

    def find_transaction_table(self, needle):
        end_of_table = self.get_rect(needle)#for capitalOne only
        if end_of_table:
            return True
            # print(f"rect of needle: {end_of_table}")
        else: 
            return False
        
    def find_table_end(self, needle):
    #get_rect()
        self.clip_y1 = 0
        end_of_table = self.get_rect(needle)#for capitalOne only
        # end_of_table = self.page.search_for(needle)#for capitalOne only
        if end_of_table:
            self.clip_y1 = round(end_of_table[0].y1,0)-5
            return self.clip_y1
        else: 
            return 0
    
    def get_rect(self, needle):
        found_rect = self.page.search_for(needle)
        return found_rect
    
    def parse_transaction_table(self, new_clip):
        tabs = self.page.find_tables(clip=new_clip, strategy="text", join_x_tolerance=5, text_x_tolerance=5)
        if tabs.tables:
            df = tabs[0].to_pandas() #probably need header cleanup, test later
            # print(dir(df))
            df.columns = ["Col1","Col2","Col3","Col4","Col5"]
            df = df.replace("", np.nan)
            df = df.dropna()
        return df    
        
    def import_cap_one_pdf(self): 
        # This is specific to capital One credit card PDF statements which is what the needles and rect reference
        # I should make this into a generic processor for the class and pull the custom details into their own function
        table_title = "Trans Date"
        end_of_trans_needle = "Total Transactions for This Period"
        self.parsed_dataframe = pd.DataFrame()
        if self.find_transaction_table(table_title):
            # print(f"I think page {self.page.number} has a transaction table")
            clip_y1 = self.find_table_end(end_of_trans_needle)
            # print(clip_y1)
            if clip_y1 == 0:
                new_clip = (30, 100, 600, 740)
                self.parsed_dataframe = self.parse_transaction_table(new_clip)
            else:
                new_clip = (30, 85, 600, clip_y1)
                self.parsed_dataframe = self.parse_transaction_table(new_clip)
            # print(f"Table contents \n{df}")
            return self.parsed_dataframe
        else:
            # df = pd.DataFrame()
            return self.parsed_dataframe
    
    def import_pdf(self,table_title,end_of_trans_needle, new_clip):
        """Generalized import function to intake institution specific variables for importing transactions
          The intent is to have a 
        default box where a table usually is to minimize noise in the parsing.  And it is used in conjunction with the end needle
        to find the bottom bounds using the related functions.  This was a major headache

        Args:
        table_title: string that represents a reliable way to find transaction tables within a pdf
        end_of_trans_needle: string that represents a reliable way to find the last transaction
            -note end_of_trans_needle must occur only ONCE in the document
        new_clip is a tuple of rect coordinates(in units) for the given pdf to discard margins/titles

        The purpose is to more generalize the import function within the Pages class so that the institution (bank, account, etc)
        specific components can be separated into other modules to allow for cleaner integration and additions in the future
        """

        self.parsed_dataframe = pd.DataFrame() # empty dataframe for processing
        if self.find_transaction_table(table_title):
            clip_y1 = self.find_table_end(end_of_trans_needle)
            if clip_y1 == 0:
                new_clip = (30, 100, 600, 740)
                self.parsed_dataframe = self.parse_transaction_table(new_clip)
            else:
                new_clip = (30, 85, 600, clip_y1)
                self.parsed_dataframe = self.parse_transaction_table(new_clip)
            # print(f"Table contents \n{df}")
            return self.parsed_dataframe
        else:
            # df = pd.DataFrame()
            return self.parsed_dataframe
        
    def __str__(self):
        return self.name
    
def import_cap_one_pdf():
    table_title = "Trans Date"
    end_of_trans_needle = "Total Transactions for This Period"
    
def cap_one_class(pdf_path):
    frame_list = []
    all_imports = pd.DataFrame
    pdf = pymupdf.open(pdf_path)
    #I had this backwards before in the for section, not sure why it broke but likely due to object order
    import_pages =[Page(page, page_num) for page_num, page in enumerate(pdf)]
    # print(page)
    for pages in import_pages:
        imports = pages.import_cap_one_pdf()
        # print(type(imports))
        # if not imports:
        #     pass
        if not imports.empty:
            # print(imports)
            frame_list.append(imports)
        else:
            pass
    # print(f"\n\n\nframe_list is \n: {frame_list}")
    all_imports = pd.concat(frame_list)
    print(all_imports)
        # print(f"type is {type(imports)}")
    # print("test using the Page class to preserve dataframes for processing")

# #return the rect of where the end of transactions should be
# def find_transaction_table(page, needle):
#     end_of_table = page.search_for(needle)#for capitalOne only
#     if end_of_table:
#         return True
#         # print(f"rect of needle: {end_of_table}")
#     else: 
#         return False
    
# def find_table_end(page, needle):
#     #get_rect()
#     end_of_table = page.search_for(needle)#for capitalOne only
#     if end_of_table:
#         # return end_of_table
#         # print(f"Bottom of table around: {round(end_of_table[0].y1,0)-3}")
#         clip_y1 = round(end_of_table[0].y1,0)-5
#         return clip_y1
#         # print(f"rect of needle: {end_of_table}")
#     else: 
#         return 0

# def parse_transaction_table(page, new_clip):
#     tabs = page.find_tables(clip=new_clip, strategy="text", join_x_tolerance=5, text_x_tolerance=5)
#     if tabs.tables:
#         df = tabs[0].to_pandas() #probably need header cleanup, test later
#         # print(dir(df))
#         df.columns = ["Col1","Col2","Col3","Col4","Col5"]
#         df = df.replace("", np.nan)
#         df = df.dropna()
        
#     return df
    
# def import_cap_one_pdf(pdf_path, csv_path): #csv file shouldnt be needed later only the dataframes
#     expensesdf = []
#     table_title = "Trans Date"
#     end_of_trans_needle = "Total Transactions for This Period"
#     pdf = pymupdf.open(pdf_path)
#     for page in pdf:
#         if find_transaction_table(page,table_title):
#             print(f"I think page {page.number} has a transaction table")
#             clip_y1 = find_table_end(page,end_of_trans_needle)
#             print(clip_y1)
#             if clip_y1 == 0:
#                 new_clip = (30, 100, 600, 740)
#                 df = parse_transaction_table(page, new_clip)
#             else:
#                 new_clip = (30, 85, 600, clip_y1)
#                 df = parse_transaction_table(page,new_clip)
#             print(f"Table contents \n{df}")
#             # next we call parse find



def pymu_pdf(pdf_path, csv_path): #works!
    # This has been replaced by other functions above and works great, leaving for reference for now
    pdf = pymupdf.open(pdf_path)
    # print(page)
    # new_clip = page.search_for("Total Transactions for This Period")
    # print(new_clip)
    # for page_num, page in enumerate(pdf):
    #     print(f"page_num is {page_num}")
    #     print(f"page is: {page}")
    quit()
    print(f"Total pages: {len(pdf)}")
    for pages in pdf: 
        if pages.number == 2:
            if pages.search_for("Transactions"):
                print("probably stuff here")
                continue #skipping for now
            else:
                print("probably nothing here")
                continue
            found_needle= pages.search_for("Total Transactions for This Period")
            print(found_needle)
            tabs = pages.find_tables(clip=(30, 100, 600, 740),strategy="text", join_x_tolerance=6)
            if tabs.tables:
                # pprint.pp(tabs[0].extract())
                df = tabs[0].to_pandas()
                # print(df)
                df = df.replace("", np.nan)
                df = df.dropna()
                # df["post_date"] = df["Col1"] + " " + df["Col2"]
                # df.drop(['Col1', 'Col2'], axis=1, inplace=True)
                # print(df)
        elif pages.number == 3:
            found_needle = find_clip(pages)
            # found_needle= pages.search_for("Total Transactions for This Period")
            print(found_needle)
            # continue
            # tabs = pages.find_tables(clip=(30, 80, 600, 740),strategy="text", join_x_tolerance=6)
            tabs = pages.find_tables(clip=(30, 85, 600, 183),strategy="text", join_x_tolerance=6) #the last coord should come from the find_clip)
            if tabs.tables:
                print(f"I found {len(tabs.tables)} table on page 3")
                pprint.pp(tabs[0].extract())
                df = tabs[0].to_pandas()
                df = df.replace("", np.nan)
                df = df.dropna()
                # df["post_date"] = df["Col1"] + " " + df["Col2"]
                # df.drop(['Col1', 'Col2'], axis=1, inplace=True)
                print(df)

def pymu_render(chosen_page):
    # This was copied from the pymupdf git repo designed for testing df joining, not really needed for now
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
    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    _ = plt.imshow(img, extent=(0, pix.w * 72 / DPI, pix.h * 72 / DPI, 0))
    plt.show()
# Adjusting clip for find tables using matplot grid.  estimated values = clip=(60, 40, 720,600)

# def pdf_to_csv_tabula(pdf_path, csv_path):
#     print("disabled because tabula never worked well")
#     quit()
#     # tabula.convert_into(pdf_path, csv_path, output_format="csv", pages='all', stream=True)
#     # tbdf= tabula.read_pdf(pdf_path, encoding="latin-1", pages="all")
#     tbdf= tabula.read_pdf(pdf_path, encoding="latin-1", pages="3,4", columns=[],guess=False, pandas_options={'header': None}, stream=True)
#     # print(tbdf[3])
#     print(f"table 1 is: {tbdf[0]}")
#     print(f"table 2 is: {tbdf[1]}")
#     print(f"table 3 is: {tbdf[2]}")
#     quit()
#     idf = pd.DataFrame(tbdf[3])
#     print("first guess")
#     print(tbdf[3])
#     # print("second guess")
#     # print(tbdf[4])
#     # print(dir(idf))
#     # print(idf.columns)
#     idf.to_csv(csv_path,index=False) #this saves the table correctly but data needs fixing

selection = input("3 for PyMuPDF \n4 for pymupdf display test\n5 for PyMuPDF class test \n ")
if selection == "1":
    pdf_path = os.path.join("statements", "1page-statement.pdf")
    csv_path = os.path.join("statements", "converted.csv")
    # pdf_to_csv_tabula(pdf_path, csv_path)
elif selection == "2":
    pdf_path = os.path.join("statements", "2page-statement.pdf")
    csv_path = os.path.join("statements", "converted.csv")
    # pdf_to_csv_tabula(pdf_path, csv_path)
elif selection == "3":
    pdf_path = os.path.join("statements", "2page-statement.pdf")
    csv_path = os.path.join("statements", "converted.csv")
    # pymu_pdf(pdf_path, csv_path) swapped to cap one function
    print("no longer needs, converted to classes")
    # import_cap_one_pdf(pdf_path, csv_path)
elif selection == "4":
    pdf_path = os.path.join("statements", "2page-statement.pdf")
    pdf = pymupdf.open(pdf_path)
    chosen_page = pdf[2]
    pymu_render(chosen_page)
    chosen_page = pdf[3]
    pymu_render(chosen_page)
elif selection == "5":
    pdf_path = os.path.join("statements", "2page-statement.pdf")
    csv_path = os.path.join("statements", "converted.csv")
    # pymu_pdf(pdf_path, csv_path) swapped to cap one function
    cap_one_class(pdf_path)    