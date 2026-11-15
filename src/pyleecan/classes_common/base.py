"""Marker base of the Pyleecan class bases."""


class PyleecanBase:
    """Marker base of every Pyleecan class base (dataclass or pydantic model).

    It has no state and no behaviour: it lets the shared support code
    (``class_info``) recognize the Pyleecan classes without importing an
    implementation. A generated class is a subclass that defines its own
    ``_package`` class variable (name of the legacy package); the bases
    (``PyleecanClass``, ``PyleecanModel``...) do not.
    """

    __slots__ = ()


def is_generated_class(value):
    """True if value is a generated Pyleecan class (not one of the bases).

    Parameters
    ----------
    value : object
        Object to check

    Returns
    -------
    is_generated : bool
        True for a generated Pyleecan class
    """
    return (
        isinstance(value, type)
        and issubclass(value, PyleecanBase)
        and bool(vars(value).get("_package"))
    )
