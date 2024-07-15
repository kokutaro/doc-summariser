import json
import logging
from jsonschema import validate, ValidationError


def check_json_format(json_str: str):
    """Checks if the given JSON string is valid.

    Args:
        json_str (str): The JSON string to check.

    Returns:
        bool: True if the JSON string is valid, False otherwise.
    """
    try:
        json.loads(json_str)
        with open("summarised_doc.schema.json") as f:
            schema = json.load(f)
        validate(json.loads(json_str), schema)

        return True
    except json.JSONDecodeError:
        return False
    except ValidationError as e:
        logging.warn(e)
        return False
