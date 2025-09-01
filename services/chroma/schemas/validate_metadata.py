"""Validate a metadata dict against one of the collection schemas.

Usage:
    from services.chroma.schemas.validate_metadata import validate
    validate('events', metadata_dict)
"""
import json
import os
from jsonschema import Draft7Validator, ValidationError

SCHEMA_DIR = os.path.join(os.path.dirname(__file__))

_SCHEMAS = {}

def _load_schema(name: str):
    if name in _SCHEMAS:
        return _SCHEMAS[name]
    path = os.path.join(SCHEMA_DIR, f"{name}.schema.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Schema not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    _SCHEMAS[name] = schema
    return schema

def validate(collection: str, payload: dict):
    """Validate the payload against the named collection schema.

    Raises jsonschema.ValidationError on failure.
    """
    schema = _load_schema(collection)
    try:
        Draft7Validator(schema).validate(payload)
    except ValidationError:
        raise

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Validate metadata file against schema')
    parser.add_argument('collection', choices=['events','characters','snippets','documents'])
    parser.add_argument('file', help='JSON file containing the payload to validate')
    args = parser.parse_args()
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}")
        print("Provide a path to a JSON file containing a payload in the form: {\"id\":..., \"text\":..., \"metadata\":{...}}")
        raise SystemExit(2)

    try:
        validate(args.collection, payload)
        print('VALID')
    except ValidationError as e:
        print('INVALID')
        print(e)
        raise SystemExit(2)
