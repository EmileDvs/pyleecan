# -*- coding: utf-8 -*-
from ....Classes_new.geometry.arc_3 import Arc3


def get_lines(self):
    """Get the lines needed to draw the surface (2 Arc3)

    Parameters
    ----------
    self : Circle
        A circle Object

    Returns
    -------
    line_list: list
        Two arcs to draw the circle

    """
    # check if the circle is correct
    self.check()
    begin = self.center + self.radius
    end = self.center - self.radius
    # first half-circle
    line1 = Arc3(begin=begin, end=end, is_trigo_direction=True, prop_dict=self.prop_dict)
    # second half-circle
    line2 = Arc3(begin=end, end=begin, is_trigo_direction=True, prop_dict=self.prop_dict)
    return [line1, line2]
