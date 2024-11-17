#!/usr/bin/env python3
"""Main entry point to this project. Running this starts the app."""

import contextlib
import json
import operator
import os
import sys
from pathlib import Path

# Layouts
import PySimpleGUI as sg

# from data import random_data as random_data_dict
from Layouts import Layouts
from tools import HTMLVIEWER, EditCommands, parse_dict_to_table

CLS = "cls" if sys.platform == "Windows" else "clear"
MAX_UNIT_LEN = 10
MIN_UNIT_LEN = 4


def main(table_values, raw_values):
    """Take two input parameters, table_values and raw_values,
    and performs a series of operations including creating a dictionary,
    filtering a table, editing a row, sorting a table, and handling window events
    until the event is a window closure or an exit event.

    Parameters
        table_values (list): A nexted list (array) representing the table data excluding notes.
        raw_values (list): A nexted list (array) representing the raw data, including notes.
    """
    global LOCAL_TABLE_VALUES  # noqa
    global LOCAL_RAW_VALUES  # noqa

    global _placeholder_raw
    global _placeholder_table

    LOCAL_RAW_VALUES = raw_values
    LOCAL_TABLE_VALUES = table_values

    _placeholder_raw, _placeholder_table = LOCAL_RAW_VALUES, LOCAL_TABLE_VALUES

    # Convert header (row, col) to string representation
    header_list = [(-1, 0), (-1, 1), (-1, 2), (-1, 3)]
    header_values = ["Unit Number", "Due Date", "Status", "Sale Type"]

    markdown_widget = window["-MARKDOWN-"].Widget
    _width, _height = markdown_widget.winfo_width(), markdown_widget.winfo_height()
    HTML_OBJ = HTMLVIEWER()
    parsed_markdown = HTML_OBJ.markdown2html(LOCAL_RAW_VALUES[0][4])
    HTML_OBJ.set_html(markdown_widget, parsed_markdown, strip=False)
    _width, _height = markdown_widget.winfo_width(), markdown_widget.winfo_height()
    # Create a dictionary to associate the string values with the tuples
    dict(zip(header_values, header_list, strict=False))
    # Bind events for keyboard shortcuts
    window.bind("<Alt_L><o>", "ALT-o")
    window.bind("<Alt_L><x>", "ALT-x")
    window.bind("<space>", "SPACE")
    window.bind("<Control_L><z>", "CTRL-z")
    window.bind("<Control_L><y>", "CTRL-y")

    editor_commands = EditCommands()

    while True:
        event, values = window.read()

        # Human readable widget names
        # TODO
        # ! Not sure these are doing anything. Either remove or standardize.
        raw_markdown_widget = window["-NOTES-"]
        window["-EDIT_NOTES-"]

        # DEBUGGING
        print(f"Event: {event}\nValues: {values}")

        # Filtering table
        if event == "-FILTER-":
            LOCAL_TABLE_VALUES, LOCAL_RAW_VALUES = filter_table(
                values["-FILTER-"], _placeholder_raw
            )
        if event == "-CLEAR-":
            refresh()
        # Editing values of a row. Spawns a custom popup menu
        if event == "-EDIT-":
            try:
                edit_row(values["-TABLE-"], LOCAL_RAW_VALUES[values["-TABLE-"][0]][-1])
            except IndexError:
                sg.popup_ok("Please select a row to edit")
        if event == "-ADD-":
            add_row()
        if event == "-SAVE-":
            try:
                row = LOCAL_RAW_VALUES[values["-TABLE-"][0]][:-1]
                LOCAL_RAW_VALUES, LOCAL_TABLE_VALUES = save_to_file(row, notes=values["-NOTES-"])
                _placeholder_raw, _placeholder_table = LOCAL_RAW_VALUES, LOCAL_TABLE_VALUES
            except IndexError:
                sg.popup_ok("Please select a row to save")
            print("Stop")
        if event == "-REMOVE-":
            try:
                LOCAL_TABLE_VALUES, LOCAL_RAW_VALUES = remove_row(values["-TABLE-"])
            except IndexError:
                sg.popup_ok("Please select a row to remove")

        if event == "-EDIT_NOTES-":
            if values["-EDIT_NOTES-"] is True:
                try:
                    if table_last_clicked:
                        note = (LOCAL_RAW_VALUES[table_last_clicked])[-1]
                    else:
                        note = LOCAL_RAW_VALUES[values["-TABLE-"][0]][-1]

                    display_html(note, True, markdown_widget, HTML_OBJ)
                    raw_markdown_widget.update(note)
                    window["-SAVE-"].update(disabled=False)
                except UnboundLocalError:
                    # Error handling if no row is selected
                    pass
                except IndexError:
                    sg.popup_ok("Please select a row to edit")
            else:
                try:
                    if table_last_clicked:
                        note = (LOCAL_RAW_VALUES[table_last_clicked])[-1]
                        html = display_html(note, False, markdown_widget, HTML_OBJ)
                        window["-MARKDOWN-"].update(html)
                        window["-SAVE-"].update(disabled=True)
                    else:
                        html = display_html(note, False, markdown_widget, HTML_OBJ)
                        window["-MARKDOWN-"].update(html)
                        window["-SAVE-"].update(disabled=True)
                except UnboundLocalError:
                    # Error handling if no row is selected
                    pass
        # Hotkeys
        if event in {window["-TABLE-"], "ALT-o"}:
            print("OK")
        if event in {window["-ADD-"], "ALT-x"}:
            break
        if event in {window["-EDIT-"], "CTRL-z"}:
            editor_commands.undo()
        if event in {window["-REMOVE-"], "CTRL-y"}:
            editor_commands.redo()
        # Show notes depending on row selected.
        if event and all(("-TABLE-" in event, "+CLICKED+" in event)):
            try:
                table_last_clicked = values["-TABLE-"][0]
                note = (LOCAL_RAW_VALUES[table_last_clicked])[-1]
                display_html(
                    notes=note,
                    notes_edit_state=False,
                    markdown_widget=markdown_widget,
                    HtmlViewer=HTML_OBJ,
                )

                if values["-EDIT_NOTES-"] is False:
                    html = display_html(
                        notes=note,
                        notes_edit_state=False,
                        markdown_widget=markdown_widget,
                        HtmlViewer=HTML_OBJ,
                    )
                    window["-MARKDOWN-"].update(html)
                else:
                    note = display_html(
                        notes=note,
                        notes_edit_state=True,
                        markdown_widget=markdown_widget,
                        HtmlViewer=HTML_OBJ,
                    )
                    raw_markdown_widget.update(note)

            except IndexError:
                pass
            except TypeError:
                pass

        # Sort table if header is clicked. Clicked column gets sorted
        # Additionally, Check if header was clicked and not the "row" column
        with contextlib.suppress(IndexError, TypeError):
            if all(
                (
                    isinstance(event, tuple),
                    event[0] == "-TABLE-",
                    event[2][0] == -1,
                    event[2][1] != -1,
                )
            ):
                # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
                col_num_clicked = event[2][1]
                LOCAL_TABLE_VALUES, LOCAL_RAW_VALUES = sort_table(
                    LOCAL_RAW_VALUES, (col_num_clicked, 0)
                )
                window["-TABLE-"].update(LOCAL_TABLE_VALUES)

        if event in {sg.WIN_CLOSED, "-EXIT-"}:
            break


def refresh() -> None:
    window["-FILTER-"].update("")
    window["-TABLE-"].update(_placeholder_table)
    window["-MARKDOWN-"].update("")
    window["-NOTES-"].update("")


def remove_row(index) -> tuple[list, list]:
    """Remove a row from table."""
    # DEBUG
    match sys.platform:
        case "linux":
            os.system("clear")
        case _:
            os.system("cls")
    print(index)  # DEBUG
    row = LOCAL_TABLE_VALUES[index[0]]
    if sg.popup_ok_cancel(f"Are you sure you want to remove {row[0]}?") == "OK":
        print(f"Removing {row[0]}")
        try:
            save_to_file(row, remove=True)
            LOCAL_TABLE_VALUES.pop(index[0])
            LOCAL_RAW_VALUES.pop(index[0])
            sg.popup_ok(f"Successfully removed {row[0]}")
        except Exception as e:
            print(e)
            print(f"Could not remove {row[0]}")
            sg.popup_ok(f"Could not remove {row[0]}\n{e}")
    else:
        print(f"Keeping {row[0]}")
    window["-TABLE-"].update(LOCAL_TABLE_VALUES)
    return LOCAL_TABLE_VALUES, LOCAL_RAW_VALUES


def add_row() -> None:
    add_window = LAYOUTS.add_item_layout()
    while True:
        add_event, add_values = add_window.read()

        # Input validation: Unit numbers must equal 10
        # The following logic checks if the length of the input is greater than 10
        # each time the input is changed. If it is greater than 10, the 11th
        # character will be removed.
        try:
            if len(add_values["-ADD_UNIT_NUMBER-"]) > MAX_UNIT_LEN:
                add_values["-ADD_UNIT_NUMBER-"] = add_values["-ADD_UNIT_NUMBER-"][:10]
                add_window["-ADD_UNIT_NUMBER-"].update(add_values["-ADD_UNIT_NUMBER-"])
            elif len(add_values["-ADD_UNIT_NUMBER-"]) < MIN_UNIT_LEN:
                add_window["-ADD_UNIT_NUMBER-"].update("EQC-")
        except ValueError:
            break
        except TypeError:
            break
        try:
            if add_event == "-ADD_MENU_SAVE-":
                # Check for empty or invalid values
                if (
                    add_values["-ADD_UNIT_NUMBER-"] == ""
                    or "EQC-" not in add_values["-ADD_UNIT_NUMBER-"]
                ):
                    sg.popup_ok("Please enter a valid unit number")
                    continue
                if add_values["-ADD_UNIT_NUMBER-"] in [row[0] for row in LOCAL_TABLE_VALUES]:
                    sg.popup_ok("Unit number already exists")
                    continue
                if len(add_values["-ADD_UNIT_NUMBER-"]) != MAX_UNIT_LEN:
                    sg.popup_ok("Unitnumber must be 10 characters (6 digits) long")
                    continue

                # Add new row and append to table, LOCAL_RAW_VALUES
                row = [
                    add_values["-ADD_UNIT_NUMBER-"],
                    add_values["-ADD_DUE_DATE-"],
                    add_values["-ADD_STATUS-"],
                    add_values["-ADD_SALE_TYPE-"],
                ]
                save_to_file(row)
                LOCAL_TABLE_VALUES.append(row)
                LOCAL_RAW_VALUES.append(row)
                window["-TABLE-"].update(LOCAL_TABLE_VALUES)
                sg.popup_ok(f'Successfully added {add_values["-ADD_UNIT_NUMBER-"]}')
                break
            if add_event in {sg.WIN_CLOSED, "-ADD_MENU_CANCEL-"}:
                break
        except Exception as e:
            sg.popup_ok(f"Error: {e}")
            print(e)
            break
    add_window.close()


def edit_row(index: list, note: str) -> None:
    """Edit a row in the table based on the given index.

    Parameters
        index (list): The index of the row to be edited.
        note (str): The new value for the row.
    """

    # DEBUG
    os.system(CLS)
    print(index)

    row = LOCAL_TABLE_VALUES[index[0]]
    edit_window = LAYOUTS.edit_item_layout(row[0], row[1], row[2], row[3])

    while True:
        edit_event, edit_values = edit_window.read()

        # Input validation: Unit numbers must equal 10
        # The following logic checks if the length of the input is greater than 10
        # each time the input is changed. If it is greater than 10, the 11th
        # character will be removed.
        try:
            if len(edit_values["-EDIT_UNIT_NUMBER-"]) > MAX_UNIT_LEN:
                edit_values["-EDIT_UNIT_NUMBER-"] = edit_values["-EDIT_UNIT_NUMBER-"][:10]
                edit_window["-EDIT_UNIT_NUMBER-"].update(edit_values["-EDIT_UNIT_NUMBER-"])
            elif len(edit_values["-EDIT_UNIT_NUMBER-"]) < MIN_UNIT_LEN:
                edit_window["-EDIT_UNIT_NUMBER-"].update("EQC-")
        except Exception as e:
            print(e)
            break
        # Save Event
        if edit_event == "-EDIT_MENU_SAVE-":
            # Show a popup if successful, otherwise show a popup error
            try:
                row = [
                    edit_values["-EDIT_UNIT_NUMBER-"],
                    edit_values["-EDIT_DUE_DATE-"],
                    edit_values["-EDIT_STATUS-"],
                    edit_values["-EDIT_SALE_TYPE-"],
                    note,
                ]
                LOCAL_TABLE_VALUES[index[0]] = row[:-1]
                LOCAL_RAW_VALUES[index[0]] = row
                save_to_file(row, notes=note)
                # window["-TABLE-"].update(LOCAL_TABLE_VALUES)
                sg.popup("Done")
            except Exception as e:
                sg.popup_ok(f"Error: {e}")
                break
            edit_window.close()
            break
        if edit_event == "-EDIT_DUE_DATE_CHOICE-":
            edit_values["-EDIT_DUE_DATE-"] = sg.popup_get_date(
                edit_values["-EDIT_DUE_DATE-"], "Pick a date"
            )
            edit_window["-EDIT_DUE_DATE-"].update(edit_values["-EDIT_DUE_DATE-"])
        if edit_event == "-EDIT_MENU_CANCEL-" or sg.WIN_CLOSED:
            edit_window.close()
            break

    # window["-TABLE-"].update(LOCAL_TABLE_VALUES)


def sort_table(LOCAL_RAW_VALUES: list, cols: tuple) -> tuple:
    """Sorts a table by the clicked column in ascending and descending order.

    Parameters
        LOCAL_RAW_VALUES (list): The raw values of the table.
        cols (tuple): The columns to sort by.

    Returns
        tuple: A tuple containing the sorted table (list) and the raw values (list).
    """

    # Sort by clicked column, accending order
    for col in reversed(cols):
        try:
            sorted_raw_values = sorted(LOCAL_RAW_VALUES, key=operator.itemgetter(col))
        except Exception as e:
            sg.popup_error("Error in sort_table", "Exception in sort_table", e)
            return ()
    # Sort by clicked column, decending order
    if sorted_raw_values == LOCAL_RAW_VALUES:  # type: ignore
        for col in reversed(cols):
            try:
                sorted_raw_values = sorted(
                    LOCAL_RAW_VALUES, key=operator.itemgetter(col), reverse=True
                )
            except Exception as e:
                sg.popup_error("Error in sort_table", "Exception in sort_table", e)
    LOCAL_RAW_VALUES = sorted_raw_values  # type: ignore
    LOCAL_RAW_VALUES[0:][:-1]
    sorted_table = sorted_raw_values[0:][:-1]  # type: ignore
    return sorted_table, sorted_raw_values  # type: ignore[unbound]


def filter_table(filter_value: str, unmodified_raw_values: list) -> tuple:
    filtered_table = []
    filtered_raw_values = []

    print(f"\033[32m{filter_value}\033[0m")
    for row in unmodified_raw_values:
        if filter_value in row[0]:
            filtered_raw_values.append(row)
            filtered_table.append(row[:-1])
    window["-TABLE-"].update(filtered_table)
    return filtered_table, filtered_raw_values


def display_html(notes, notes_edit_state, markdown_widget, HtmlViewer) -> None:
    # Parse markdown to HTML
    if notes_edit_state is False:
        html_content = HtmlViewer.markdown2html(notes)
        parsed_html = HtmlViewer.set_html(markdown_widget, html_content)

        window["-NOTES-"].update(visible=False, disabled=True)
        window["-MARKDOWN-"].update(visible=True, disabled=True)
        window["-MARKDOWN-"].update(parsed_html)
        _width, _height = markdown_widget.winfo_width(), markdown_widget.winfo_height()
        return parsed_html
    window["-MARKDOWN-"].update(visible=False)
    window["-NOTES-"].update(visible=True, disabled=False)
    window["-NOTES-"].update(notes)
    return notes


def save_to_file(
    values_list, remove=False, notes="", jsonfile=Path("./data/random_data.json")
) -> tuple[list[str], list[str]]:
    """Save values to a file.

    Parameters
        values_list (list): List of values to save.
        remove (bool): Whether to remove the values from the file.
        notes (str): Additional notes.

    Returns
        str: notes.
    """

    unit_number = values_list[0]
    due_date = values_list[1]
    status = values_list[2]
    sale_type = values_list[3]
    random_data_dict = json.loads(jsonfile.read_text())

    if unit_number not in random_data_dict:
        print(f"Adding {unit_number}")
        random_data_dict[unit_number] = {
            "due_date": due_date,
            "status": status,
            "sale_type": sale_type,
            "notes": notes,
        }
    elif remove:
        print(f"Removing {unit_number}")
        del random_data_dict[unit_number]
    else:
        print(f"Updating {unit_number}")
        print(f"Note:\n{notes}")
        random_data_dict[unit_number].update(
            {
                "due_date": due_date,
                "status": status,
                "sale_type": sale_type,
                "notes": notes,
            }
        )
    jsonfile.write_text(json.dumps(random_data_dict))

    LOCAL_RAW_VALUES = parse_dict_to_table(random_data_dict)
    LOCAL_TABLE_VALUES = [row[:-1] for row in LOCAL_RAW_VALUES]
    window["-TABLE-"].update(LOCAL_TABLE_VALUES)
    # window["-NOTES-"].update("")
    # window["-MARKDOWN-"].update("")
    # window["-FILTER-"].update("")

    return LOCAL_RAW_VALUES, LOCAL_TABLE_VALUES


if __name__ == "__main__":
    LAYOUTS = Layouts()
    window, global_table_values, global_raw_values = LAYOUTS.main_layout()
    main(global_table_values, global_raw_values)
    window.close()
