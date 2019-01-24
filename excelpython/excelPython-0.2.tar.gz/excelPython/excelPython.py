import win32com
from win32com.client import Dispatch
import os


class ExcelFile:
    def __init__(self, fileLocation):
        self.fileLocation = fileLocation
        self.workbook
        self.xlapp

    def __enter__(self):
        # Start an instance of Excel
        self.xlapp = win32com.client.DispatchEx("Excel.Application")
        # Open the workbook in said instance of Excel
        self.workbook = self.xlapp.workbooks.open(self.fileLocation)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Quit
        self.xlapp.Quit()

    def saveWorkbook(self):
        self.workbook.Save()

    def saveWorkbookAs(self, fileLocation, xlFileFormat ):
        self.workbook.SaveAs(os.path.abspath(fileLocation), FileFormat=xlFileFormat)