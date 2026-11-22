from ....Functions_new.utils.geometry import comp_flower_arc
from ....Classes_new.geometry.arc_1 import Arc1
from ....classes_common.errors import ParentMissingError
import numpy as np


def get_bore_line(self, label=None) -> list:
    """Return the bore line description

    Parameters
    ----------
    self : BoreUD
        A BoreUD object

    Returns
    -------
    bore_list : list
        List of bore lines
    """

    if label is not None:
        for line in self.line_list:
            line.label = label

    return self.line_list
