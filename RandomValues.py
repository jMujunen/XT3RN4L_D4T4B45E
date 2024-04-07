#!/usr/bin/env python3

# generate_random_values.py - generate random values for a table and store them in a dictionary

import random
import pprint
from datetime import datetime, timedelta


class RandomValues:
    def __init__(self, number_of_values=1):
        self.number_of_values = number_of_values
    def generate_random_unit_number(self):
        rng = random.randint(0, 999999)
        return f"EQC-{rng:06d}"

    def generate_random_due_date(self):
        if random.choice([True, False]):
            start_date = datetime(2024, 4, 1)
            end_date = datetime(2027, 1, 1)
            random_date = start_date + (end_date - start_date) * random.random()
            return random_date.strftime('%Y-%m-%d')
        else:
            return ""

    def generate_random_status(self):
        return random.choice(["Active", "Ready", "Damaged"])

    def generate_random_sale_type(self):
        if random.choice([True, False]):
            return random.choice(["Cash", "Net30"])
        else:
            return ""

    def generate_random_values(self):
        # Return a list of random values
        self.unit_number = self.generate_random_unit_number()
        due_date = self.generate_random_due_date()
        status = self.generate_random_status()
        sale_type = self.generate_random_sale_type()
        if status == "Active":
            while not due_date:
                due_date = self.generate_random_due_date()
            while not sale_type:
                sale_type = self.generate_random_sale_type()

        if (due_date == "" or 
            status == "Damaged" or 
            status == "Ready" or
            sale_type == ""
            ):
            return [self.unit_number, "", status, ""]
        else:
            return [self.unit_number, due_date, status, sale_type]
    def generate_random_notes(self):
        num_bullet_points = random.randint(1, 5)
        notes = f"# {self.unit_number}\n\n" + "--------------------\n\n" +  "- " + "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt. " * random.randint(1, 3)
        for _ in range(num_bullet_points):
            notes += "\n- " + "lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. " * random.randint(1, 3)
        return notes
    def write_to_dict(self):
        # Write the random values to a dictionary where the key is the unit number
        data = {}
        for i in range(self.number_of_values):
            random_values = self.generate_random_values()
            data[random_values[0]] = {
                "due_date": random_values[1],
                "status": random_values[2],
                "sale_type": random_values[3],
                "notes": self.generate_random_notes()
            }
        with open ('random_data.py', 'w') as f:
            f.write('random_data = ' + pprint.pformat(data))

# Test the random value generation
if __name__ == "__main__":
    RandomValues(200).write_to_dict()