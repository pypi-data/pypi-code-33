

# =============================================================================
# get header rows as string
# =============================================================================
def get_row_as_str(row: int):
    return repr(row)


# =============================================================================
# read header as dictionary
# =============================================================================
def read_header(ws, max_col, first_row=1):
    header_dict = {}
    for col in range(1, max_col+1):
        col_value = ws.cell(row=first_row, column=col).value
        header_dict[col_value] = col
    return header_dict
