def get_data_with_key(key: str, data_dict: dict) -> dict:
    """Get data from a dictionary using a key."""
    return data_dict.get(key, None)


def get_data_with_keys(keys: list, data_dict: dict) -> dict:
    """Get data from a dictionary using a list of keys."""
    return {key: data_dict.get(key, None) for key in keys}


def create_data_getter(key: str) -> callable:
    """Create a function that gets data from a dictionary using a key."""
    return lambda data_dict: get_data_with_key(key, data_dict)
