#!/usr/bin/env python3

# parse_data.py - parse data for table from data.py

from data import data_dict

def parse_dict_to_table(data):
    # Initialize the table with headers
    table = [["Unit Number", "Due Date", "Status", "Sale Type"]]
    
    # Iterate through the dictionary and extract values
    for unit_number, details in data.items():
        due_date = details.get('date', '')
        status = details.get('status', '')
        sale_type = details.get('sale_type', '')
        notes = details.get('notes', '')
        # Append the extracted values to the table
        table.append([unit_number, due_date, status, sale_type])
    
    return table
if __name__ == "__main__":
    print(parse_dict_to_table(data_dict))