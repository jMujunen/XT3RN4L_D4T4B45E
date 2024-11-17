import json
import pprint
import random
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import markdown
import PySimpleGUI as sg
from tkhtmlview import html_parser


@dataclass
class HTMLVIEWER:
    parser: html_parser.HTMLTextParser = field(default_factory=html_parser.HTMLTextParser)

    def set_html(self, widget, html, strip=True) -> None:
        prev_state = widget.cget("state")
        widget.config(state=sg.tk.NORMAL)
        widget.delete("1.0", sg.tk.END)
        widget.tag_delete(widget.tag_names)
        self.parser.w_set_html(widget, html, strip=strip)
        widget.config(state=prev_state)

    @staticmethod
    def markdown2html(markdown_content) -> str:
        return markdown.markdown(str(markdown_content))


def parse_dict_to_table(data: dict) -> list[str]:
    # Initialize the table with headers
    table = []

    # Iterate through the dictionary and extract values
    for unit_number, details in data.items():
        due_date = details.get("due_date", "")
        status = details.get("status", "")
        sale_type = details.get("sale_type", "")
        notes = details.get("notes", "")
        # Append the extracted values to the table
        table.append([unit_number, due_date, status, sale_type, notes])

    return table


@dataclass
class RandomValues:
    number_of_values: int = field(default=1)

    @staticmethod
    def generate_random_unit_number() -> str:
        """Generate a random unit number in the format 'EQC-XXXXXX'."""
        rng = random.randint(0, 999999)
        return f"EQC-{rng:06d}"

    @staticmethod
    def generate_random_due_date() -> str:
        """Generate a random due date within the range of '2024-04-01' to '2027-01-01'.

        Returns
        -------
            str: Empty string with 50% chance.
        """
        if random.choice([True, False]):
            start_date = datetime(2024, 4, 1)
            end_date = datetime(2027, 1, 1)
            random_date = start_date + (end_date - start_date) * random.random()
            return random_date.strftime("%Y-%m-%d")
        return ""

    @staticmethod
    def generate_random_status() -> str:
        """Generate a random status from the choices: 'Active', 'Ready', and 'Damaged'."""
        return random.choice(["Active", "Ready", "Damaged"])

    @staticmethod
    def generate_random_sale_type() -> str:
        if random.choice([True, False]):
            return random.choice(["Cash", "Net30"])
        return ""

    def generate_random_values(self) -> list[str]:
        """Generate a list of random values for the unit number, due date, status, and sale type."""
        self.unit_number = self.generate_random_unit_number()
        due_date = self.generate_random_due_date()
        status = self.generate_random_status()
        sale_type = self.generate_random_sale_type()
        if status == "Active":
            while not due_date:
                due_date = self.generate_random_due_date()
            while not sale_type:
                sale_type = self.generate_random_sale_type()

        if any((not due_date, status in {"Damaged", "Ready"}, not sale_type)):
            return [self.unit_number, "", status, ""]
        return [self.unit_number, due_date, status, sale_type]

    def _generate_random_notes(self) -> str:
        """Generate random notes with a varying number of bullet points."""
        num_bullet_points = random.randint(1, 5)
        notes = (
            f"# {self.unit_number}\n\n"
            + "--------------------\n\n"
            + "- "
            + "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt. "
            * random.randint(1, 3)
        )
        for _ in range(num_bullet_points):
            notes += (
                "\n- "
                + "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                * random.randint(1, 3)
            )
        return notes

    def write(self) -> None:
        """Write the generated random values to a dictionary where the key is the unit number."""
        data = {}
        random_data = Path("random_date.py")
        random_data_json = Path("random_data.json")
        for _i in range(self.number_of_values):
            random_values = self.generate_random_values()
            data[random_values[0]] = {
                "due_date": random_values[1],
                "status": random_values[2],
                "sale_type": random_values[3],
                "notes": self._generate_random_notes(),
            }
        content = f"random_data = {pprint.pformat(data)}"
        random_data.write_text(content)
        random_data_json.write_text(json.dumps(data, indent=4))


@dataclass
class EditCommands:
    """A class to store the undo and redo stacks."""

    redo_stack: list[str] = field(default_factory=list)
    undo_stack: list[str] = field(default_factory=list)

    def undo(self) -> None:
        """Pop a character from the undo stack and push it to the redo stack."""
        if len(self.undo_stack) > 0:
            char = self.undo_stack.pop()
            self.redo_stack.append(char)
            print(self.redo_stack)
            print(self.undo_stack)
            print(char)

    def redo(self) -> None:
        """Pop a character from the redo stack and push it to the undo stack."""
        if len(self.redo_stack) > 0:
            char = self.redo_stack.pop()
            self.undo_stack.append(char)
            print(self.redo_stack)
            print(self.undo_stack)
            print(char)

    def insert_text(self, text) -> str:
        self.undo_stack.append(text)
        return text


# @dataclass
# class EditStack:
#     """A class to store the undo and redo stacks."""

#     redo_stack: deque[str] = field(default_factory=lambda: deque(maxlen=8196))
#     undo_stack: deque[str] = field(default_factory=lambda: deque(maxlen=8196))

#     def undo(self) -> None:
#         """Pop a character from the undo stack and push it to the redo stack."""
#         if len(self.undo_stack) > 0:
#             char = self.undo_stack.pop()
#             self.redo_stack.append(char)
#             print(self.redo_stack)
#             print(self.undo_stack)
#             print(char)

#     def redo(self) -> None:
#         """Pop a character from the redo stack and push it to the undo stack."""
#         if len(self.redo_stack) > 0:
#             char = self.redo_stack.pop()
#             self.undo_stack.append(char)
#             print(self.redo_stack)
#             print(self.undo_stack)
#             print(char)

#     def insert_text(self, text) -> str:
#         self.undo_stack.append(text)
#         return text
