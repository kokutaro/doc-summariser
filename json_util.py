import json
import logging
from jsonschema import validate, ValidationError


def check_json_format(json_str: str):
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
