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
# Copyright
__copyright__ = ""
# License type
__license__ = 'MIT'
# Status ('Prototype', 'Development' or 'Pre-production')
__status__ = 'Development'
# Version (0.0.x = 'Prototype', 0.x.x = 'Development', x.x.x = 'Pre-production)
__version__ = '0.1.6'
# Release date
__releasedate__ = '04/02/2018'
# Credits (e.g. content contributors)
__credits__ = ()


from nicexcel.wrapper import to_excel, to_excel_ms
