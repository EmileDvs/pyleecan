"""Attribute docstrings generated from the CSV descriptions."""

import ast

import pytest

from pyleecan.Generator.ClassGenerator.New.class_generator import _attribute_docstring


@pytest.mark.parametrize(
    "description",
    [
        "Plain description",
        'Loss model for iron cores : "Bertotti" or "Steinmetz"',
        'Ends with a quote"',
        'Triple """ quote inside',
        "Single ' and double \" quotes",
        "Backslash \\mu and newline\nsecond line",
        "",
    ],
)
def test_attribute_docstring_round_trip(description):
    """The docstring is valid Python and evaluates to the description."""
    docstring = _attribute_docstring(description)
    assert ast.literal_eval(docstring) == description


def test_attribute_docstring_unchanged_without_quotes():
    """Descriptions without double quotes keep the previous output."""
    assert _attribute_docstring("Name of the loss") == '"""Name of the loss"""'
