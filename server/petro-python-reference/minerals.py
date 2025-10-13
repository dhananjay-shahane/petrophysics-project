import pandas as pd
import os
import csv

class Mineral:
    def __init__(self, name):
        self.name = name
        self.properties = {}

    def add_property(self, key, value):
        """Add a property to the mineral."""
        if key in self.properties:
            raise ValueError(f"Property '{key}' already exists for mineral '{self.name}'.")
        self.properties[key] = value
        
    def to_dict(self):
        """Convert the mineral and its properties to a dictionary for CSV export."""
        return {"name": self.name, **self.properties}

    @classmethod
    def from_dict(cls, data):
        """Create a Mineral object from a dictionary."""
        mineral = cls(data['name'])
        for key, value in data.items():
            if key != 'name':
                mineral.add_property(key, value)
        return mineral

    def __repr__(self):
        return f"Mineral(name='{self.name}', properties={self.properties})"


class Minerals:
    def __init__(self):
        self.minerals = {}
        self.appFolder = os.path.dirname(os.path.abspath(__file__))
        self.folder = os.path.join(self.appFolder, 'Geological_Data')
        self.mineral_file_path = os.path.join(self.folder, 'minerals.csv')
        
        # Load minerals from CSV file upon initialization
        self.load_from_csv()
        
    def __repr__(self):
        return f"Minerals(minerals={list(self.minerals.values())})"
        
    def add_mineral(self, mineral):
        """Add a mineral to the collection, ensuring no duplicates."""
        if mineral.name in self.minerals:
            raise ValueError(f"Mineral '{mineral.name}' already exists in the collection.")
        self.minerals[mineral.name] = mineral
        
    def update_property(self, key, value):
        """Update an existing property of the mineral."""
        if key not in self.properties:
            raise ValueError(f"Property '{key}' does not exist for mineral '{self.name}'.")
        self.properties[key] = value
        
    def add_property_to_mineral(self, mineral_name, property_name, value):
        """Add a property to a specific mineral by name."""
        if mineral_name not in self.minerals:
            raise ValueError(f"Mineral '{mineral_name}' does not exist in the collection.")
        
        self.minerals[mineral_name].add_property(property_name, value)

    def save_to_csv(self):
        """Save the collection of minerals to a CSV file."""
        with open(self.mineral_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name'] + list(next(iter(self.minerals.values())).properties.keys()))
            writer.writeheader()
            for mineral in self.minerals.values():
                writer.writerow(mineral.to_dict())

    def load_from_csv(self):
        """Load minerals from a CSV file into the collection."""
        if not os.path.exists(self.mineral_file_path):
            print(f"CSV file not found at: {self.mineral_file_path}")
            return

        with open(self.mineral_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                mineral = Mineral.from_dict(row)
                self.add_mineral(mineral)

    def print_minerals(self):
        """Print a list of minerals and their properties."""
        if not self.minerals:
            print("No minerals in the collection.")
            return
        for mineral in self.minerals.values():
            print(f"Mineral: {mineral.name}")
            for key, value in mineral.properties.items():
                print(f"  {key}: {value}")
            print()  # Add a blank line for better readability


# Example usage:
if __name__ == "__main__":
    minerals_collection = Minerals()
    
    # Adding minerals (Example)
    quartz = Mineral("Quartz")
    calcite = Mineral("Calcite")
    
    try:
        minerals_collection.add_mineral(quartz)
        minerals_collection.add_mineral(calcite)

        # Adding properties to minerals
        minerals_collection.add_property_to_mineral('Quartz', 'GR', 90)
        minerals_collection.add_property_to_mineral('Calcite', 'RHOB', 2.71)

        # Print minerals to check added properties
        minerals_collection.print_minerals()

        # Save to CSV
        minerals_collection.save_to_csv()
    except ValueError as e:
        print(e)
