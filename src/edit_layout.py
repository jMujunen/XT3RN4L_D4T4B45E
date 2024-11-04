import PySimpleGUI as sg

sg.theme("DarkGrey6")


def layout(
    unit_number: str, due_date: str = "", status: str = "", sale_type: str = ""
) -> sg.Window:
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


# Example
if __name__ == "__main__":
    window = layout(111, 111, 111, 111)
    while True:
        event, values = window.read()
        print(event, values)
        if event in (sg.WIN_CLOSED, "-EDIT_MENU_CANCEL-"):
            break
    window.close()
