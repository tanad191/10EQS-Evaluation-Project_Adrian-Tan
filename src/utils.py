def extract_column_from_header(row):
    """
    Returns the header value for an HTML table cell 
    Input: the element of a table data cell
    """
    if (row.br):
        row.br.extract()
    if row.a:
        row.a.extract()
    if row.sup:
        row.sup.extract()
        
    column_name = ' '.join(row.contents)
    
    # Filter the digit and empty names
    if not(column_name.strip().isdigit()):
        column_name = column_name.strip()
        return column_name
