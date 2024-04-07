#!/usr/bin/env python3

import sys
import os
import string
import operator
import PySimpleGUI as sg
# External libraries
from tkhtmlview import html_parser
import markdown
# Layouts
import layout
import edit_layout
import add_layout
# Custom Modules
from RandomValues import RandomValues
import Html_Viewer

def main(table_values, raw_values):
    """
    A function that takes two input parameters, table_values and raw_values,
    and performs a series of operations including creating a dictionary, 
    filtering a table, editing a row, sorting a table, and handling window events 
    until the event is a window closure or an exit event.

    Parameters:
        table_values (list): A list of lists representing the table data excluding notes.
        raw_values (list): A list of lists representing the raw data, including notes.
    """
    # Convert header (row, col) to string representation
    header_list = [(-1,0), (-1,1), (-1,2), (-1,3)]
    header_values = ["Unit Number", "Due Date", "Status", "Sale Type"]
    
    markdown_widget = window["-MARKDOWN-"].Widget
    width, height = markdown_widget.winfo_width(), markdown_widget.winfo_height()
    HTML_OBJ = Html_Viewer.HTML_VIEWER()
    parsed_markdown = HTML_OBJ.markdown2html(raw_values[0][4])
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
                note = raw_values[values["-TABLE-"][0]][-1]
                display_html(note, True, markdown_widget, HTML_OBJ)
            except IndexError:
                pass

        # Filtering table
        if event == '-FILTER-':
            table_values, raw_values = filter_table(values["-FILTER-"])

        # Editing values of a row. Spawns a custom popup menu
        if event == '-EDIT-':
            try:
                edit_row(values["-TABLE-"])
            except IndexError:
                sg.popup_ok('Please select a row to edit')
        if event == '-ADD-':
            add_row()

        if event == '-REMOVE-':
            try:
                table_values, raw_values = remove_row(values["-TABLE-"])
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
                        note = raw_values[values["-TABLE-"][0]][-1]
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
                    table_values, raw_values = sort_table(raw_values,(col_num_clicked, 0))
        
        if event == sg.WIN_CLOSED or event == "-EXIT-":
            break

def remove_row(index):
    try:
        os.system('clear')
        print(index)
    except:
        os.system('cls')
        print(index)
    
    row = table_values[index[0]]
    if sg.popup_ok_cancel(f'Are you sure you want to remove {row[0]}?') == 'OK':
        print(f'Removing {row[0]}')
        table_values.pop(index[0])
        raw_values.pop(index[0])
    else:
        print(f'Keeping {row[0]}')
    window['-TABLE-'].update(table_values)
    return table_values, raw_values

def add_row():
    add_window = add_layout.layout()
    while True:
        add_event, add_values = add_window.read()
        try:
            if add_event == '-ADD_MENU_SAVE-':
                # Check for empty or invalid values
                if add_values['-ADD_UNIT_NUMBER-'] == '' or \
                        'EQC' not in add_values['-ADD_UNIT_NUMBER-']:
                    sg.popup_ok('Please enter a valid unit number')
                '''
                if add_values['-ADD_DUE_DATE-'] == '' or \
                        not re.match(r'\d{4}-\d{2}-\d{2}', add_values['-ADD_DUE_DATE-']):
                    sg.popup_ok('Please enter a valid due date')
                if add_values['-ADD_STATUS-'] == '':
                    sg.popup_ok('Please enter a status')
                if add_values['-ADD_SALE_TYPE-'] == '':
                    sg.popup_ok('Please enter a sale type')
                '''
                table_values.append([
                    add_values['-ADD_UNIT_NUMBER-'], 
                    add_values['-ADD_DUE_DATE-'], 
                    add_values['-ADD_STATUS-'], 
                    add_values['-ADD_SALE_TYPE-']
                ])
                sg.popup_ok(f'Successfully added {add_values["-ADD_UNIT_NUMBER-"]}')
                break
            if add_event == sg.WIN_CLOSED or add_event == '-ADD_MENU_CANCEL-':
                break
        except Exception as e:
            sg.popup_ok(f'Error: {e}')
            break
    add_window.close()
def edit_row(index):
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
    row = table_values[index[0]]
    edit_window = edit_layout.layout(row[0], row[1], row[2], row[3])

    while True:
        edit_event, edit_values = edit_window.read()
        if edit_event == '-EDIT_MENU_SAVE-':
            table_values[index[0]] = (
                edit_values['-EDIT_UNIT_NUMBER-'], 
                edit_values['-EDIT_DUE_DATE-'], 
                edit_values['-EDIT_STATUS-'], 
                edit_values['-EDIT_SALE_TYPE-']
            )
            print(table_values[index[0]])
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
    window['-TABLE-'].update(table_values)

def sort_table(raw_values, cols):
    """
    Sorts a table by the clicked column in ascending and descending order.

    Parameters:
        raw_values (list): The raw values of the table.
        cols (tuple): The columns to sort by.

    Returns:
        tuple: A tuple containing the sorted table (list) and the raw values (list).
    """

    # Sort by clicked column, accending order
    for col in reversed(cols):
        try:
            sorted_raw_values = sorted(
                raw_values, 
                key=operator.itemgetter(col)
            )
        except Exception as e:
            sg.popup_error('Error in sort_table', 'Exception in sort_table', e)
    # Sort by clicked column, decending order
    if sorted_raw_values == raw_values:
        for col in reversed(cols):
            try:
                sorted_raw_values = sorted(
                    raw_values, 
                    key=operator.itemgetter(col), 
                    reverse=True
                )
            except Exception as e:
                sg.popup_error('Error in sort_table', 'Exception in sort_table', e)

    sorted_table = sorted_raw_values[0:][:-1]
    window['-TABLE-'].update(sorted_table)
    return sorted_table, sorted_raw_values

    '''
    sorted_raw_values = sorted(raw_values, key=lambda x: x[sort_by])
    sorted_table_values = sorted(table_values, key=lambda x: x[sort_by])
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
    for row in table_values:
        if filter_string in row[0]:
            filtered_table.append(row)
    '''
    for row in raw_values:
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

RandomValues(200).write_to_dict()
window, table_values, raw_values = layout.main()
main(table_values, raw_values)
window.close()