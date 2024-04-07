#!/usr/bin/env python3

# alt_layout.py 

import random

import PySimpleGUI as sg
from tkhtmlview import html_parser

import data
from random_data import random_data

sg.theme("Dark Gray 2")

'''
[["","BBB","CCC","DDD"],["AAA","111","222","333"]]
'''


def main():
    values = data.parse_dict_to_table(random_data)
    table_values = []
    for value in values:
        table_values.append(value[:-1])
    search_column = [
        [
            sg.Text("Search"),
            sg.Input(size=(25, 1), key="-FILTER-", enable_events=True),
            sg.Button("Clear", key="-CLEAR-"),
        ],
        [
            # Loop through data and add to table
            sg.Table(
            values=table_values,
            headings=["Unit Number", "Due Date", "Status", "Sale Type"],
            enable_click_events=True,
            key="-TABLE-",
            expand_x=True,
            expand_y=True,
            justification="center",
            auto_size_columns=True,
            num_rows=25,
            right_click_menu= ["&Right", ["Right-Click-Menu-Item", "Another Right-Click-Menu-Item"]],
            border_width=1,
            alternating_row_color='#3d555a',
            selected_row_colors=('white', 'black'),
            )
        ],
        [
            sg.Button("Add", key="-ADD-"),
            sg.Button("Remove", key="-REMOVE-"),
            sg.Button('Edit', key='-EDIT-'),
        ]
    ]

    info_column = [
        [
            sg.Push(), sg.Text("Notes"), sg.Push()
        ],
        [
            sg.Multiline(
                size=(40, 25), 
                key="-NOTES-", 
                autoscroll_only_at_bottom=True,
                right_click_menu= ["&Right", ["Copy", "Paste"]],
                wrap_lines=True,
                disabled=True,
                visible=True,
            ),
            sg.Multiline(
                size=(40, 25), 
                disabled=True, 
                key='-MARKDOWN-', 
                visible=False
            ),
        ],
        [
            sg.Button("Save", key="-SAVE-", disabled=True),
            sg.Checkbox("Edit", key="-EDIT_NOTES-", default=False, enable_events=True),
        ]
    ]

    layout = [
        [
            sg.Column(search_column), 
            sg.VSeparator(), 
            sg.Column(info_column),
        ],
        [
            sg.HorizontalSeparator()
        ],
        
        [
            sg.StatusBar("Read Mode", key="-STATUS-"),
            sg.Push(),
            sg.Progress(100, orientation="h", size=(20, 2), key="-PROGRESS-", visible=False),
        ],
    ]
    
    window = sg.Window(
        "Data", 
        layout,
        finalize=True
        #metadata={"-SEARCH-": search_column}
    )

    # Add the ability to double-click a cell
    window["-TABLE-"].bind('<Double-Button-1>' , "+-double click-")
    return window, table_values, values


# Example  
if __name__ == "__main__":
    gui = main()
    while True:
        event, values = gui.read()
        print(f'''
        event: {event}
        values: {values}
        ''') # print(event, values)
        if event == '-TABLE-':
            gui["-NOTES-"].update(values["-TABLE-"])
        if event == sg.WIN_CLOSED or event == "-EXIT-":
            break
    