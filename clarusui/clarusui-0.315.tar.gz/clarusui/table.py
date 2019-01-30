from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from clarusui.gridvisualisationelement import GridViz
from clarusui.layout import Element
from clarusui import utils

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

tableTemplate = env.get_template('table.html')

class Table(GridViz):
    def __init__(self, response, **options):
        super(self.__class__, self).__init__(response,**options)
        self._dataFrame.insert(0, self._dataFrame.index.name, self._dataFrame.index) #add a column with values from index at beginning as we want to display these too
        self.defaultDisplayFormat = options.pop('defaultDisplayFormat', '{:,.0f}')
        self.columnDisplayFormats = options.pop('columnDisplayFormats', None)
        self.columnColourLogic = options.pop('columnColourLogic', None)
        self.columnFlashColourLogic = options.pop('columnFlashColourLogic', None)
        self._set_headers(self._get_filtered_col_headers())
        self._set_rows()    
        self.set_header_css_class(options.pop('headerCssClass', None))
        self.set_header_colour(options.pop('headerColour', None))
        
        
    def set_header_css_class(self, headerCssClass):        
        if (headerCssClass is not None):
            for header in self.headers:
                header.set_css_class(headerCssClass)
                
    def set_header_colour(self, colour):
        if colour is not None:
            for header in self.headers:
                header.set_bgcolour(colour)
    
    def set_column_header_colour(self, column, colour):
        header = self.headers[column]
        header.set_bgcolour(colour)
                
    def get_column_display_format(self, columnName):
        displayFormat = None
        if self.columnDisplayFormats is not None:
            displayFormat = self.columnDisplayFormats.get(columnName)
        
        if displayFormat is not None:
            return displayFormat
        else:
            return self.defaultDisplayFormat
        
    def _get_column_colour_logic(self, columnName):
        if self.columnColourLogic is not None:
            return self.columnColourLogic.get(columnName)
        return None
    
    def _eval_column_colour_logic(self, columnName, cellValue):
        logic = self._get_column_colour_logic(columnName)
        if logic is not None:
            return logic(cellValue)
        return None
    
    def _get_column_flash_colour_logic(self, columnName):
        if self.columnFlashColourLogic is not None:
            return self.columnFlashColourLogic.get(columnName)
        return None
    
    def _eval_column_flash_colour_logic(self, columnName, cellValue):
        logic = self._get_column_flash_colour_logic(columnName)
        if logic is not None:
            return logic(cellValue)
        return None
                      
    def _set_headers(self, headers):
        self.headers = []
       
        for header in headers:
            headerCell = Cell(header)
            self.headers.append(headerCell)
            
    def _index_of_column(self, header):
        fullHeaders = list(self._dataFrame)
        return fullHeaders.index(header)
    
    def _index_of_row(self, header):
        fullHeaders = list(self._dataFrame.index.values)
        return fullHeaders.index(header)
    
    def _set_rows(self):
        self.rows = []
        rowIdx = 0
        for row in self._get_filtered_row_headers():
            r = []
            for header in self.headers:
                cell = Cell(self._get_value(row if self._dataFrame.index.is_unique else rowIdx, 
                                            header.cellvalue if self._dataFrame.index.is_unique else self._index_of_column(header.cellvalue)), 
                            numberFormat=self.get_column_display_format(header.cellvalue))
                colour = self._eval_column_colour_logic(header.get_cell_value(), cell.get_cell_value())
                if colour is not None:
                    cell.set_bgcolour(colour)
                    
                flashColour = self._eval_column_flash_colour_logic(header.get_cell_value(), cell.get_cell_value())
                if flashColour is not None:
                    cell.set_flash_colour(flashColour)
                r.append(cell)
                if cell._is_numeric(): #right align number cells
                    header.add_custom_css({'text-align':'right'})
            self.rows.append(r)
            rowIdx += 1
    
    
    def get_cell(self, row, column):
        return self.rows[row][column]
    
    def _render(self):
        return tableTemplate.render(table=self)
    
    def toDiv(self):
        return self._render()
    
    #will set a flag against any cell with country name match - allow per column/cell etc?
    def add_country_flags(self):
        for row in self.rows:
            for cell in row:
                cv = cell.get_cell_value()
                countryCode = utils.get_country_code(cv)
                if countryCode is not None:
                    cell.set_icon('flag-icon flag-icon-'+countryCode.lower())
                    
        
    
        
class Cell(Element):
    def __init__(self, cellvalue, **options):
        super(self.__class__, self).__init__(None,**options)
        self.numberFormat = options.pop('numberFormat', '{:,.0f}')
        self.cellvalue = cellvalue
        self.iconName = None
        self.iconAlignment = 'left'
        if self._is_numeric():
            self.add_custom_css({'text-align':'right'})
    
    def _is_numeric(self):
        if self.cellvalue is None:
            return False
        try:
            x = float(str(self.cellvalue)) #cast to string as float(True) == 1
            return True
        except Exception:
            return False
    
    def set_number_format(self, numberFormat):
        self.numberFormat = numberFormat;
    
    def set_icon(self, iconName, iconAlignment='left'):
        self.iconName = iconName
        self.iconAlignment = iconAlignment
    
    def _iconify_cell(self, cellValue):
        if self.iconName is None:
            return cellValue
        iconCode = '<i class="'+self.iconName+'" aria-hidden="true"></i>'
        if self.iconAlignment == 'left':
            cellValue = iconCode + ' ' +cellValue
        else: 
            cellValue = cellValue + ' ' +iconCode
        return cellValue
            
    
    def get_cell_value(self):
        cv = ''
        if self._is_numeric():
            cv = self.numberFormat.format(float(self.cellvalue))
        else:
            cv = self.cellvalue
        
        return self._iconify_cell(cv)
            
    def toDiv(self):
        raise NotImplementedError("Table cell not suitable for standalone usage")