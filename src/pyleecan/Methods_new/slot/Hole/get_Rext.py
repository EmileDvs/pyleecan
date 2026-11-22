from ....classes_common.errors import ParentMissingError


def get_Rext(self) -> float:
    """Return the parent lamination exterior radius

    Parameters
    ----------
    self : Hole
        A Hole object

    Returns
    -------
    Rext: float
        The parent lamination exterior radius [m]

    """

    if self.parent is not None:
        return self.parent.Rext
    else:
        raise ParentMissingError("Error: The hole is not inside a Lamination")
