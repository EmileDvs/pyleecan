from warnings import warn


def getattr_recursive(obj, attr_list: list):
    """
    Function to recursively get an attribute.

    Parameters
    ----------
    obj : object
        An object

    attr_list: list
        A list of strings that is the attribute 'tree'

    Returns
    -------
    attr: attribute
        An attribute

    """

    warn(
        "getattr_recursive is deprecated, it is not used by pyleecan (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    if len(attr_list) > 1:
        return getattr_recursive(getattr(obj, attr_list[0]), attr_list[1:])
    else:
        return getattr(obj, attr_list[0])
