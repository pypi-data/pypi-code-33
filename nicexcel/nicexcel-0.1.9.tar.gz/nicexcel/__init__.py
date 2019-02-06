"""
=====
Formatting module for Excel files writing
=====

Provides

  - Content 1: code for writing python files

Available modules
---------------------
:nicexcel:
    Module that takes Pandas DataFrame objects and writes them to excel
    in a nicely formatted files:
        - column width auto-adapted to fit characters contained in it
        - filterable Excel columns
        - header freezed by default
        - no indexing by default
        - easy possibility of number formatting of columns

    Two main functions are available
        - to_excel_nice() --> wrapper of pd.DataFrame.to_excel() function are
            still available because of function wrapping
        - list_to_excel_nice() --> function that writes a dictionary of
            dataframes into one excel file, inserting each dataframe on a
            single sheet


References
---------------------
:Copyright: None
:License: MIT
"""
# =============================================================================
# Package attributes
# =============================================================================
# Documentation format
__docformat__ = 'NumPy'
# License type
__license__ = 'MIT'
# Status ('Prototype', 'Development' or 'Pre-production')
__status__ = 'Development'
# Version
__version__ = '0.1.9'
# Release date
__releasedate__ = '06/02/2018'


from nicexcel.wrapper import to_excel, to_excel_ms
