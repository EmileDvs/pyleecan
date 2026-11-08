from importlib import import_module

from ...Classes._check import InitUnKnowClassError


def import_class(mod_name, class_name, prop_name="", *, module_name=None):
    """Dynamically import a class, optionally specifying its module name."""

    try:
        module = import_module(
            mod_name + "." + (class_name if module_name is None else module_name)
        )
        return getattr(module, class_name)
    except Exception:
        if prop_name != "":
            raise InitUnKnowClassError(
                "Unknow class name "
                + class_name
                + " in init_dict for property "
                + prop_name
            )
        else:
            raise InitUnKnowClassError(
                "Unknow class name " + class_name + " when loading"
            )
