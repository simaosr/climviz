# Create a function that returns a function that applies a prefix to an input string
def make_prefixer(prefix: str):  # type: ignore
    def prefixer(input_string: str) -> str:
        return prefix + input_string

    return prefixer


def make_page_id_func(page_name: str) -> callable:
    return make_prefixer(page_name + "-")


# Function to generate id from label
def make_id_from_label(label):
    return label.lower().replace(" ", "-")
