import datetime
from dataclasses import dataclass, field

# from pathlib import Path
import PySimpleGUI as sg

from .tools import parse_dict_to_table


@dataclass
class Layouts:
    theme: str = field(default="Dark Gray 2")
    jsonfile: str = field(default="./data/random_data.json", repr=False)

    def __post__init__(self) -> None:
        """Init shared settings for the layouts."""
        sg.theme(self.theme)

    def main_layout(self, table_data: dict[str, dict[str, str]]) -> tuple[sg.Window, list, list]:
        values = parse_dict_to_table(table_data)
        table_values = [value[:-1] for value in values]
        # jsonfile = Path(jsonfile)
        # table_data = json.loads(jsonfile.read_text())
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
                    headings=["Unit Number", "Due Date", "  Status  ", "Sale Type"],
                    enable_click_events=True,
                    key="-TABLE-",
                    expand_x=True,
                    expand_y=True,
                    justification="center",
                    auto_size_columns=True,
                    num_rows=25,
                    border_width=1,
                    alternating_row_color="#3d555a",
                    selected_row_colors=("white", "black"),
                )
            ],
            [
                sg.Button("Add", key="-ADD-"),
                sg.Button("Remove", key="-REMOVE-"),
                sg.Button("Edit", key="-EDIT-"),
            ],
        ]

        info_column = [
            [sg.Push(), sg.Text("Notes"), sg.Push()],
            [
                sg.Multiline(
                    size=(40, 25),
                    key="-NOTES-",
                    right_click_menu=["&Right", ["Copy", "Paste"]],
                    disabled=True,
                    visible=True,
                ),
                sg.Multiline(size=(40, 25), disabled=True, key="-MARKDOWN-", visible=False),
            ],
            [
                sg.Button("Save", key="-SAVE-", disabled=True),
                sg.Checkbox("Edit", key="-EDIT_NOTES-", default=False, enable_events=True),
            ],
        ]

        layout = [
            [
                sg.Column(search_column),
                sg.VSeparator(),
                sg.Column(info_column),
            ],
        ]

        window = sg.Window(
            "Data",
            layout,
            resizable=True,
            finalize=True,
            grab_anywhere=True,
            font="JetBrainsMono 10",
            # metadata={"-SEARCH-": search_column}
        )

        # Add the ability to double-click a cell
        window["-TABLE-"].bind("<Double-Button-1>", "+-double click-")
        return window, table_values, values

    def add_item_layout(self) -> sg.Window:
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

    def edit_item_layout(self, unit_number: str, due_date="", status="", sale_type="") -> sg.Window:
        layout = [
            [
                sg.Text("Unit Number"),
                sg.Push(),
                sg.Input(
                    key="-EDIT_UNIT_NUMBER-",
                    size=(25, 1),
                    default_text=unit_number,
                    readonly=True,
                    text_color="black",
                    background_color="dark gray",
                ),
            ],
            [
                sg.Text("Due Date"),
                sg.Push(),
                # sg.DatePicker(key="-EDIT_DUE_DATE-", default_date=due_date)
                sg.Input(
                    key="-EDIT_DUE_DATE-",
                    size=(16, 1),
                    readonly=True,
                    text_color="black",
                    background_color="dark gray",
                    default_text=due_date,
                ),
                sg.CalendarButton(
                    "Choose",
                    key="-EDIT_DUE_DATE_CHOICE-",
                    format="%Y-%m-%d",
                ),
            ],
            [
                sg.Text("Status"),
                sg.Push(),
                sg.OptionMenu(
                    ["Damaged", "Ready", "Active"],
                    key="-EDIT_STATUS-",
                    size=(20, 1),
                    default_value=status,
                ),
            ],
            [
                sg.Text("Sale Type"),
                sg.Push(),
                sg.OptionMenu(
                    ["Cash", "Net30"],
                    key="-EDIT_SALE_TYPE-",
                    default_value=sale_type,
                    size=(20, 1),
                ),
                # sg.Input(key="-EDIT_SALE_TYPE-", size=(25,1), default_text=sale_type)
            ],
            [
                sg.Button("Save", key="-EDIT_MENU_SAVE-"),
                sg.Button("Cancel", key="-EDIT_MENU_CANCEL-"),
            ],
        ]

        return sg.Window("Edit Layout", layout)
