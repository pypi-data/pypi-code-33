from models.export_models.export_document_elements import ExportElementStyle
import logging
row_title_style =None
row_value_style = None

table_header_style = None
table_rows_content_style = None
table_rows_root_content_style = None
table_not_classificated_rows = None

#init styles for export
def init_styles():
    try:
        global row_title_style
        row_title_style = ExportElementStyle(fw="bold")

        global row_value_style
        row_value_style = ExportElementStyle()

        global table_header_style
        table_header_style = ExportElementStyle(fw="bold",bgc="#e6e6ff")

        global table_rows_content_style
        table_rows_content_style = ExportElementStyle()

        global table_rows_root_content_style
        table_rows_root_content_style = ExportElementStyle(fw="bold",bgc="#e6f7ff")

        global table_not_classificated_rows
        table_not_classificated_rows = ExportElementStyle(fw="bold",bgc="#ffb3b3", fs="italic")


        logging.info("Styles init successful")
    except Exception as e:
        logging.error("Error initialization. " + str(e))