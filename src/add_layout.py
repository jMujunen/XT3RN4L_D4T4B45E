#!/usr/bin/env python3

# add_layout.py - Popup menu for adding a new entry

import datetime

import PySimpleGUI as sg

sg.theme("DarkGrey6")


def layout() -> sg.Window:
    layout = [
        [
            sg.Text("Unit Number"),
            sg.Push(),
            sg.Input(
                key="-ADD_UNIT_NUMBER-", size=(25, 1), default_text="EQC-", enable_events=True
            ),
        ],
        [
            sg.Text("Due Date"),
            sg.Push(),
            sg.Input(
                key="-ADD_DUE_DATE-",
                size=(16, 1),
                readonly=True,
                default_text=datetime.date.today().strftime("%Y-%m-%d"),
                text_color="black",
                background_color="dark gray",
            ),
            sg.CalendarButton(
                "Choose",
                key="-ADD_DUE_DATE_CHOICE-",
                format="%Y-%m-%d",
            ),
        ],
        [
            sg.Text("Status"),
            sg.Push(),
            sg.OptionMenu(["Damaged", "Ready", "Active"], key="-ADD_STATUS-", size=(20, 1)),
        ],
        [
            sg.Text("Sale Type"),
            sg.Push(),
            sg.OptionMenu(["Cash", "Net30"], key="-ADD_SALE_TYPE-", size=(20, 1)),
        ],
        [
            sg.Button("Add", key="-ADD_MENU_SAVE-"),
            sg.Button("Cancel", key="-ADD_MENU_CANCEL-"),
        ],
    ]

    return sg.Window("Add Layout", layout)


# Example
if __name__ == "__main__":
    window = layout()
    while True:
        event, values = window.read()
        print(event, values)
        if event in (sg.WIN_CLOSED, "-ADD_MENU_CANCEL-"):
            break
        if event == "-ADD_MENU_SAVE-":
            try:
                sg.popup_ok(f'Successfully added {values["-ADD_UNIT_NUMBER-"]}')
            except Exception as e:
                sg.popup_error(f'{e!r} - Failed to save {values["-ADD_UNIT_NUMBER-"]}')

    window.close()
