# Experimental dataclass generated from Generator/ClassesRef/Geometry/Surface.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from math import ceil

from ..definitions import PACKAGE_NAME, config_dict
from ..Functions.FEMM.get_FEMM_BC_propname import get_FEMM_BC_propname
from ..Functions.FEMM.get_mesh_param import get_mesh_param
from ..Functions.init_fig import init_fig
from ..Functions.labels import (
    BORE_LAB,
    BOUNDARY_PROP_LAB,
    DRAW_PROP_LAB,
    LAM_LAB,
    RADIUS_PROP_LAB,
    YOKE_LAB,
    decode_label,
)
from ..Functions.Load.import_class import import_class as _pyleecan_import_class
from ._pyleecan_class import PyleecanClass
from .arc_1 import Arc1
from .arc_2 import Arc2
from .arc_3 import Arc3
from .hole import Hole
from .segment import Segment
from .slot import Slot


@dataclass(eq=False)
class Surface(PyleecanClass):
    """SurfLine define by list of lines that delimit it

    Attributes
    ----------
    point_ref : complex
        Center of symmetry
        Default: 0
    label : str or None
        Label of the surface
        Default: None
    """

    PATCH_EDGE = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE"]
    PATCH_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR"]
    point_ref: complex = 0
    """Center of symmetry"""
    label: str | None = None
    """Label of the surface"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                Hole,
                Slot,
                Surface,
            ),
        ):
            raise TypeError(
                "Surface parent must be an instance of Hole or Slot or Surface, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Geometry.Surface.comp_mesh_dict
    def comp_mesh_dict(self, element_size, prefix=""):
        """Returns the number of mesh elements on each line of the surface
        to match the element_size.

        Parameters
        ----------
        self : Surface
            a Surface object

        element_size : float
            The size of each element on the mesh [m]
        prefix: str
            Label prefix for line


        Returns
        -------
        mesh_dict : dict
            Dictionary containing the number of element of each line of the surface
        """

        mesh_dict = {}
        lines = self.get_lines()
        for ii, line in enumerate(lines):
            label = prefix + str(ii)
            length = line.comp_length()
            number_of_element = ceil(length / element_size)
            mesh_dict[label] = number_of_element

        return mesh_dict

    # Inlined from Methods.Geometry.Surface.draw_FEMM
    def draw_FEMM(
        self,
        femm,
        nodeprop=None,
        maxseg=None,
        FEMM_dict=None,
        hide=False,
        BC_dict=None,
        is_draw=True,
        type_set_BC=0,
    ):
        """draw the Surface in FEMM

        Parameters
        ----------
        femm : FEMMHandler
            client to send command to a FEMM instance
        nodeprop :
            Nodal property
            (Default value = None)
        maxseg :
            Meshed with elements that span at most maxsegdeg degrees per element
            (Default value = None)
        FEMM_dict : dict
            dictionary containing the main parameters of FEMM
        hide :
            0 = not hidden in post-processor, 1 == hidden in post processor
            (Default value = False)
        BC_dict : dict
            Boundary condition dict ([line label] = BC name)
        is_draw : bool
            1 to draw the list of surfaces given
        type_set_BC : bool
            1 to set BC of the yoke only, 0 to set all

        Returns
        -------
        None

        """
        # Check if the Surface is correct
        self.check()

        # Draw all the lines
        lines = self.get_lines()

        for line in lines:
            label_dict = decode_label(self.label)  # Use surface mesh param
            # Bore / Yoke radius should have different mesh property
            if line.prop_dict not in [None, {}]:
                if RADIUS_PROP_LAB in line.prop_dict:
                    if YOKE_LAB in line.prop_dict[RADIUS_PROP_LAB]:
                        label_dict["surf_type"] = LAM_LAB + YOKE_LAB
                    elif BORE_LAB in line.prop_dict[RADIUS_PROP_LAB]:
                        label_dict["surf_type"] = LAM_LAB + BORE_LAB
                    else:
                        raise Exception(
                            "Unknown prop_dict for line of surface " + self.label
                        )
                if (
                    DRAW_PROP_LAB in line.prop_dict
                    and not line.prop_dict[DRAW_PROP_LAB]
                ):
                    continue  #  This line should not be drawn
            mesh_dict = get_mesh_param(label_dict, FEMM_dict)

            group = mesh_dict["group"]
            if isinstance(group, list):
                group = group[label_dict["S_id"]]

            # Get or create the Boundary Condition (if any)
            if line.prop_dict is not None and BOUNDARY_PROP_LAB in line.prop_dict:
                is_yoke_BC = LAM_LAB + YOKE_LAB in line.prop_dict[BOUNDARY_PROP_LAB]

                if type_set_BC == 0 or (type_set_BC == 1 and is_yoke_BC):
                    propname = get_FEMM_BC_propname(
                        femm=femm,
                        line_label=line.prop_dict[BOUNDARY_PROP_LAB],
                        BC_dict=BC_dict,
                    )

                else:
                    propname = "None"  # No BC to set
            else:
                propname = "None"  # No BC to set
            # Draw the Line
            if type(line) in [Arc1, Arc2, Arc3]:
                line.draw_FEMM(
                    femm=femm,
                    nodeprop=nodeprop,
                    maxseg=maxseg,
                    element_size=mesh_dict["element_size"],
                    propname=propname,
                    hide=hide,
                    group=group,
                    is_draw=is_draw,
                )
            else:
                line.draw_FEMM(
                    femm=femm,
                    nodeprop=nodeprop,
                    propname=propname,
                    element_size=mesh_dict["element_size"],
                    automesh=mesh_dict["automesh"],
                    hide=hide,
                    group=group,
                    is_draw=is_draw,
                )

    # Inlined from Methods.Geometry.Surface.intersect_line
    def intersect_line(self, Z1, Z2):
        """Return all the intersection of a line with the surfaces

        Parameters
        ----------
        self : Surface
            A Surface object
        Z1 : complex
            First point to define the intersecting line
        Z2 : complex
            Second point to define the intersecting line

        Returns
        -------
        Z_list : [complex]
            List of intersection between the line and the surface
        """

        Z_list = []

        for line in self.get_lines():
            Z_list.extend(line.intersect_line(Z1, Z2))

        return Z_list

    # Inlined from Methods.Geometry.Surface.is_inside
    def is_inside(self, Z, if_online=False):
        """Determine if a given point is inside the surface.
           If the point is on the line defining the surface, by default it will be considered as outside

        Parameters
        ----------
        self : Surface
            A Surface object
        Z : complex
            Point that we want to check if it is in the surface
        if_online : bool
            True to consider the point  on the line as in the surface
            False to consider the point on the line as out of the surface

        Returns
        -------
        is_inside : bool
            True : the point is inside the surface
            False : the point is outside the surface
        """

        # Half of the width of the branch where we will check is there is a point
        eps = 0.0001

        # Recovering the point cloud that compose the surface
        line_list = self.get_lines()

        pointcloud = []
        for line in line_list:
            line_len = line.comp_length()
            Npoint = max(int(line_len / eps), 4)
            pointcloud.extend(line.discretize(nb_point=Npoint))

        # Step 1 : Checking if the point is on the line that define the surface
        # First, we call the is_online method for each segment to check is the point is on one of the segment
        for line in line_list:
            if line.is_on_line(Z):
                return if_online

        # Step 2 : Checking if the point is inside the surface
        # Then, we are creating a cross on both axes with a width of 2*eps centered on Z
        # We check that at least one point is inside each branch of the cross

        # To determine which branch the point is in, we check the distance to Z
        is_top, is_left, is_bot, is_right = False, False, False, False
        for point in pointcloud:
            # If the point selected is inside the branch on the x-axis
            if (point.real > Z.real - eps) and (point.real < Z.real + eps):
                if point.imag - Z.imag > 0:
                    # The point is on top of Z
                    is_top = True
                else:
                    # The point is below Z
                    is_bot = True
            # If the point selected is inside the branch on the y-axis
            if (point.imag > Z.imag - eps) and (point.imag < Z.imag + eps):
                if point.real - Z.real > 0:
                    # The point is on the left of Z
                    is_left = True
                else:
                    # The point is on the right of Z
                    is_right = True

        # Plot for debug
        # fig, ax = self.plot()
        # ax.plot(Z.real, Z.imag, "xr")
        # for point in pointcloud:
        #     ax.plot(point.real, point.imag, "xg")

        return is_top and is_left and is_right and is_bot

    # Inlined from Methods.Geometry.Surface.plot
    def plot(
        self,
        fig=None,
        ax=None,
        color=None,
        edgecolor=None,
        is_edge_only=False,
        linestyle=None,
        is_disp_point_ref=False,
        is_disp_line_index=False,
        is_show_fig=True,
    ):
        """Plot the Surface patch in a matplotlib fig

        Parameters
        ----------
        self : Surface
            A Surface object
        fig :
            if None, open a new fig and plot, else add to the
            current one (Default value = None)
        color :
            the color of the patch (Default value = PATCH_COLOR)
        edgecolor :
            the edge color of the patch (Default value = PATCH_EDGE)
        is_edge_only: bool
            To set the transparancy of the face color to 0 and 1 for the edge color
        linestyle : str
            Line style of the edge {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
        is_disp_point_ref : bool
            True to add the point_ref
        is_disp_line_index : bool
            True to add the index of the lines
        is_show_fig : bool
            To call show at the end of the methods

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        (fig, ax, patch_leg, label_leg) = init_fig(fig, ax)
        ax.set_xlabel("[m]")
        ax.set_ylabel("[m]")

        patches = self.get_patches(
            color=color,
            edgecolor=edgecolor,
            is_edge_only=is_edge_only,
            linestyle=linestyle,
        )
        for patch in patches:
            ax.add_patch(patch)

        if is_disp_point_ref:
            ax.plot(self.point_ref.real, self.point_ref.imag, "kx")

        if is_disp_line_index:
            for ii, line in enumerate(self.get_lines()):
                mid = line.get_middle()
                ax.text(mid.real, mid.imag, str(ii))
        # Axis Setup
        ax.axis("equal")

        if is_show_fig:
            fig.show()
        return fig, ax

    plot.__defaults__ = plot.__defaults__[:2] + (PATCH_COLOR,) + plot.__defaults__[3:]
    plot.__defaults__ = plot.__defaults__[:3] + (PATCH_EDGE,) + plot.__defaults__[4:]

    # Inlined from Methods.Geometry.Surface.split_line
    def split_line(self, Z1, Z2, is_join=False, prop_dict_join=None):
        """Cut the Surface in two part according to a line defined by two complex
        "Above" is in the coordinate system with Z1 in 0 and Z2 on the X>0 axis

        Parameters
        ----------
        self : Surface
            An Surface object
        Z1 : complex
            First point of the cutting Line
        Z2 : complex
            Second point of the cutting Line
        is_join : bool
            True to join the split_list with Segment on the cutting line
        prop_dict_join : dict
            Property dict to set on the join line

        Returns
        -------
        top_surf, bot_surf : SurfLine
            The two part of the Surface
            (one can be None if the line doesn't cut the surface)
        """

        # Dynamic import to avoid import loop
        SurfLine = _pyleecan_import_class(PACKAGE_NAME + ".Classes", "SurfLine")

        # Split all the lines of the surface
        lines = self.get_lines()
        top_split_list = []  # List of line of the top part
        bot_split_list = []  # List of line of the bot part
        for line in lines:
            line_top, line_bot = line.split_line(
                Z1=Z1,
                Z2=Z2,
                is_join=is_join,
                prop_dict_join=prop_dict_join,
            )
            top_split_list.extend(line_top)
            bot_split_list.extend(line_bot)

        # Create the resulting surface and update ref point
        if len(top_split_list) > 0:
            if is_join:  # Make sure that the surface is closed (if needed)
                top_split_list = self.join_surf_line(top_split_list, prop_dict_join)
            top_surf = SurfLine(label=self.label, line_list=top_split_list)
            top_surf.comp_point_ref(is_set=True)
        else:
            top_surf = None

        if len(bot_split_list) > 0:
            if is_join:  # Make sure that the surface is closed (if needed)
                bot_split_list = self.join_surf_line(bot_split_list, prop_dict_join)
            bot_surf = SurfLine(label=self.label, line_list=bot_split_list)
            bot_surf.comp_point_ref(is_set=True)
        else:
            bot_surf = None

        return top_surf, bot_surf

    @staticmethod
    def join_surf_line(split_list, prop_dict_join):
        """Join the surface to make sur the the surface is closed"""
        final_list = []
        for ii in range(len(split_list) - 1):
            final_list.append(split_list[ii])
            if abs(split_list[ii].get_end() - split_list[ii + 1].get_begin()) > 1e-6:
                final_list.append(
                    Segment(
                        begin=split_list[ii].get_end(),
                        end=split_list[ii + 1].get_begin(),
                        prop_dict=prop_dict_join,
                    )
                )
        final_list.append(split_list[-1])
        # Add last line
        if abs(split_list[-1].get_end() - split_list[0].get_begin()) > 1e-6:
            final_list.append(
                Segment(
                    begin=split_list[-1].get_end(),
                    end=split_list[0].get_begin(),
                    prop_dict=prop_dict_join,
                )
            )
        return final_list
