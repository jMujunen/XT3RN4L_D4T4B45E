#!/usr/bin/env python3

import sys
import os
import string
import operator
import PySimpleGUI as sg

# External libraries
from tkhtmlview import html_parser
import markdown
import pprint

# Layouts
import layout
import edit_layout
import add_layout
import data
from random_data import random_data as random_data_dict

# Custom Modules
from RandomValues import RandomValues
import Html_Viewer

def main(table_values, raw_values):
    global local_table_values
    global local_raw_values
    local_raw_values = raw_values
    local_table_values = table_values
    """
    A function that takes two input parameters, local_table_values and local_raw_values,
    and performs a series of operations including creating a dictionary, 
    filtering a table, editing a row, sorting a table, and handling window events 
    until the event is a window closure or an exit event.

    Parameters:
        local_table_values (list): A list of lists representing the table data excluding notes.
        local_raw_values (list): A list of lists representing the raw data, including notes.
    """
    # Convert header (row, col) to string representation
    header_list = [(-1,0), (-1,1), (-1,2), (-1,3)]
    header_values = ["Unit Number", "Due Date", "Status", "Sale Type"]
    
    markdown_widget = window["-MARKDOWN-"].Widget
    width, height = markdown_widget.winfo_width(), markdown_widget.winfo_height()
    HTML_OBJ = Html_Viewer.HTML_VIEWER()
    parsed_markdown = HTML_OBJ.markdown2html(local_raw_values[0][4])
    parsed_html = HTML_OBJ.set_html(markdown_widget, parsed_markdown, strip=False)
    width, height = markdown_widget.winfo_width(), markdown_widget.winfo_height()
    # Create a dictionary to associate the string values with the tuples
    header_tuple_dict = dict(zip(header_values, header_list))
    while True:
        event, values = window.read()
        # EQC-11-1111
        # Human readable widget names
        raw_markdown_widget = window["-NOTES-"]
        edit_notes_widget = window["-EDIT_NOTES-"]

        # DEBUGGING
        print(f"Event: {event}\nValues: {values}")

        # Determine state of checkbox
        if event == '-EDIT_NOTES-':
            try:
                note = local_raw_values[values["-TABLE-"][0]][-1]
                display_html(note, True, markdown_widget, HTML_OBJ)
            except IndexError:
                pass

        # Filtering table
        if event == '-FILTER-':
            local_table_values, local_raw_values = filter_table(values["-FILTER-"])

        # Editing values of a row. Spawns a custom popup menu
        if event == '-EDIT-':
            try:
                edit_row(values["-TABLE-"], local_raw_values[values["-TABLE-"][0]][-1])
            except IndexError:
                sg.popup_ok('Please select a row to edit')
        if event == '-ADD-':
            add_row()

        if event == '-REMOVE-':
            try:
                local_table_values, local_raw_values = remove_row(values["-TABLE-"])
            except IndexError:
                sg.popup_ok('Please select a row to remove')

        if event == '-EDIT_NOTES-':
            if values['-EDIT_NOTES-'] == True:
                note = display_html(note, True, markdown_widget, HTML_OBJ)
                raw_markdown_widget.update(note)
            else:
                html = display_html(note, False, markdown_widget, HTML_OBJ)
                window["-MARKDOWN-"].update(html)
        # Show notes depending on row selected.
        if event:
            if '-TABLE-' in event:
                if '+CLICKED+' in event:
                    try:
                        note = local_raw_values[values["-TABLE-"][0]][-1]
                        display_html(note, False, markdown_widget, HTML_OBJ)
                        
                        if values['-EDIT_NOTES-'] == False:
                            html = display_html(note, False, markdown_widget, HTML_OBJ)
                            window["-MARKDOWN-"].update(html)
                        else:
                            note = display_html(note, True, markdown_widget, HTML_OBJ)
                            raw_markdown_widget.update(note)
                        
                    except IndexError:
                        pass
                    except TypeError:
                        pass
        
        # Sort table if header is clicked. Clicked column gets sorted
        if isinstance(event, tuple):
            # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
            # You can also call Table.get_last_clicked_position to get the cell clicked
            if event[0] == '-TABLE-':
                # Check if header was clicked and not the "row" column
                if event[2][0] == -1 and event[2][1] != -1:
                    col_num_clicked = event[2][1]
                    local_table_values, local_raw_values = sort_table(local_raw_values,(col_num_clicked, 0))
                    window['-TABLE-'].update(local_table_values)
        
        if event == sg.WIN_CLOSED or event == "-EXIT-":
            break

def remove_row(index):
    try:
        os.system('clear')
        print(index)
    except:
        os.system('cls')
        print(index)
    
    row = local_table_values[index[0]]
    if sg.popup_ok_cancel(f'Are you sure you want to remove {row[0]}?') == 'OK':
        print(f'Removing {row[0]}')
        try:
            save_to_file(row, remove=True)
            local_table_values.pop(index[0])
            local_raw_values.pop(index[0])
            sg.popup_ok(f'Successfully removed {row[0]}')
        except Exception as e:
            print(e)
            print(f'Could not remove {row[0]}')
            sg.popup_ok(f'Could not remove {row[0]}\n{e}')
    else:
        print(f'Keeping {row[0]}')
    window['-TABLE-'].update(local_table_values)
    return local_table_values, local_raw_values

def add_row():
    add_window = add_layout.layout()
    while True:
        add_event, add_values = add_window.read()

        # Input validation: Unit numbers must equal 10
        # The following logic checks if the length of the input is greater than 10
        # each time the input is changed. If it is greater than 10, the 11th
        # character will be removed.
        if len(add_values['-ADD_UNIT_NUMBER-']) > 10:
            add_values['-ADD_UNIT_NUMBER-'] = add_values['-ADD_UNIT_NUMBER-'][:10]
            add_window['-ADD_UNIT_NUMBER-'].update(add_values['-ADD_UNIT_NUMBER-'])
        try:
            if add_event == '-ADD_MENU_SAVE-':
                # Check for empty or invalid values
                if add_values['-ADD_UNIT_NUMBER-'] == '' or \
                        'EQC-' not in add_values['-ADD_UNIT_NUMBER-']:
                    sg.popup_ok('Please enter a valid unit number')
                    continue
                if add_values['-ADD_UNIT_NUMBER-'] in [row[0] for row in local_table_values]:
                    sg.popup_ok('Unit number already exists')
                    continue
                if len(add_values['-ADD_UNIT_NUMBER-']) != 10:
                    sg.popup_ok('Unitnumber must be 10 characters (6 digits) long')
                    continue

                # Add new row and append to table, local_raw_values
                row = [
                    add_values['-ADD_UNIT_NUMBER-'],
                    add_values['-ADD_DUE_DATE-'],
                    add_values['-ADD_STATUS-'],
                    add_values['-ADD_SALE_TYPE-']
                ]
                save_to_file(row)
                local_table_values.append(row)
                local_raw_values.append(row)
                window['-TABLE-'].update(local_table_values)
                sg.popup_ok(f'Successfully added {add_values["-ADD_UNIT_NUMBER-"]}')
                break
            if add_event == sg.WIN_CLOSED or add_event == '-ADD_MENU_CANCEL-':
                break
        except Exception as e:
            sg.popup_ok(f'Error: {e}')
            print(e)
            break
    add_window.close()
def edit_row(index, note):
    """
    Edit a row in the table based on the given index.

    Parameters:
        index (int): The index of the row to be edited.

    Returns:
        None
    """
    try:
        os.system('clear')
        print(index)
    except:
        os.system('cls')
        print(index)
    row = local_table_values[index[0]]
    edit_window = edit_layout.layout(row[0], row[1], row[2], row[3])

    while True:
        edit_event, edit_values = edit_window.read()

        # Input validation: Unit numbers must equal 10
        # The following logic checks if the length of the input is greater than 10
        # each time the input is changed. If it is greater than 10, the 11th
        # character will be removed.
        try:
            if len(edit_values['-EDIT_UNIT_NUMBER-']) > 10:
                edit_values['-EDIT_UNIT_NUMBER-'] = edit_values['-EDIT_UNIT_NUMBER-'][:10]
                edit_window['-EDIT_UNIT_NUMBER-'].update(edit_values['-EDIT_UNIT_NUMBER-'])
        except Exception as e:
            print(e)
            break
        # Save Event
        if edit_event == '-EDIT_MENU_SAVE-':
            # Show a popup if successful, otherwise show a popup error
            try:
                row = [
                    edit_values['-EDIT_UNIT_NUMBER-'], 
                    edit_values['-EDIT_DUE_DATE-'], 
                    edit_values['-EDIT_STATUS-'], 
                    edit_values['-EDIT_SALE_TYPE-'],
                    note
                ]
                local_table_values[index[0]] = row[:-1]
                local_raw_values[index[0]] = row
                save_to_file(row)
                window['-TABLE-'].update(local_table_values)
                sg.popup_ok(f'Successfully edited {edit_values["-EDIT_UNIT_NUMBER-"]}')
            except Exception as e:
                sg.popup_ok(f'Error: {e}')
                break
            edit_window.close()
            break
        if edit_event == '-EDIT_DUE_DATE_CHOICE-':
            edit_values['-EDIT_DUE_DATE-'] = sg.popup_get_date(
                edit_values['-EDIT_DUE_DATE-'],
                'Pick a date')
            edit_window['-EDIT_DUE_DATE-'].update(edit_values['-EDIT_DUE_DATE-'])
        if edit_event == '-EDIT_MENU_CANCEL-' or sg.WIN_CLOSED:
            edit_window.close()
            break

    window['-TABLE-'].update(local_table_values)

def sort_table(local_raw_values, cols):
    """
    Sorts a table by the clicked column in ascending and descending order.

    Parameters:
        local_raw_values (list): The raw values of the table.
        cols (tuple): The columns to sort by.

    Returns:
        tuple: A tuple containing the sorted table (list) and the raw values (list).
    """

    # Sort by clicked column, accending order
    for col in reversed(cols):
        try:
            sorted_raw_values = sorted(
                local_raw_values, 
                key=operator.itemgetter(col)
            )
        except Exception as e:
            sg.popup_error('Error in sort_table', 'Exception in sort_table', e)
    # Sort by clicked column, decending order
    if sorted_raw_values == local_raw_values:
        for col in reversed(cols):
            try:
                sorted_raw_values = sorted(
                    local_raw_values, 
                    key=operator.itemgetter(col), 
                    reverse=True
                )
            except Exception as e:
                sg.popup_error('Error in sort_table', 'Exception in sort_table', e)
    local_raw_values = sorted_raw_values
    local_table_values = local_raw_values[0:][:-1]
    sorted_table = sorted_raw_values[0:][:-1]
    return sorted_table, sorted_raw_values

    '''
    sorted_raw_values = sorted(local_raw_values, key=lambda x: x[sort_by])
    sorted_table_values = sorted(local_table_values, key=lambda x: x[sort_by])
    window['-TABLE-'].update(sorted_table_values)
    return sorted_raw_values, sorted_table_values
    '''
    # Access the tuple associated with a specific string value
    '''
    print(string_tuple_dict['unit'])  # Output: (-1, 0)
    print(string_tuple_dict['date'])  # Output: (-1, 1)
    print(string_tuple_dict['status'])  # Output: (-1, 2)
    '''

    # Access the string value associated with a specific tuple
    '''
    print(tuple_string_dict[(-1, 0)])  # Output: 'unit'
    print(tuple_string_dict[(-1, 1)])  # Output: 'date'
    print(tuple_string_dict[(-1, 2)])  # Output: 'status'
    '''
    

def filter_table(filter_value):
    filtered_table = []
    filtered_raw_values = []
    prefix = 'EQC-'
    #filter_string = prefix + input
    '''
    for row in local_table_values:
        if filter_string in row[0]:
            filtered_table.append(row)
    '''
    for row in local_raw_values:
        if filter_value in row[0]:
            filtered_raw_values.append(row)
            filtered_table.append(row[:-1])
    window["-TABLE-"].update(filtered_table)
    return filtered_table, filtered_raw_values

def display_html(notes, notes_edit_state, markdown_widget, HTML_VIEWER):

    # Parse markdown to HTML
    if notes_edit_state == False:
        html_content = HTML_VIEWER.markdown2html(notes)
        parsed_html = HTML_VIEWER.set_html(markdown_widget, html_content)

        window["-NOTES-"].update(visible=False, disabled=True)
        window["-MARKDOWN-"].update(visible=True, disabled=True)
        window["-MARKDOWN-"].update(parsed_html)
        width, height = markdown_widget.winfo_width(), markdown_widget.winfo_height()
        return parsed_html
    else:
        window["-MARKDOWN-"].update(visible=False)
        window["-NOTES-"].update(visible=True, disabled=False)
        window["-NOTES-"].update(notes)
        return notes

def save_to_file(values_list, remove=False):
    # Start Temporary logic. Remove once saving to file is fully implemented
    count = 0
    for key in values_list:
        count += 1
    if count > 5:
        print('Feature not yet implemented')
        sg.popup('Feature not yet implemented')
    #<!--- End Temporary logic ---!>

    row_dict = {}
    unit_number = values_list[0]
    due_date = values_list[1]
    status = values_list[2]
    sale_type = values_list[3]

    try:
        notes = values_list[4]
    except IndexError:
        notes = ''

    if unit_number not in random_data_dict.keys():
        print(f'Adding {unit_number}')
        row_dict[unit_number] = {}
        row_dict[unit_number]['due_date'] = due_date
        row_dict[unit_number]['status'] = status
        row_dict[unit_number]['sale_type'] = sale_type
        row_dict[unit_number]['notes'] = notes

    else:
        if remove == True:
            print(f'Removing {unit_number}')
            del random_data_dict[unit_number]
            row_dict = {}
        else:
            print(f'Updating {unit_number}')
            row_dict[unit_number] = {
                'due_date': due_date,
                'status': status,
                'sale_type': sale_type,
                'notes': notes
            }

    print(row_dict)
    random_data_dict.update(row_dict)
    local_raw_values = data.parse_dict_to_table(random_data_dict)
    local_table_values = []

    for row in local_raw_values:
        local_table_values.append(row[:-1])
    window['-TABLE-'].update(local_table_values)
    with open('random_data.py', 'w') as f:
        f.write('random_data = ' + pprint.pformat(random_data_dict))

#RandomValues(200).write_to_dict()
window, global_table_values, global_raw_values = layout.main()
main(global_table_values, global_raw_values)
window.close()