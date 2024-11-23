import json
from pathlib import Path

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from tools import parse_dict_to_table


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data")
        self.setGeometry(100, 100, 800, 600)

        self.jsonfile = Path("./data/random_data.json").resolve()
        data_dict = json.loads(self.jsonfile.read_text())
        values = parse_dict_to_table(data_dict)
        table_values = [value[:-1] for value in values]

        self.init_ui(table_values, values)

    def init_ui(self, table_values, values) -> None:
        # Main layout
        main_layout = QHBoxLayout()

        # Search column
        search_column = QVBoxLayout()
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search"))
        self.search_input = QLineEdit()
        search_layout.addWidget(self.search_input)

        clear_button = QPushButton("Clear")
        search_layout.addWidget(clear_button)
        search_column.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setRowCount(len(table_values))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Unit Number", "Due Date", "  Status  ", "Sale Type"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)

        for row, value in enumerate(table_values):
            for col, item in enumerate(value):
                self.table.setItem(row, col, QTableWidgetItem(str(item)))

        search_column.addWidget(self.table)

        # Buttons
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        remove_button = QPushButton("Remove")
        edit_button = QPushButton("Edit")
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(remove_button)
        buttons_layout.addWidget(edit_button)
        search_column.addLayout(buttons_layout)

        # Info column
        info_column = QVBoxLayout()
        info_column.addWidget(QLabel("Notes"))
        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(True)
        info_column.addWidget(self.notes_text)
        self.markdown_text = QTextEdit()
        self.markdown_text.setReadOnly(True)
        self.markdown_text.setVisible(False)
        info_column.addWidget(self.markdown_text)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.setDisabled(True)
        edit_checkbox = QCheckBox("Edit")
        info_column.addLayout(buttons_layout)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.create_widget(search_column))
        splitter.addWidget(self.create_widget(info_column))

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(splitter)
        self.setCentralWidget(central_widget)

    def create_widget(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    @staticmethod
    def add_item_layout():
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Unit Number"))
        unit_number_input = QLineEdit()
        unit_number_input.setPlaceholderText("EQC-")
        layout.addWidget(unit_number_input)

        layout.addWidget(QLabel("Due Date"))
        due_date_input = QDateEdit()
        due_date_input.setDate(QDate.currentDate())
        due_date_input.setReadOnly(True)
        due_date_input.setCalendarPopup(True)
        layout.addWidget(due_date_input)

        layout.addWidget(QLabel("Status"))
        status_combo = QComboBox()
        status_combo.addItems(["Damaged", "Ready", "Active"])
        layout.addWidget(status_combo)

        layout.addWidget(QLabel("Sale Type"))
        sale_type_combo = QComboBox()
        sale_type_combo.addItems(["Cash", "Net30"])
        layout.addWidget(sale_type_combo)

        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    @staticmethod
    def edit_item_layout(unit_number, due_date="", status="", sale_type=""):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Unit Number"))
        unit_number_input = QLineEdit(unit_number)
        unit_number_input.setReadOnly(True)
        layout.addWidget(unit_number_input)

        layout.addWidget(QLabel("Due Date"))
        due_date_input = QDateEdit()
        due_date_input.setDate(QDate.fromString(due_date, "yyyy-MM-dd"))
        due_date_input.setReadOnly(True)
        due_date_input.setCalendarPopup(True)
        layout.addWidget(due_date_input)

        layout.addWidget(QLabel("Status"))
        status_combo = QComboBox()
        status_combo.addItems(["Damaged", "Ready", "Active"])
        status_combo.setCurrentText(status)
        layout.addWidget(status_combo)

        layout.addWidget(QLabel("Sale Type"))
        sale_type_combo = QComboBox()
        sale_type_combo.addItems(["Cash", "Net30"])
        sale_type_combo.setCurrentText(sale_type)
        layout.addWidget(sale_type_combo)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        widget = QWidget()
        widget.setLayout(layout)
        return widget


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
