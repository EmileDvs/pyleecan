"""Experimental dataclass-based Pyleecan classes."""

from json import load
from os.path import dirname, join

def get_class_dict():
    """Return the CSV-derived class generation dictionary."""
    path = join(dirname(__file__), "_class_dict.json")
    with open(path, encoding="utf-8") as class_dict_file:
        return load(class_dict_file)
