# File generated according to Generator/ClassesRef/Elmer/Section.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Elmer/Section"""

from io import StringIO
from os import linesep
from sys import getsizeof

from pyleecan.Classes.Elmer import Elmer
from pyleecan.Classes.SolverInputFile import INDENT
from pyleecan.Classes._check import check_var

from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class Section(Elmer):
    """Class to setup a section of an Elmer Solver Input File"""

    VERSION = 1

    # cf Methods.Elmer.Section.__delitem__
    # -*- coding: utf-8 -*-
    def __delitem__(self, key):
        """Called to implement deletion of self[key]."""
        self._statements.__delitem__(key)
        self._comments.__delitem__(key)

    # cf Methods.Elmer.Section.__getitem__
    def __getitem__(self, idx):
        """Method to behave like a dict and get the value (and comment as a tuple)"""
        value = self._statements.__getitem__(idx)
        comment = self._comments.__getitem__(idx)
        return (value, comment)

    # cf Methods.Elmer.Section.__iter__
    def __iter__(self):
        """Method to behave like a dict and iterate the keys"""
        return self._statements.__iter__()

    # cf Methods.Elmer.Section.__len__
    def __len__(self):
        """Method to behave like a dict and the number of keys"""
        return self._statements.__len__()

    # cf Methods.Elmer.Section.__missing__
    def __missing__(self, key):
        """method to implement self[key] for dict subclasses when key is not in the dict."""
        return self._statements.__missing__(key)

    # cf Methods.Elmer.Section.__reversed__
    def __reversed__(self):
        """Built-in to implement reverse iteration"""
        return self._statements.__reversed__()

    # cf Methods.Elmer.Section.__setitem__
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

    # cf Methods.Elmer.Section.keys
    def keys(self):
        """Return keys to behave like a dict"""
        return self._statements.keys()

    # cf Methods.Elmer.Section.pop
    def pop(self, key):
        """
        Remove the item with the given key and return it.
        """
        if key not in self.keys():
            raise ElmerSectionError("Key doesn't exist.")

        value = self._statements.pop(key)
        comment = self._comments.pop(key)

        return (value, comment)

    # cf Methods.Elmer.Section.write
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        section="",
        id=None,
        comment="",
        _statements=-1,
        _comments=-1,
        logger_name="Pyleecan.Elmer",
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "section" in list(init_dict.keys()):
                section = init_dict["section"]
            if "id" in list(init_dict.keys()):
                id = init_dict["id"]
            if "comment" in list(init_dict.keys()):
                comment = init_dict["comment"]
            if "_statements" in list(init_dict.keys()):
                _statements = init_dict["_statements"]
            if "_comments" in list(init_dict.keys()):
                _comments = init_dict["_comments"]
            if "logger_name" in list(init_dict.keys()):
                logger_name = init_dict["logger_name"]
        # Set the properties (value check and convertion are done in setter)
        self.section = section
        self.id = id
        self.comment = comment
        self._statements = _statements
        self._comments = _comments
        # Call Elmer init
        super(Section, self).__init__(logger_name=logger_name)
        # The class is frozen (in Elmer init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Section_str = ""
        # Get the properties inherited from Elmer
        Section_str += super(Section, self).__str__()
        Section_str += 'section = "' + str(self.section) + '"' + linesep
        Section_str += "id = " + str(self.id) + linesep
        Section_str += 'comment = "' + str(self.comment) + '"' + linesep
        Section_str += "_statements = " + str(self._statements) + linesep
        Section_str += "_comments = " + str(self._comments) + linesep
        return Section_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Elmer
        if not super(Section, self).__eq__(other):
            return False
        if other.section != self.section:
            return False
        if other.id != self.id:
            return False
        if other.comment != self.comment:
            return False
        if other._statements != self._statements:
            return False
        if other._comments != self._comments:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Elmer
        diff_list.extend(
            super(Section, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if other._section != self._section:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._section)
                    + ", other="
                    + str(other._section)
                    + ")"
                )
                diff_list.append(name + ".section" + val_str)
            else:
                diff_list.append(name + ".section")
        if other._id != self._id:
            if is_add_value:
                val_str = " (self=" + str(self._id) + ", other=" + str(other._id) + ")"
                diff_list.append(name + ".id" + val_str)
            else:
                diff_list.append(name + ".id")
        if other._comment != self._comment:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._comment)
                    + ", other="
                    + str(other._comment)
                    + ")"
                )
                diff_list.append(name + ".comment" + val_str)
            else:
                diff_list.append(name + ".comment")
        if other.__statements != self.__statements:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self.__statements)
                    + ", other="
                    + str(other.__statements)
                    + ")"
                )
                diff_list.append(name + "._statements" + val_str)
            else:
                diff_list.append(name + "._statements")
        if other.__comments != self.__comments:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self.__comments)
                    + ", other="
                    + str(other.__comments)
                    + ")"
                )
                diff_list.append(name + "._comments" + val_str)
            else:
                diff_list.append(name + "._comments")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Elmer
        S += super(Section, self).__sizeof__()
        S += getsizeof(self.section)
        S += getsizeof(self.id)
        S += getsizeof(self.comment)
        if self._statements is not None:
            for key, value in self._statements.items():
                S += getsizeof(value) + getsizeof(key)
        if self._comments is not None:
            for key, value in self._comments.items():
                S += getsizeof(value) + getsizeof(key)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from Elmer
        Section_dict = super(Section, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        Section_dict["section"] = self.section
        Section_dict["id"] = self.id
        Section_dict["comment"] = self.comment
        Section_dict["_statements"] = (
            self._statements.copy() if self._statements is not None else None
        )
        Section_dict["_comments"] = (
            self._comments.copy() if self._comments is not None else None
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        Section_dict["__class__"] = "Section"
        return Section_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        section_val = self.section
        id_val = self.id
        comment_val = self.comment
        if self._statements is None:
            _statements_val = None
        else:
            _statements_val = self._statements.copy()
        if self._comments is None:
            _comments_val = None
        else:
            _comments_val = self._comments.copy()
        logger_name_val = self.logger_name
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            section=section_val,
            id=id_val,
            comment=comment_val,
            _statements=_statements_val,
            _comments=_comments_val,
            logger_name=logger_name_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.section = None
        self.id = None
        self.comment = None
        self._statements = None
        self._comments = None
        # Set to None the properties inherited from Elmer
        super(Section, self)._set_None()

    def _get_section(self):
        """getter of section"""
        return self._section

    def _set_section(self, value):
        """setter of section"""
        check_var("section", value, "str")
        self._section = value

    section = property(
        fget=_get_section,
        fset=_set_section,
        doc="""Name of the section

        :Type: str
        """,
    )

    def _get_id(self):
        """getter of id"""
        return self._id

    def _set_id(self, value):
        """setter of id"""
        check_var("id", value, "int")
        self._id = value

    id = property(
        fget=_get_id,
        fset=_set_id,
        doc="""Index of a numbered section

        :Type: int
        """,
    )

    def _get_comment(self):
        """getter of comment"""
        return self._comment

    def _set_comment(self, value):
        """setter of comment"""
        check_var("comment", value, "str")
        self._comment = value

    comment = property(
        fget=_get_comment,
        fset=_set_comment,
        doc="""Section global comment

        :Type: str
        """,
    )

    def _get__statements(self):
        """getter of _statements"""
        return self.__statements

    def _set__statements(self, value):
        """setter of _statements"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("_statements", value, "dict")
        self.__statements = value

    _statements = property(
        fget=_get__statements,
        fset=_set__statements,
        doc="""internal dict to store the sections statements

        :Type: dict
        """,
    )

    def _get__comments(self):
        """getter of _comments"""
        return self.__comments

    def _set__comments(self, value):
        """setter of _comments"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("_comments", value, "dict")
        self.__comments = value

    _comments = property(
        fget=_get__comments,
        fset=_set__comments,
        doc="""internal dict to store comments on single statements

        :Type: dict
        """,
    )

    class ElmerSectionError(Exception):
        pass


ElmerSectionError = Section.ElmerSectionError


class File(str):
    pass


class Variable:

    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value


class MATC:

    def __init__(self, expr=None):
        self.expr = expr
