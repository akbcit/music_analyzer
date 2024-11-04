
def nested_structure_type(data):
    if not isinstance(data, (dict, list)):
        return "none"
    elif isinstance(data, dict):
        return "dict"
    elif isinstance(data, list):
        return "list"


def flatten(element, parent_key, accumulator, separator="_"):
    element_type = nested_structure_type(element)  # Determine if element is a dict or list (assumed function)
    if element_type == "dict":
        # Loop through each key-value pair in the dictionary
        for key, value in element.items():
            # Create a new key by combining the parent key and current key
            composite_key = f"{parent_key}{separator}{key}" if parent_key else key  # Avoids starting with a separator
            # Recursively flatten if value is a nested structure, otherwise store the value
            flatten(value, composite_key, accumulator, separator)
    elif element_type == "list":
        # Handle lists by indexing each element
        for index, item in enumerate(element):
            composite_key = f"{parent_key}{separator}{index}" if parent_key else str(index)
            flatten(item, composite_key, accumulator, separator)
    else:
        # If it's a base type (e.g., int, str), add to the accumulator dictionary
        accumulator[parent_key] = element



