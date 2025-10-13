class KeyValueStore:
    def __init__(self, filename):
        self.filename = filename
        self.store = {}
        self.load_from_file(filename)

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().split()  # Split the right side into individual values
                    self.store[key] = value  # Store key with its associated values

    def get_values(self, key):
        """Retrieve the values for a given key."""
        return self.store.get(key, None)

    def add_key(self, key):
        """Add a key with no associated values."""
        if key not in self.store:
            self.store[key] = [key]  # Initialize with an empty list
            print(f'Key "{key}" added with no associated values.')
        else:
            print(f'Key "{key}" already exists.')
    def delete_key(self, key):
        """Delete a key and its associated values."""
        if key in self.store:
            del self.store[key]  # Remove the key from the store
            print(f'Key "{key}" and its associated values have been deleted.')
        else:
            print(f'Key "{key}" does not exist. No action taken.')

    def add_values_to_key(self, key, values):
        """Add values to an existing key, ensuring no duplicates."""
        if key in self.store:
            if isinstance(values, str):  # Check if values is a string
                value_list = values.split()  # Split the string into a list
                # Use a set to ensure uniqueness before adding
                unique_values = set(value_list) - set(self.store[key])  # Find new unique values
                self.store[key].extend(unique_values)  # Add unique values to the existing list
                print(f'Values {unique_values} added to key "{key}".')
            else:
                print('Values should be provided as a space-separated string.')
        else:
            print(f'Key "{key}" does not exist. Please add it first.')


    def update_file(self):
        """Update the text file with current keys and values."""
        with open(self.filename, 'w') as file:
            for key, values in self.store.items():
                file.write(f'{key} = {" ".join(values)}\n')  # Write key with associated values
        print(f'File "{self.filename}" updated with current keys and values.')

    def print_data(self):
        """Print the original data in a readable format."""
        for key, values in self.store.items():
            print(f'{key} = {" ".join(values)}')
    def get_key(self, value):
        """Retrieve the key associated with a given value."""
        for key, values in self.store.items():
            if value in values:
                return key
        return None
    
    def clear_store(self):
        """Clear all keys and values from the store."""
        self.store.clear()
        print('All keys and values have been cleared from the store.')

    def list_keys(self):
        """Return a list of all keys in the store."""
        return list(self.store.keys())

    def get_all_data(self):
        """Return all key-value pairs as a dictionary."""
        return self.store

    def contains_key(self, key):
        """Check if a specific key exists in the store."""
        exists = key in self.store
        print(f'Key "{key}" exists: {exists}')
        return exists

# Example usage
if __name__ == "__main__":
    kv_store = KeyValueStore('data.txt')  # Ensure this file has your original data
    
    # Print the original data
    print("Original Data:")
    kv_store.print_data()
    
    # Example to retrieve values for a key
    key_to_find = 'ABC'  # Change this to test different keys
    values = kv_store.get_values(key_to_find)
    
    if values is not None:
        print(f'The values for key "{key_to_find}" are: {values}.')
    else:
        print(f'Key "{key_to_find}" not found.')

    # Adding a key with no associated values
    kv_store.add_key('NEW_KEY')

    # Adding values to an existing key
    kv_store.add_values_to_key('NEW_KEY', ['VALUE1', 'VALUE2'])
    
    # Get key
    key = kv_store.get_key('BDFD')
    print('the key for ', 'BDFD is' , key)
    # Update the text file with the current state
    kv_store.update_file()
