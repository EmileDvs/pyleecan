from json import load
from os.path import dirname, join


def get_class_dict():
    """Function to get the Class Dict."""
    path = dirname(__file__)

    with open(join(path, "Class_Dict.json")) as class_dict_file:
        class_dict = load(class_dict_file)

    return class_dict


class NotImplementedYetError(Exception):
    """NotImplementedYetError"""


class ParentMissingError(Exception):
    """ParentMissingError"""
