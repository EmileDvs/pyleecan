from ....classes_common.errors import ParentMissingError


def get_Rbo(self) -> float:
    """Return the parent lamination bore radius

    Parameters
    ----------
    self : Hole
        A Hole object

    Returns
    -------
    Rbo: float
        The parent lamination bore radius [m]

    """

    if self.parent is not None:
        return self.parent.get_Rbo()
    else:
        raise ParentMissingError("Error: The hole is not inside a Lamination")
