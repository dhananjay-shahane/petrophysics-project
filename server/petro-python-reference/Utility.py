from fe_data_objects import *
def find_item_by_name(item_list, item_name):
    # Use a list comprehension to find the item by name
    found_items = [item for item in item_list if item.well_name == item_name]
    return found_items[0] if found_items else None
def generate_unique_name(existing_names, base_name):
        """Generate a unique name based on the existing names."""
        final_name = base_name
        count = 1
        
        # Create a set for fast lookup of existing names
        existing_name_set = set(existing_names)
        
        # Incrementally create a new name until it's unique
        while final_name in existing_name_set:
            final_name = f"{base_name}_{count}"
            count += 1
            
        return final_name
def find_constant_by_name(obj:Dataset, name:str):
   return next((const for const in obj.constants if isinstance(const, Constant) and const.name == name), None)
def find_dataset_by_name(obj:Well, name:str):
   return next((dtst for dtst in obj.datasets if isinstance(dtst, Dataset) and dtst.name == name), None)
def find_well_by_name(obj:List[Well], name:str):
   return next((w for w in obj if isinstance(w, Well) and w.well_name == name), None)