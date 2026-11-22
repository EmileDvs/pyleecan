from ....classes_common.errors import ParentMissingError


def get_name_lam(self) -> str:
    """Return the name of the parent lamination

    Parameters
    ----------
    self : Slot
        A Slot object

    Returns
    -------
    name: string
        The name of the parent lamination

    """

    if self.parent is not None:
        return self.parent.get_label()
    else:
        return "NoLam"
