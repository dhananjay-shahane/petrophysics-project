import csv

class Item:
    def __init__(self, name, category, scale, unit, left_limit, right_limit, description):
        if scale not in ['Linear', 'Logarithmic']:
            raise ValueError("Scale must be either 'ABC' or 'XYZ'.")
        self.name = name
        self.category = category
        self.scale = scale  # Scale must be 'ABC' or 'XYZ'
        self.unit = unit
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.description = description

    def __str__(self):
        return (f"Item(name='{self.name}', category='{self.category}', scale='{self.scale}', "
                f"unit='{self.unit}', left_limit={self.left_limit}, right_limit={self.right_limit}, "
                f"description='{self.description}')")

class ItemCollection:
    def __init__(self, filename=None):
        self.items = []  # List to store Item objects
        self.filename = filename  # Store filename for saving later
        if self.filename:
            self.load_from_csv(filename)

    def add_item(self, item):
        """Add an Item object to the collection."""
        self.items.append(item)
        #print(f'Item "{item.name}" added to the collection.')
        #self.save_to_csv(self.filename)  # Save changes after adding
        
    def get_attribute_by_item_name(self, name, attribute):
        """Get a specific attribute of the item given its name."""
        for item in self.items:
            if item.name == name:
                if hasattr(item, attribute):
                    return getattr(item, attribute)
                else:
                    print(f'Attribute "{attribute}" not found in item "{name}".')
                    return None
        print(f'Item "{name}" not found in the collection.')
        return None

    def remove_item(self, name):
        """Remove an Item from the collection by name."""
        for item in self.items:
            if item.name == name:
                self.items.remove(item)
                print(f'Item "{name}" removed from the collection.')
                self.save_to_csv(self.filename)  # Save changes after removing
                return
        print(f'Item "{name}" not found in the collection.')

    def create_and_add_item_with_prompt(self):
        """Prompt the user to create an Item and add it to the collection."""
        name = input("Enter item name: ")
        category = input("Enter item category: ")
        scale = input("Enter item scale (ABC or XYZ): ")
        while scale not in ['Linear', 'Logarithmic']:
            print("Invalid input. Scale must be either 'ABC' or 'XYZ'.")
            scale = input("Enter item scale (ABC or XYZ): ")
        unit = input("Enter item unit: ")
        left_limit = float(input("Enter left limit: "))
        right_limit = float(input("Enter right limit: "))
        description = input("Enter item description: ")

        item = Item(
            name=name,
            category=category,
            scale=scale,
            unit=unit,
            left_limit=left_limit,
            right_limit=right_limit,
            description=description
        )
        self.add_item(item)
    def create_and_add_item(self, name, category, scale, unit, left_limit, right_limit, description):
        """Create an Item object and add it to the collection without user prompt."""
        if scale not in ['Linear', 'Logarithmic']:
            raise ValueError("Scale must be either 'ABC' or 'XYZ'.")

        item = Item(
            name=name,
            category=category,
            scale=scale,
            unit=unit,
            left_limit=left_limit,
            right_limit=right_limit,
            description=description
        )
        self.add_item(item)
        self.save_to_csv(self.filename)
    def find_item(self, name):
        """Find an Item in the collection by name."""
        for item in self.items:
            if item.name == name:
                return item
        print(f'Item "{name}" not found in the collection.')
        return None

    def list_items(self):
        """List all items in the collection."""
        if not self.items:
            print("No items in the collection.")
        else:
            for item in self.items:
                print(item)

    def save_to_csv(self, filename):
        """Save the item collection to a CSV file."""
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(['Name', 'Category', 'Scale', 'Unit', 'Left Limit', 'Right Limit', 'Description'])
            # Write item data
            for item in self.items:
                writer.writerow([
                    item.name,
                    item.category,
                    item.scale,
                    item.unit,
                    item.left_limit,
                    item.right_limit,
                    item.description
                ])
        print(f'Data saved to {self.filename}.')

    def load_from_csv(self, filename):
        """Load items from a CSV file into the collection."""
        try:
            with open(filename, mode='r') as file:
                reader = csv.reader(file)
                try:
                    next(reader)  # Skip the header
                except StopIteration:
                    print("The file is empty or does not have a header.")
                    return

                for row in reader:
                    if len(row) == 7:  # Ensure there are exactly 7 columns
                        name, category, scale, unit, left_limit, right_limit, description = row
                        if scale not in ['Linear', 'Logarithmic']:
                            print(f"Invalid scale '{scale}' in row, skipping.")
                            continue  # Skip this row if the scale is invalid
                        item = Item(
                            name=name,
                            category=category,
                            scale=scale,
                            unit=unit,
                            left_limit=float(left_limit),
                            right_limit=float(right_limit),
                            description=description
                        )
                        self.add_item(item)
                    else:
                        print("Row with incorrect number of columns found and skipped:", row)
            print(f'Data loaded from {filename}.')
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except Exception as e:
            print(f"An error occurred while loading from CSV: {e}")