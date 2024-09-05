#!python3
data_dict = {
    "EQC-111-222-333": {
        "due_date": "2024-06-01",
        "status": "active",
        "sale_type": "cash",
        "notes": [
            "First line of notes",
            "Second line of notes",
            "- Bullet point1",
            "- Bullet point2",
            "- Bullet point3",
        ],
    },
    "EQC-222-333-444": {
        "due_date": "2023-06-01",
        "status": "active",
        "sale_type": "net30",
        "notes": ["Call Jeff not Bob"],
    },
    "EQC-333-444-555": {
        "due_date": "2022-06-01",
        "status": "active",
        "sale_type": "net30",
        "notes": [],
    },
}


def parse_dict_to_table(data=data_dict):
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


# Example usage
if __name__ == "__main__":
    print(parse_dict_to_table())
