# Experimental dataclass generated from Generator/ClassesRef/Elmer/Section.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from io import StringIO
from typing import Any

from .elmer import Elmer
from .solver_input_file import INDENT


@dataclass(eq=False)
class Section(Elmer):
    """Class to setup a section of an Elmer Solver Input File

    Attributes
    ----------
    section : str or None
        Name of the section
        Default: None
    id : int or None
        Index of a numbered section
        Default: None
    comment : str or None
        Section global comment
        Default: None
    _statements : dict or None
        internal dict to store the sections statements
        Default: {}
    _comments : dict or None
        internal dict to store comments on single statements
        Default: {}
    """

    section: str | None = None
    """Name of the section"""
    id: int | None = None
    """Index of a numbered section"""
    comment: str | None = None
    """Section global comment"""
    _statements: dict[str, Any] | None = field(default_factory=dict)
    """internal dict to store the sections statements"""
    _comments: dict[str, Any] | None = field(default_factory=dict)
    """internal dict to store comments on single statements"""

    # Inlined from Methods.Elmer.Section.__delitem__
    # -*- coding: utf-8 -*-
    def __delitem__(self, key):
        """Called to implement deletion of self[key]."""
        self._statements.__delitem__(key)
        self._comments.__delitem__(key)

    # Inlined from Methods.Elmer.Section.__getitem__
    def __getitem__(self, idx):
        """Method to behave like a dict and get the value (and comment as a tuple)"""
        value = self._statements.__getitem__(idx)
        comment = self._comments.__getitem__(idx)
        return (value, comment)

    # Inlined from Methods.Elmer.Section.__iter__
    def __iter__(self):
        """Method to behave like a dict and iterate the keys"""
        return self._statements.__iter__()

    # Inlined from Methods.Elmer.Section.__len__
    def __len__(self):
        """Method to behave like a dict and the number of keys"""
        return self._statements.__len__()

    # Inlined from Methods.Elmer.Section.__missing__
    def __missing__(self, key):
        """method to implement self[key] for dict subclasses when key is not in the dict."""
        return self._statements.__missing__(key)

    # Inlined from Methods.Elmer.Section.__reversed__
    def __reversed__(self):
        """Built-in to implement reverse iteration"""
        return self._statements.__reversed__()

    # Inlined from Methods.Elmer.Section.__setitem__
    def __setitem__(self, key, value):
        """Called to implement assignment to self[key]."""
        if isinstance(value, tuple):
            self._statements.__setitem__(key, value[0])
            if len(tuple) >= 1:
                self._comments.__setitem__(key, value[1])
            else:
                self._comments.__setitem__(key, None)
        else:
            self._statements.__setitem__(key, value)
            self._comments.__setitem__(key, None)

    # Inlined from Methods.Elmer.Section.keys
    def keys(self):
        """Return keys to behave like a dict"""
        return self._statements.keys()

    # Inlined from Methods.Elmer.Section.pop
    def pop(self, key):
        """
        Remove the item with the given key and return it.
        """
        if key not in self.keys():
            raise self.ElmerSectionError("Key doesn't exist.")

        value = self._statements.pop(key)
        comment = self._comments.pop(key)

        return (value, comment)

    # Inlined from Methods.Elmer.Section.write
    def write(self, stream=None, *, NEWLINE="\n", END="End"):
        """Write the Elmer SIF section to a stream. If no stream is given, the method
        will return a StringIO.
        """
        if not stream:
            stream = StringIO()

        # if section has an 'id' write a numbered sections
        if self.id:
            nbr = str(self.id)
        else:
            nbr = ""

        # write section header
        stream.write(NEWLINE)
        if self.comment:
            stream.write("! " + self.comment)
            stream.write(NEWLINE)
        stream.write(self.section + " " + nbr)

        # write section entries
        for key in self.keys():
            n = ""
            value, comment = self[key]
            if isinstance(value, list) and len(value) > 1:
                n = "(" + str(len(value)) + ")"
            stream.write(NEWLINE + INDENT)
            stream.write(key + n + " = " + self._convert(value))
            if comment:
                stream.write(INDENT + "! " + comment)

        # end section
        stream.write(NEWLINE + END + NEWLINE)

        return stream

    @staticmethod
    def _convert(value, get_type=True):
        """internal method to convert the data corresponding to Elmer SIF needs"""
        if isinstance(value, File):  # check before str due to inheretance
            return "File " * get_type + f'"{value}"'

        if isinstance(value, str):
            return "String " * get_type + f'"{value}"'

        if isinstance(value, float):
            return "Real " * get_type + f"{value}"

        if isinstance(value, bool):
            return "Logical " * get_type + f"{value}"

        if isinstance(value, int):
            return "Integer " * get_type + f"{value}"

        if isinstance(value, list):
            val_str = ""
            for idx, val in enumerate(value):
                get_type = True if idx == 0 else False
                val_str += Section._convert(val, get_type=get_type) + " "
            return val_str

        if isinstance(value, Variable):
            return (
                "Variable "
                + value.name
                + NEWLINE
                + 2 * INDENT
                + Section._convert(value.value)
            )

        if isinstance(value, MATC):
            return f'Real MATC "{value.expr}"'

    class ElmerSectionError(Exception):
        pass
