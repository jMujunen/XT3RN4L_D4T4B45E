#!/usr/bin/env python3

# generate_random_values.py - generate random values for a table and store them in a dictionary

import json
import pprint
import random
from datetime import datetime
from pathlib import Path


class RandomValues:
    def __init__(self, number_of_values=1) -> None:
        """Initialize the class with the given number of values to generate. Default is 1."""
        self.number_of_values = number_of_values

    def generate_random_unit_number(self) -> str:
        """Generate a random unit number in the format 'EQC-XXXXXX' where X is a six digit number."""
        rng = random.randint(0, 999999)
        return f"EQC-{rng:06d}"

    def generate_random_due_date(self) -> str:
        """Generate a random due date within the range of '2024-04-01' to '2027-01-01'. Returns an empty string with 50% chance."""
        if random.choice([True, False]):
            start_date = datetime(2024, 4, 1)
            end_date = datetime(2027, 1, 1)
            random_date = start_date + (end_date - start_date) * random.random()
            return random_date.strftime("%Y-%m-%d")
        return ""

    def generate_random_status(self) -> str:
        """Generate a random status from the choices: 'Active', 'Ready', and 'Damaged'."""
        return random.choice(["Active", "Ready", "Damaged"])

    def generate_random_sale_type(self) -> str:
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

        if any((not due_date, status in ("Damaged", "Ready"), not sale_type)):
            return [self.unit_number, "", status, ""]
        return [self.unit_number, due_date, status, sale_type]

    def generate_random_notes(self) -> str:
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
                "notes": self.generate_random_notes(),
            }
        content = f"random_data = {pprint.pformat(data)}"
        random_data.write_text(content)
        random_data_json.write_text(json.dumps(data, indent=4))


# Test the random value generation
if __name__ == "__main__":
    RandomValues(200).write()
