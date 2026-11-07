# Experimental dataclass generated from Generator/ClassesRef/Machine/Bore.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from . import ParentMissingError
from ..definitions import config_dict
from ..Functions.Geometry.cut_lines_between_angle import cut_lines_between_angles
from ..Functions.init_fig import init_fig
from ._pyleecan_class import PyleecanClass
from .lamination import Lamination
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class Bore(PyleecanClass):
    """Abstract class for Bore shape

    Attributes
    ----------
    type_merge_slot : int
        how to merge slot/notch into the bore radius (0: connect the dot, 1: intersection, 2: translate)
        Default: 1; Minimum: 0; Maximum: 2
    alpha : float
        Angular offset for the bore shape
        Unit: rad; Default: 0
    """

    ROTOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["ROTOR_COLOR"]
    STATOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["STATOR_COLOR"]
    type_merge_slot: int = 1
    """how to merge slot/notch into the bore radius (0: connect the dot, 1: intersection, 2: translate)"""
    alpha: float = 0
    """Angular offset for the bore shape"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Lamination,)):
            raise TypeError(
                "Bore parent must be an instance of Lamination, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Machine.Bore.comp_Rmax
    def comp_Rmax(self):
        """Compute the maximum radius of the Bore shape

        Parameters
        ----------
        self : Bore
            A Bore object

        Returns
        -------
        Rmax : float
            Maximum radius of the Bore shape [m]
        """

        line_list = self.get_bore_line()
        point_list = []

        for line in line_list:
            point_list.extend(line.discretize(100))

        return np.max(np.abs(np.array(point_list)))

    # Inlined from Methods.Machine.Bore.comp_Rmin
    def comp_Rmin(self):
        """Compute the minimum radius of the Bore shape

        Parameters
        ----------
        self : Bore
            A Bore object

        Returns
        -------
        Rmin : float
            Minimum radius of the Bore shape
        """

        line_list = self.get_bore_line()
        point_list = []

        for line in line_list:
            point_list.extend(line.discretize(100))

        return np.min(np.abs(np.array(point_list)))

    # Inlined from Methods.Machine.Bore.comp_surface
    def comp_surface(self):
        """Returns the area of the shape

        Parameters
        ----------
        self : Bore
            A Bore object

        Returns
        -------
        Sbore : float
            Area of the bore
        """

        return self.get_surface().comp_surface()

    # Inlined from Methods.Machine.Bore.get_surface
    def get_surface(self):
        """Returns the bore shape as a Surface object

        Parameters
        ----------
        self : Bore
            A Bore object

        Returns
        -------
        Sbore : Surface
            Surface object to draw the bore
        """

        line_list = self.get_bore_line()

        return SurfLine(line_list=line_list, point_ref=0, label="Bore")

    # Inlined from Methods.Machine.Bore.is_yoke
    def is_yoke(self):
        """Return if the Shape is for the Bore or Yoke radius

        Parameters
        ----------
        self : Bore
            A Bore object

        Returns
        -------
        is_yoke : bool
            True if the shape is on the yoke
        """

        if self.parent is not None:
            return self is self.parent.yoke
        else:
            raise ParentMissingError(
                "Error: The Bore object is not inside a Lamination"
            )

    # Inlined from Methods.Machine.Bore.merge_slot
    def merge_slot(self, radius_desc_list, prop_dict, sym):
        """Merge the Bore shape with notches/slot on the bore/yoke

        Parameters
        ----------
        radius_desc_list : list
            List of dict to describe the bore/yoke radius
        prop_dict : dict
            Property dictionary to apply on the radius lines (not on slot/notch)
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        line_list : list
            List of lines needed to draw the radius
        """
        if self.type_merge_slot == 0:
            return self.merge_slot_connect(
                radius_desc_list, prop_dict=prop_dict, sym=sym
            )
        if self.type_merge_slot == 1:
            return self.merge_slot_intersect(
                radius_desc_list, prop_dict=prop_dict, sym=sym
            )
        if self.type_merge_slot == 2:
            return self.merge_slot_translate(
                radius_desc_list, prop_dict=prop_dict, sym=sym
            )
        else:
            raise Exception("Not implemented yet")

    # Inlined from Methods.Machine.Bore.merge_slot_connect
    def merge_slot_connect(self, radius_desc_list, prop_dict, sym):
        """Merge the Bore shape with notches/slot on the bore/yoke
        Connect method: Add lines between radius and notch/slot
        (To use when the radius shape have circular part matchine the radius
        or when radius lines are bellow normal radius)

        Parameters
        ----------
        radius_desc_list : list
            List of dict to describe the bore/yoke radius
        prop_dict : dict
            Property dictionary to apply on the radius lines (not on slot/notch)
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        line_list : list
            List of lines needed to draw the radius
        """

        # Get all Radius lines (0 to 2*pi)
        radius_lines = self.get_bore_line()

        # Update begin and end angle if Radius (next step already cut lines)
        if sym != 1 and radius_desc_list[0]["label"] == "Radius":
            radius_desc_list[0]["begin_angle"] = 0
        if sym != 1 and radius_desc_list[-1]["label"] == "Radius":
            radius_desc_list[-1]["end_angle"] = 2 * np.pi / sym

        # Replace Arc radius from desc by lines from shape
        for desc_dict in radius_desc_list:
            if desc_dict["label"] == "Radius":
                desc_dict["lines"] = cut_lines_between_angles(
                    radius_lines, desc_dict["begin_angle"], desc_dict["end_angle"]
                )

        # If slot/notch are coliding with sym lines => Cut
        if sym != 1:
            # Cut first desc (if needed)
            if radius_desc_list[0]["begin_angle"] < 0:
                lines = []
                for line in radius_desc_list[0]["lines"]:
                    top_split_list, _ = line.split_line(0, 1)
                    lines.extend(top_split_list)
                radius_desc_list[0]["begin_angle"] = 0
                radius_desc_list[0]["lines"] = lines
            # Cut last desc (if needed)
            if radius_desc_list[-1]["end_angle"] > 2 * np.pi / sym:
                lines = []
                for line in radius_desc_list[-1]["lines"]:
                    _, bot_split_list = line.split_line(0, np.exp(1j * 2 * np.pi / sym))
                    lines.extend(bot_split_list)
                radius_desc_list[-1]["end_angle"] = 2 * np.pi / sym
                radius_desc_list[-1]["lines"] = lines

        # Apply merge strategy on slot/notch
        line_list = []
        for ii, desc_dict in enumerate(radius_desc_list):
            if desc_dict["label"] == "Radius":
                # Add prop_dict on all the Radius Lines
                if prop_dict is not None:
                    for line in desc_dict["lines"]:
                        if line.prop_dict is None:
                            line.prop_dict = {}
                        line.prop_dict.update(prop_dict)
                line_list.extend(desc_dict["lines"])
            else:  # Connect and add notch lines
                if len(line_list) > 0:
                    # Connect Radius to slot/notch by Segment (if needed)
                    if (
                        abs(line_list[-1].get_end() - desc_dict["lines"][0].get_begin())
                        > 1e-6
                    ):
                        line_list.append(
                            Segment(
                                line_list[-1].get_end(),
                                desc_dict["lines"][0].get_begin(),
                            )
                        )
                line_list.extend(desc_dict["lines"])
                # Connect slot/notch to next radius
                if (
                    abs(
                        radius_desc_list[ii + 1]["lines"][0].get_begin()
                        - desc_dict["lines"][-1].get_end()
                    )
                    > 1e-6
                ):
                    line_list.append(
                        Segment(
                            desc_dict["lines"][-1].get_end(),
                            radius_desc_list[ii + 1]["lines"][0].get_begin(),
                        )
                    )
        return line_list

    # Inlined from Methods.Machine.Bore.merge_slot_intersect
    def merge_slot_intersect(self, radius_desc_list, prop_dict, sym):
        """Merge the Bore shape with notches/slot on the bore/yoke
        Intersect method: cut lines of notch/slot to make the radius end match notch/slot begin
        technically reduice slot/notch height without changing yoke height

        Parameters
        ----------
        radius_desc_list : list
            List of dict to describe the bore/yoke radius
        prop_dict : dict
            Property dictionary to apply on the radius lines (not on slot/notch)
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        line_list : list
            List of lines needed to draw the radius
        """

        # Get all Radius lines (0 to 2*pi)
        radius_lines = self.get_bore_line()

        # Update begin and end angle if Radius (next step already cut lines)
        if sym != 1 and radius_desc_list[0]["label"] == "Radius":
            radius_desc_list[0]["begin_angle"] = 0
        if sym != 1 and radius_desc_list[-1]["label"] == "Radius":
            radius_desc_list[-1]["end_angle"] = 2 * np.pi / sym

        # Replace Arc radius from desc by lines from shape
        for ii, desc_dict in enumerate(radius_desc_list):
            if desc_dict["label"] == "Radius":
                desc_dict["lines"] = cut_lines_between_angles(
                    radius_lines, desc_dict["begin_angle"], desc_dict["end_angle"]
                )

        # # Check that the Radius lines are correct
        # for ii, desc_dict in enumerate(radius_desc_list):
        #     if desc_dict["label"] == "Radius":
        #         print(ii)
        #         print(
        #             str(desc_dict["begin_angle"])
        #             + " and "
        #             + str(angle(desc_dict["lines"][0].get_begin()) % (2 * pi))
        #         )
        #         print(
        #             str(desc_dict["end_angle"])
        #             + " and "
        #             + str(angle(desc_dict["lines"][-1].get_end()) % (2 * pi))
        #         )

        # If slot/notch are coliding with sym lines => Cut
        if sym != 1:
            # Cut first desc (if needed)
            if radius_desc_list[0]["begin_angle"] < 0:
                lines = []
                for line in radius_desc_list[0]["lines"]:
                    top_split_list, _ = line.split_line(0, 1)
                    lines.extend(top_split_list)
                radius_desc_list[0]["begin_angle"] = 0
                radius_desc_list[0]["lines"] = lines
            # Cut last desc (if needed)
            if radius_desc_list[-1]["end_angle"] > 2 * np.pi / sym:
                lines = []
                for line in radius_desc_list[-1]["lines"]:
                    _, bot_split_list = line.split_line(0, np.exp(1j * 2 * np.pi / sym))
                    lines.extend(bot_split_list)
                radius_desc_list[-1]["end_angle"] = 2 * np.pi / sym
                radius_desc_list[-1]["lines"] = lines

        # Apply merge strategy on slot/notch
        line_list = []
        for ii, desc_dict in enumerate(radius_desc_list):
            if desc_dict["label"] == "Radius":
                # Add prop_dict on all the Radius Lines
                if prop_dict is not None:
                    for line in desc_dict["lines"]:
                        if line.prop_dict is None:
                            line.prop_dict = {}
                        line.prop_dict.update(prop_dict)
                line_list.extend(desc_dict["lines"])
            else:  # Intersect and add slot/notch lines
                # Define First cutting line
                # rad_line = radius_desc_list[ii - 1]["lines"][-1]
                op = desc_dict["end_angle"] - desc_dict["begin_angle"]
                if not (ii == 0 and sym != 1):  # No first cut for first notch on Ox
                    rad_line_list = cut_lines_between_angles(
                        radius_lines,
                        desc_dict["begin_angle"] - op / 4,
                        desc_dict["begin_angle"] + op / 4,
                    )
                    # Find first line to intersect with cutting line
                    for jj in range(len(desc_dict["lines"])):
                        inter_list = desc_dict["lines"][jj].intersect_obj(
                            rad_line_list[-1], is_on_line=True
                        )
                        if len(inter_list) > 0:
                            break
                    if jj < len(desc_dict["lines"]) - 1:
                        # Slot/notch was cut => Replace lines by cut ones
                        desc_dict["lines"] = desc_dict["lines"][
                            jj:
                        ]  # Keep all lines after cut
                        # Update lines to start/end at cutting point
                        desc_dict["lines"][0].split_point(inter_list[0], is_begin=False)
                        if len(line_list) == 0:  # Slot/notch on Ox
                            radius_desc_list[-1]["lines"][-1].split_point(
                                inter_list[0], is_begin=True
                            )
                        else:
                            line_list[-1].split_point(inter_list[0], is_begin=True)
                    else:  # The slot is above the shape => Use shape lines
                        desc_dict["lines"] = cut_lines_between_angles(
                            radius_lines,
                            desc_dict["begin_angle"],
                            desc_dict["end_angle"],
                        )
                        # Add prop_dict on all the Radius Lines
                        if prop_dict is not None:
                            for line in desc_dict["lines"]:
                                if line.prop_dict is None:
                                    line.prop_dict = {}
                                line.prop_dict.update(prop_dict)
                        line_list.extend(desc_dict["lines"])
                        continue  # No need to cut the other side
                # Second cut
                if not (ii == len(radius_desc_list) - 1 and sym != 1):
                    # No second cut for notch on sym line
                    rad_line_list = cut_lines_between_angles(
                        radius_lines,
                        desc_dict["end_angle"] - op / 4,
                        desc_dict["end_angle"] + op / 4,
                    )
                    for jj in range(len(desc_dict["lines"])):
                        inter_list = desc_dict["lines"][-(jj + 1)].intersect_obj(
                            rad_line_list[0], is_on_line=True
                        )
                        if len(inter_list) > 0:
                            break
                    if jj < len(desc_dict["lines"]):
                        # Slot/notch was cut => Replace lines by cut ones
                        if jj != 0:  # Keep all the lines if last line is cut
                            desc_dict["lines"] = desc_dict["lines"][
                                :-jj
                            ]  # Keep all lines before cut
                        # Update lines to start/end at cutting point
                        desc_dict["lines"][-1].split_point(inter_list[0], is_begin=True)
                        radius_desc_list[ii + 1]["lines"][0].split_point(
                            inter_list[0], is_begin=False
                        )
                # Add slot/notch lines to final list
                line_list.extend(desc_dict["lines"])
        return line_list

    # Inlined from Methods.Machine.Bore.merge_slot_translate
    def merge_slot_translate(self, radius_desc_list, prop_dict, sym):
        """Merge the Bore shape with notches/slot on the bore/yoke
        Translate method: Translate lines of notch/slot to match the radius of the shape
        technically Keep the slot/notch height by reduicing the yoke height

        Parameters
        ----------
        radius_desc_list : list
            List of dict to describe the bore/yoke radius
        prop_dict : dict
            Property dictionary to apply on the radius lines (not on slot/notch)
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        line_list : list
            List of lines needed to draw the radius
        """

        raise Exception("Not Implemented Yet")

    # Inlined from Methods.Machine.Bore.plot
    def plot(self, fig=None, ax=None):
        """Plot the Bore in a matplotlib fig

        Parameters
        ----------
        self : Bore
            A Bore object
        fig :
            if None, open a new fig and plot, else add to the current
            one (Default value = None)

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """
        surf = self.get_surface()

        # Display the result
        (fig, ax, patch_leg, label_leg) = init_fig(fig, ax)
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        ax.set_title("Bore")

        # Add the Bore to the fig
        if self.get_is_stator:
            patches = surf.get_patches(color=self.STATOR_COLOR)
        else:
            patches = surf.get_patch(color=self.ROTOR_COLOR)
        for patch in patches:
            ax.add_patch(patch)

        # Axis Setup
        ax.axis("equal")
        fig.show()
        return fig, ax
