import datetime
import json
import os
import sys
from pathlib import Path
import operator
import contextlib
import markdown
from PySide6.QtCore import QCoreApplication, QDate, QEvent, QSettings, Qt
from PySide6.QtGui import QAction, QFont
# from PySide6.QAction import QMenuAction, QHeaderView

import PySide6.Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QDialog,
    QFontDialog,
)
from pyside_layout import MainWindow as MAIN
from tools import parse_dict_to_table
from typing import Any

MAX_UNIT_LEN = 10
MIN_UNIT_LEN = 4
LOCAL_TABLE_VALUES: list[list[Any]] = []
LOCAL_RAW_VALUES: list[list[Any]] = []
_placeholder_raw: list[list[Any]] = []
_placeholder_table: list[list[Any]] = []
_reversed_table_sort = False


class MainWindow(QMainWindow):
    def __init__(self, data_file="./data/random_data.json"):
        """Initialize the main window with a data file."""
        super().__init__()
        self.setWindowTitle("Data Editor")
        self.setGeometry(100, 100, 800, 600)

        self.jsonfile = Path(data_file).resolve()
        data_dict = json.loads(self.jsonfile.read_text())
        values = parse_dict_to_table(data_dict)
        table_values = [value[:-1] for value in values]
        self.raw_values = values
        self.init_ui(table_values, values)
        self.load_data()

    def clear_search_bar(self) -> None:
        print(self)
        print("Button was clicked")
        self.search_input.setText("")

    def init_ui(self, table_values: list[str], values: list[str]) -> None:  # noqa: PLR0915
        """Initialize the user interface with a table and search bar."""
        # self.setWindowTitle("Table Editor")
        # self.setGeometry(100, 100, 800, 600)

        # * ===== Main layout =====
        main_layout = QHBoxLayout()

        search_column = QVBoxLayout()
        search_layout = QHBoxLayout()

        # * ===== Search Bar Layout =====
        search_layout.addWidget(QLabel("Search"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)

        clear_button = QPushButton("Clear")
        clear_button.setCheckable(True)
        clear_button.clicked.connect(self.clear_search_bar)

        search_layout.addWidget(clear_button)
        search_column.addLayout(search_layout)

        # * ===== Table Layout =====
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.table = QTableWidget()
        self.table.setRowCount(len(table_values))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Unit Number", "Due Date", "  Status  ", "Sale Type"])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # type: ignore
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # type: ignore
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # type: ignore
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # type: ignore
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_table)

        self.current_cell = self.table.cellClicked.connect(self.cell_clicked)

        for row, value in enumerate(table_values):
            for col, item in enumerate(value):
                self.table.setItem(row, col, QTableWidgetItem(str(item)))

        search_column.addWidget(self.table)

        # * ===== Filter Layout =====
        filter_layout = QHBoxLayout()
        self.filter_label = QLabel("Filter:")
        self.filter_input = QLineEdit()
        self.filter_input.returnPressed.connect(self.filter_table)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.refresh)
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(self.clear_button)

        # * ===== Editor Layout =====
        info_column = QVBoxLayout()
        info_column.addWidget(QLabel("Notes"))

        # self.edit_notes_checkbox = QCheckBox("Edit Notes")
        # self.edit_notes_checkbox.stateChanged.connect(self.toggle_edit_notes)

        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(False)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_to_file)

        # info_column.addWidget(self.edit_notes_checkbox)
        info_column.addWidget(self.notes_text)
        info_column.addWidget(self.save_button)

        # * ===== Add Item layout =====
        add_layout = QHBoxLayout()
        self.addunitnumber = QLineEdit()
        self.addduedate = QDateEdit()
        self.addstatus = QComboBox()
        self.addstatus.addItems(["Damaged", "Active", "Inactive", "Pending"])
        self.addsaletype = QComboBox()
        self.addsaletype.addItems(["Cash", "Net30"])
        self.addbutton = QPushButton("Add")
        self.addbutton.clicked.connect(self.add_row)
        add_layout.addWidget(QLabel("Unit Number:"))
        add_layout.addWidget(self.addunitnumber)
        add_layout.addWidget(QLabel("Due Date:"))
        add_layout.addWidget(self.addduedate)
        add_layout.addWidget(QLabel("Status:"))
        add_layout.addWidget(self.addstatus)
        add_layout.addWidget(QLabel("Sale Type:"))
        add_layout.addWidget(self.addsaletype)
        add_layout.addWidget(self.addbutton)

        # * ==== Menu ====
        menubar = QMenuBar()
        filemenu = menubar.addMenu("File")
        editmenu = menubar.addMenu("Edit")
        settingsmenu = menubar.addMenu("Settings")

        self.setMenuBar(menubar)

        # - ---- Menu Actions ----
        self.addaction = QAction("Add")
        self.editaction = QAction("Edit")
        self.editaction = QAction("Edit")
        self.removeaction = QAction("Remove")
        self.saveaction = QAction("Save")
        self.settingsaction = QAction("Font")
        self.settingsaction.triggered.connect(self.choose_font)

        # settingsmenu.connect(self.choose_font)

        filemenu.addAction(self.addaction)
        editmenu.addAction(self.editaction)
        editmenu.addAction(self.removeaction)
        editmenu.addAction(self.saveaction)
        settingsmenu.addAction(self.settingsaction)

        # * ==== Main Layout ====
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.table)
        main_layout.addLayout(add_layout)
        # main_layout.addWidget(self.edit_notes_checkbox)
        main_layout.addWidget(self.notes_text)
        main_layout.addWidget(self.save_button)

        # * ==== Splitter ====
        splitter = QSplitter(Qt.Horizontal)  # type: ignore
        splitter.addWidget(self.create_widget(search_column))
        splitter.addWidget(self.create_widget(info_column))

        central_widget = QWidget()
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(splitter)
        self.setCentralWidget(central_widget)

    def sort_table(self, col: int) -> None:
        global _reversed_table_sort  # noqa: PLW0603

        if _reversed_table_sort:
            sorted_raw_values = sorted(LOCAL_RAW_VALUES, key=operator.itemgetter(col))
        else:
            sorted_raw_values = sorted(LOCAL_RAW_VALUES, key=operator.itemgetter(col), reverse=True)
        self.raw_values = sorted_raw_values
        # Toggle flag
        _reversed_table_sort = not _reversed_table_sort
        for row, values in enumerate(sorted_raw_values):
            for c, value in enumerate(values):
                self.table.setItem(row, c, QTableWidgetItem(value))

    def cell_clicked(self, row, col) -> None:
        """Handle cell click event."""
        item = self.table.item(row, col)
        if item is None:
            return
        value = item.text()
        note = self.raw_values[row][4]
        print(f"Cell clicked: Row {row}, Column {col}, Value: {value}, Content: {note}")
        self.notes_text.setPlainText(note)
        self.row, self.col = row, col

    def save_edited_row(  # noqa: PLR0913, PLR0917
        self, row_data, unit_number_input, duedate_input, status_input, saletype_input, notes_input
    ) -> None:
        """Save the edited row to the table and update the file with the new data.

        Args
        ----
            row_data (list): The original data of the row.
            unit_number_input (QLineEdit): The QLineEdit widget for the Unit Number field.
            duedate_input (QDateEdit): The QDateEdit widget for the Due Date field.
            status_input (QComboBox): The QComboBox widget for the Status field.
            saletype_input (QComboBox): The QComboBox widget for the Sale Type field.
            notes_input (QTextEdit): The QTextEdit widget for the Notes field.
        """
        unit_number = unit_number_input.text()
        due_date = duedate_input.date().toString("yyyy-MM-dd")
        status = status_input.currentText()
        sale_type = saletype_input.currentText()
        notes = notes_input.toPlainText()

        if len(unit_number) != MAX_UNIT_LEN or "EQC-" not in unit_number:
            QMessageBox.information(self, "Error", "Please enter a valid unit number")
            return

        row_data = [unit_number, due_date, status, sale_type, notes]
        for i, item in enumerate(self.table.selectedItems()):
            item.setText(row_data[i])

        self.save_to_file(row_data)
        QMessageBox.information(self, "Success", f"Successfully updated {unit_number}")

    def choose_font(self) -> None:
        ok = False
        ok, font = QFontDialog.getFont()
        print(font)
        if ok:
            self.notes_text.setFont(font)

    def add_action_triggered(self):
        print("Add action triggered")

    def edit_action_triggered(self):
        print("Edit action triggered")

    def remove_action_triggered(self):
        print("Remove action triggered")

    @staticmethod
    def create_widget(layout) -> QWidget:
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def load_data(self) -> None:
        global LOCAL_TABLE_VALUES, LOCAL_RAW_VALUES, _placeholder_raw, _placeholder_table  # noqa: PLW0603
        jsonfile = Path("./data/random_data.json")
        if jsonfile.exists():
            with open(jsonfile, encoding="utf-8") as f:  # noqa: PTH123
                data = json.load(f)
            LOCAL_TABLE_VALUES = [
                [k, v["due_date"], v["status"], v["sale_type"]] for k, v in data.items()
            ]
            LOCAL_RAW_VALUES = [
                [k, v["due_date"], v["status"], v["sale_type"], v["notes"]] for k, v in data.items()
            ]
            _placeholder_raw = LOCAL_RAW_VALUES.copy()
            _placeholder_table = LOCAL_TABLE_VALUES.copy()
            self.update_table()

    def update_table(self) -> None:
        self.table.setRowCount(len(LOCAL_TABLE_VALUES))
        for row, values in enumerate(LOCAL_TABLE_VALUES):
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def filter_table(self, *args) -> None:
        """Filter the table based on the input arguments.

        Args:
            *args: A variable number of arguments representing the filter values.
        """
        filter_value = " ".join(args)
        print(filter_value)
        if not filter_value:
            self.table.setRowCount(len(LOCAL_TABLE_VALUES))
            for row, values in enumerate(LOCAL_TABLE_VALUES):
                for col, value in enumerate(values):
                    self.table.setItem(row, col, QTableWidgetItem(value))
            return
        filtered_table = []
        filtered_raw_values = []
        for row in LOCAL_RAW_VALUES:
            if filter_value in row[0]:
                print("\n", filter_value, "\n\r", row[0])
                filtered_table.append(row[:-1])
                filtered_raw_values.append(row)
        self.table.setRowCount(len(filtered_table))
        for row, values in enumerate(filtered_table):
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.table_values = filtered_table
        self.raw_values = filtered_raw_values

    def refresh(self) -> None:
        self.filter_input.setText("")
        self.table.setRowCount(len(_placeholder_table))
        for row, values in enumerate(_placeholder_table):
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.tablevalues = _placeholder_table
        self.raw_values = _placeholder_raw
        self.notes_text.setPlainText("")
        # self.markdown_text.setText("")

    def add_row(self) -> None:
        unitnumber = self.addunitnumber.text()
        duedate = self.addduedate.date().toString("yyyy-MM-dd")
        status = self.addstatus.currentText()
        saletype = self.addsaletype.currentText()
        if len(unitnumber) != MAX_UNIT_LEN or "EQC-" not in unitnumber:
            QMessageBox.information(self, "Error", "Please enter a valid unit number")

            return
        if unitnumber in [row[0] for row in LOCAL_TABLE_VALUES]:
            QMessageBox.information(self, "Error", "Unit number already exists")
            return
        row = [unitnumber, duedate, status, saletype, ""]
        LOCAL_TABLE_VALUES.append(row[:-1])
        LOCAL_RAW_VALUES.append(row)
        self.save_to_file(row)
        self.update_table()
        QMessageBox.information(self, "Success", f"Successfully added {unitnumber}")

    def edit_row(self) -> None:
        selected_rows = list(self.table.selectedItems())
        if not selected_rows:
            QMessageBox.information(self, "Error", "Please select a row to edit")
            return
        row_data = [item.text() for item in selected_rows]
        unit_number, due_date, status, sale_type, notes = row_data

        edit_dialog = QDialog()
        layout = QVBoxLayout()

        unit_number_label = QLabel("Unit Number:")
        unit_number_input = QLineEdit(unit_number)
        duedate_label = QLabel("Due Date:")
        duedate_input = QDateEdit()
        duedate_input.setDate(datetime.datetime.fromtimestamp(datetime.datetime.now()))
        status_label = QLabel("Status:")
        status_input = QComboBox()
        status_input.addItems(["Damaged", "Active", "Inactive", "Pending"])
        status_input.setCurrentText(status)
        saletype_label = QLabel("Sale Type:")
        saletype_input = QComboBox()
        saletype_input.addItems(["Cash", "Sale Type"])
        saletype_input.setCurrentText(sale_type)
        notes_label = QLabel("Notes:")
        notes_input = QTextEdit(notes)
        save_button = QPushButton("Save")
        save_button.clicked.connect(
            lambda: self.save_edited_row(
                row_data,
                unit_number_input,
                duedate_input,
                status_input,
                saletype_input,
                notes_input,
            )
        )
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(edit_dialog.close)

        layout.addWidget(unit_number_label)
        layout.addWidget(unit_number_input)
        layout.addWidget(duedate_label)
        layout.addWidget(duedate_input)
        layout.addWidget(status_label)
        layout.addWidget(status_input)
        layout.addWidget(saletype_label)
        layout.addWidget(saletype_input)
        layout.addWidget(notes_label)
        layout.addWidget(notes_input)
        layout.addWidget(save_button)
        layout.addWidget(cancel_button)

        edit_dialog.setLayout(layout)
        edit_dialog.exec()

    def remove_row(self) -> None:
        selected_rows = list(self.table.selectedItems())
        if not selected_rows:
            QMessageBox.information(self, "Error", "Please select a row to remove")
            return
        row_data = [item.text() for item in selected_rows]
        if (
            QMessageBox.question(self, "Confirm", f"Are you sure you want to remove {row_data[0]}?")
            == QMessageBox.StandardButton.Yes
        ):
            self.save_to_file(row_data, remove=True)
            self.update_table()
            QMessageBox.information(self, "Success", f"Successfully removed {row_data[0]}")

    def save_to_file(self, *args, remove=False):  # -> None:
        unit_number, due_date, status, sale_type, notes = self.raw_values[self.row]

        random_data_dict = json.loads(self.jsonfile.read_text)
        if unit_number not in random_data_dict:
            random_data_dict[unit_number] = {
                "due date": due_date,
                "status": status,
                "sale type": sale_type,
                "notes": notes,
            }
        elif remove:
            del random_data_dict[unit_number]
        else:
            random_data_dict[unit_number].update({
                "due date": due_date,
                "status": status,
                "sale type": sale_type,
                "notes": notes,
            })

        self.jsonfile.write_text(json.dumps(random_data_dict))
        self.update_table()

    def toggle_edit_notes(self, state) -> None:
        if state == Qt.CheckState.Checked:
            # Assuming self.table.selecteIitems() is supposed to return the selected items
            selected_items = self.table.selectedItems()
            if selected_items:
                last_item_text = selected_items[-1].text()
                self.notes_text.setPlainText(last_item_text)
                self.notes_text.setEnabled(True)
                self.save_button.setEnabled(True)
                self.markdown_text.setEnabled(False)
            else:
                # Handle the case where no items are selected
                self.notes_text.setPlainText("")
                self.notes_text.setEnabled(False)
                self.save_button.setEnabled(False)
                self.markdown_text.setEnabled(True)
        else:
            self.notes_text.setPlainText("")
            self.notes_text.setEnabled(False)
            self.save_button.setEnabled(False)
            self.markdown_text.setEnabled(True)


if __name__ == "__main__":
    # app = QCoreApplication([])
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
