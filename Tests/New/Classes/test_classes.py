from collections.abc import Mapping

import pytest
from cloudpickle import dumps
from pydantic import ValidationError

from pyleecan.Classes_new._check import CheckMaxError, CheckMinError, CheckTypeError
from pyleecan.Classes_new._class_info import PYLEECAN_BASES
from pyleecan.Classes_new._error import InitUnKnowClassError
from pyleecan.Classes_new._import import import_class
from pyleecan.definitions import DOC_DIR
from pyleecan.Functions_new.Load.retrocompatibility import NORMALIZATION_CLASS_NAMES
from pyleecan.Generator import PYTHON_TYPE
from pyleecan.Generator.ClassGenerator.init_method_generator import get_mother_attr
from pyleecan.Generator.read_fct import read_all
from Tests.find import find_test_value, is_type_dict, is_type_list

# Get the dict of all the classes and their information
gen_dict = read_all(DOC_DIR)  # dict of class dict
# Remove one list level (packages Machine, Simulation, Material...)
class_list = list(gen_dict.values())
# The classes are resolved by their CSV name (import_class accepts the legacy
# names of the renamed classes, e.g. Norm_ref -> NormRef)



class _ClassNamespace(Mapping):
    """Pyleecan classes by name, to evaluate the CSV default values (e.g. "Segment()")"""

    def __getitem__(self, name):
        try:
            return import_class(name)
        except InitUnKnowClassError:
            raise KeyError(name) from None

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0


CLASSES = _ClassNamespace()

# Errors raised by an invalid value: legacy check errors (dataclasses) or
# pydantic ValidationError (classes of the PYDANTIC_PACKAGES)
TYPE_ERRORS = (CheckTypeError, ValidationError)
MIN_ERRORS = (CheckMinError, ValidationError)
MAX_ERRORS = (CheckMaxError, ValidationError)

"""
This test check that all the classes matches the current documentation
It makes sure that the class generator works and was run
"""


@pytest.mark.parametrize("class_dict", class_list)
def test_class_as_dict(class_dict):
    """Check if as_dict return the correct dict"""
    # Setup
    d = dict()
    prop_list = get_mother_attr(gen_dict, class_dict, "properties")[0]
    # Generated the expected result dict
    for prop in prop_list:
        if prop["type"] == "ndarray":
            if prop["value"] == "":
                d[prop["name"]] = None
            else:
                d[prop["name"]] = prop["value"]
        elif prop["value"] in ["None", None]:
            d[prop["name"]] = None
        elif type(prop["value"]) is str and "()" in prop["value"]:
            d[prop["name"]] = eval(prop["value"] + ".as_dict()", globals(), CLASSES)
        elif prop["type"] == "complex":
            d[prop["name"]] = str(prop["value"])
        elif prop["type"] == "dict":
            if prop["value"] == "":
                d[prop["name"]] = {}
            else:
                d[prop["name"]] = prop["value"]
        elif prop["type"] == "list":
            if prop["value"] in ["", -1]:
                d[prop["name"]] = []
            else:
                d[prop["name"]] = prop["value"]
        elif prop["type"] in PYTHON_TYPE:  # PYTHON_TYPE and not dict or list
            d[prop["name"]] = prop["value"]
        elif "." in prop["type"]:  # Imported type or list of imported type
            val = eval(prop["value"], globals(), CLASSES)
            d[prop["name"]] = {
                "__class__": str(type(val)),
                "__repr__": str(val.__repr__()),
                "serialized": dumps(val).decode("ISO-8859-2"),
            }
        elif is_type_list(prop["type"]):  # List of pyleecan type
            d[prop["name"]] = list()
        elif is_type_dict(prop["type"]):  # Dict of pyleecan type
            d[prop["name"]] = dict()
        else:  # pyleecan type
            d[prop["name"]] = import_class(prop["type"])().as_dict()
    # Accepted difference: the normalization classes are renamed (Norm_ref ->
    # NormRef...), the legacy names are still accepted when loading
    d["__class__"] = NORMALIZATION_CLASS_NAMES.get(class_dict["name"], class_dict["name"])

    test_obj = import_class(class_dict["name"])()
    # Test
    try:
        result_dict = test_obj.as_dict(type_handle_ndarray=0, keep_function=False)
    except Exception as e:
        raise Exception(
            "Error while calling as_dict for " + class_dict["name"] + ":\n" + str(e)
        )
    for key in result_dict:
        assert d[key] == result_dict[key], (
            "Error for class "
            + class_dict["name"]
            + " for property: "
            + key
            + ", expected: "
            + str(d[key])
            + ", returned: "
            + str(result_dict[key]),
        )
    assert d.keys() == result_dict.keys(), (
        "Wrong as_dict keys for class "
        + class_dict["name"]
        + " returned "
        + str(result_dict.keys())
        + " expected "
        + str(d.keys())
    )


@pytest.mark.parametrize("class_dict", class_list)
def test_class_set_None(class_dict):
    """Check that _set_None set to None every non pyleecantype properties"""

    test_obj = import_class(class_dict["name"])()
    test_obj._set_None()
    prop_list = get_mother_attr(gen_dict, class_dict, "properties")[0]
    for prop in prop_list:
        # ndarray set as None are set as array([])
        if prop["type"] in PYTHON_TYPE or prop["type"] == "ndarray":
            assert test_obj.__getattribute__(prop["name"]) == None


@pytest.mark.parametrize("class_dict", class_list)
def test_class_inherit(class_dict):
    """Check if the class inherit of its mother class"""
    if class_dict["mother"] != "":
        assert (
            issubclass(import_class(class_dict["name"]), import_class(class_dict["mother"]))
            == True
        )
    else:
        assert issubclass(import_class(class_dict["name"]), PYLEECAN_BASES) == True


@pytest.mark.parametrize("class_dict", class_list)
def test_class_methods(class_dict):
    """Check if the class has all its methods"""
    test_obj = import_class(class_dict["name"])()

    meth_list = get_mother_attr(gen_dict, class_dict, "methods")[0]
    for meth in meth_list:
        meth = meth.split(".")[-1]  # Get the methods name if in a folder

        # Check if the method exists, shouldn't be raised because of the class generator
        assert hasattr(import_class(class_dict["name"]), meth) == True, (
            class_dict["name"] + " has no method: " + meth
        )

        meth_obj = getattr(import_class(class_dict["name"]), meth)
        assert not isinstance(meth_obj, property), meth_obj.fget("")


@pytest.mark.parametrize("class_dict", class_list)
def test_class_type_float(class_dict):
    """Check if the setter is type sensitive for float"""
    test_obj = import_class(class_dict["name"])()

    prop_list = get_mother_attr(gen_dict, class_dict, "properties")[0]
    for prop in prop_list:
        value = find_test_value(prop, "float")
        msg = "Error for class " + class_dict["name"] + " with " + prop["name"]
        # Check the doc to know if it should raise an error or not
        if prop["type"] in ["float", "complex", "", None]:
            # No error expected
            test_obj.__setattr__(prop["name"], value)

            assert test_obj.__getattribute__(prop["name"]) == value, msg
        elif (
            prop["type"] == "int"
            and prop["min"] not in ["", None]
            and prop["max"] not in ["", None]
            and prop["min"] == prop["max"]
        ):
            # Integer with only one value possible => find_test_value returns this value as float so it passes
            test_obj.__setattr__(prop["name"], value)
            assert test_obj.__getattribute__(prop["name"]) == value, msg
        else:
            # CheckTypeError expected
            with pytest.raises(TYPE_ERRORS):
                # print(msg + " value " + str(value) + " type " + str(type(value)))
                test_obj.__setattr__(prop["name"], value)


@pytest.mark.parametrize("class_dict", class_list)
def test_class_min(class_dict):
    """Check if the setter respect the specified min"""
    # Setup
    test_obj = import_class(class_dict["name"])()

    prop_list = get_mother_attr(gen_dict, class_dict, "properties")[0]
    for prop in prop_list:
        if prop["min"] != "" and prop["type"] in ["float", "int"]:
            min_val = eval(prop["type"] + "(" + str(prop["min"]) + ")")
            # Test Ok
            test_obj.__setattr__(prop["name"], min_val)
            assert test_obj.__getattribute__(prop["name"]) == min_val, (
                "Error for class "
                + class_dict["name"]
                + " for property: "
                + prop["name"]
            )

            # Test Fail
            with pytest.raises(MIN_ERRORS):
                test_obj.__setattr__(prop["name"], min_val - 1)


@pytest.mark.parametrize("class_dict", class_list)
def test_class_max(class_dict):
    """Check if the setter respect the specified max"""
    # Setup
    test_obj = import_class(class_dict["name"])()

    prop_list = get_mother_attr(gen_dict, class_dict, "properties")[0]
    for prop in prop_list:
        if prop["max"] != "" and prop["type"] in ["float", "int"]:
            max_val = eval(prop["type"] + "(" + str(prop["max"]) + ")")
            # Test Ok
            test_obj.__setattr__(prop["name"], max_val)
            assert test_obj.__getattribute__(prop["name"]) == max_val, (
                "Error for class "
                + class_dict["name"]
                + " for property: "
                + prop["name"]
            )

            # Test Fail
            with pytest.raises(MAX_ERRORS):
                test_obj.__setattr__(prop["name"], max_val + 1)


@pytest.mark.parametrize("class_dict", class_list)
def test_class_copy(class_dict):
    """Check if the copy method is correct"""

    test_obj = import_class(class_dict["name"])()
    result = test_obj.copy()
    assert test_obj == result


if __name__ == "__main__":
    # for class_dict0 in class_list:
    #     # test_class_as_dict(class_dict0)

    #     test_class_inherit(class_dict0)

    test_class_as_dict(class_list[116])

    # test_class_init_default(class_list[179])
