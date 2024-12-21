import pdfplumber
import pandas as pd
import osenv
import os
import sys
import re
import pikepdf
# Input file and password


class DataGather:
    def __init__(self, pdfpath: str, outputname:str, inputfilename: str = None):
        self.pdf_password = os.environ['EMAIL_PASSWORD']
        self.pdfpath = pdfpath
        if inputfilename == None:
            self.inputfilename = inputfilename
        else:
            self.inputfilename = os.path.join(pdfpath, inputfilename)
        
        self.outputname = os.path.join(pdfpath, outputname)
        self.rows = []
        self.column_names = ['Name', 'Type', 'ISIN', 'Own Piece', 'Under Accoonting', 'Piece', 'Currency','Avg Price', 'Currency Exchange', 'Price', 'Price HUF']
        self.column_names_dividend = ['Name', 'ISIN', 'Type', 'Stock Piece', 'Dividend', 'All Dividend', 'Expense', 'Tax', "LogDate"]
    
    def inputfile(self):
        filesinfolder = os.listdir(self.pdfpath)
        for element in filesinfolder:
            if "Done" in element:
                continue
            with pikepdf.open(os.path.join(self.pdfpath, element), password=self.pdf_password) as pdf:
                pdf.save(os.path.join(self.pdfpath, f"Done - {element}"))
            if "EK_HUN" in element:
                self.inputfilename = os.path.join(self.pdfpath,element)
            else:
                os.remove(os.path.join(self.pdfpath, element))

    def DePassword(self):
        with pikepdf.open(self.inputfilename, password=self.pdf_password, allow_overwriting_input=True) as pdf:
            pdf.save(self.outputname)
        if "Done" not in self.inputfilename:
            os.remove(self.inputfilename)


    
    # Function to check and convert numeric strings to floats
    def convert_numeric_strings(self, val):
        if isinstance(val, str) and val.replace('.', '', 1).isdigit():
            return float(val)  # Convert numeric strings to float
        return val  # Leave non-numeric strings as they are

    

    def DividendExtract(self):
        with pdfplumber.open(self.outputname) as pdf:
            for i, page in enumerate(pdf.pages):
                    data = page.extract_text()
        if "Osztalék" in data:
            extractedlines = [x for x in data.split('\n')]
        else:
            return 0

        for line in extractedlines:
            match = re.search(r'^(.*?)\s(IE\w+|US(?!D\w*)\w+|Részvény)', line)
            if match:
                company_name = match.group(1).strip()
                identifier = match.group(2)
                rest = line[match.end():].strip().split()
                self.rows.append([company_name, identifier] + rest)

        print(self.rows)
        df = pd.DataFrame(self.rows,columns=self.column_names_dividend)
        df = df.applymap(self.convert_numeric_strings)
        df['Tax'] = df['Tax'].str.replace(',', '.').astype(float)
        df['LogDate'] = pd.to_datetime(df['LogDate'], errors='coerce').dt.strftime('%Y-%m-%d')
        df = df[["LogDate", "ISIN", 'All Dividend', 'Tax', 'Stock Piece']]
        return df
        

   
    def MonthlyExtract(self) -> pd.DataFrame:
        # Open and read the PDF
        with pdfplumber.open(self.outputname) as pdf:
            for i, page in enumerate(pdf.pages):
                if i == 1:
                    data = page.extract_text()


        extractedlines = [x for x in data.split('\n')]



        for line in extractedlines:
            match = re.search(r'^(.*?)\s(IE\w+|US\w+|Részvény)', line)
            if match:
                company_name = match.group(1).strip()
                identifier = match.group(2)
                rest = line[match.end():].strip().split()
                self.rows.append([company_name, identifier] + rest)



        counter = 3
        for j in self.rows: 
            for i in j[3:]:
                value = i.replace(',', '.')
                j[counter] = j[counter].replace(',', '.')
                if '.' not in value and any(char.isdigit() for char in value) and i != j[-1][-3:]:
                    j[counter+1] = i + j[counter+1]
                    j.pop(counter)
                else:
                    counter += 1
                
                

            counter = 3

        df = pd.DataFrame(self.rows, columns=self.column_names)
        df.dropna(inplace=True)
        df = df.applymap(self.convert_numeric_strings)
        return df