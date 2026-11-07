# Experimental dataclass generated from Generator/ClassesRef/Machine/CondType13.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ..definitions import config_dict
from .conductor import Conductor


@dataclass(eq=False)
class CondType13(Conductor):
    """parallel stranded conductor consisting of at least a single round wire

    Attributes
    ----------
    Wwire : float
        cf schematics, single wire diameter without insulation [m]
        Unit: m; Default: 0.015; Minimum: 0
    Wins_cond : float
        (advanced) cf schematics, winding coil insulation diameter [m]
        Unit: m; Default: 0.015; Minimum: 0
    Nwppc_rad : int
        cf schematics, stator winding number of preformed wires (strands) in parallel per coil along radial (vertical) direction
        Default: 1; Minimum: 1
    Nwppc_tan : int
        cf schematics, stator winding number of preformed wires (strands) in parallel per coil along tangential (horizontal) direction
        Default: 1; Minimum: 1
    Wins_wire : float
        (advanced) cf schematics, winding strand insulation thickness [m]
        Unit: m; Default: 0; Minimum: 0
    Kwoh : float
        winding overhang factor which describes the fact that random round wire end-windings can be more or less compressed (0.5 for small motors, 0.8 for large motors) - can be used to tune the average turn length (relevant if type_cond==1)
        Default: 0.5; Minimum: 0
    """

    COND_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][0].copy()
    INS_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][1].copy()
    Wwire: float = 0.015
    """cf schematics, single wire diameter without insulation [m]"""
    Wins_cond: float = 0.015
    """(advanced) cf schematics, winding coil insulation diameter [m]"""
    Nwppc_rad: int = 1
    """cf schematics, stator winding number of preformed wires (strands) in parallel per coil along radial (vertical) direction"""
    Nwppc_tan: int = 1
    """cf schematics, stator winding number of preformed wires (strands) in parallel per coil along tangential (horizontal) direction"""
    Wins_wire: float = 0
    """(advanced) cf schematics, winding strand insulation thickness [m]"""
    Kwoh: float = 0.5
    """winding overhang factor which describes the fact that random round wire end-windings can be more or less compressed (0.5 for small motors, 0.8 for large motors) - can be used to tune the average turn length (relevant if type_cond==1)"""

    # Inlined from Methods.Machine.CondType13.comp_height
    def comp_height(self):
        """Compute the height of the conductor

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        H: float
            Height of the conductor [m]

        """

        return (2 * self.Wins_wire + self.Wwire) * self.Nwppc_rad

    # Inlined from Methods.Machine.CondType13.comp_height_wire
    def comp_height_wire(self):
        """Return wire diameter

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        H: float
            Diameter of the wire [m]

        """

        return self.Wwire

    # Inlined from Methods.Machine.CondType13.comp_nb_circumferential_wire
    def comp_nb_circumferential_wire(self):
        """Return number of adjacent wires in circumferential direction

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in circumferential direction

        """

        return self.Nwppc_tan

    # Inlined from Methods.Machine.CondType13.comp_nb_radial_wire
    def comp_nb_radial_wire(self):
        """Return number of adjacent wires in radial direction

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in radial direction

        """

        return self.Nwppc_rad

    # Inlined from Methods.Machine.CondType13.comp_surface
    def comp_surface(self):
        """Compute the surface of the conductor

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        S: float
            Surface of the conductor (with insulation) [m**2]

        """

        S = self.comp_height() * self.comp_width()

        return S

    # Inlined from Methods.Machine.CondType13.comp_surface_active
    def comp_surface_active(self):
        """Compute the active surface of the conductor

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        Sact: float
            Surface without insulation [m**2]

        """

        Sact = self.Wwire * self.Wwire * self.Nwppc_tan * self.Nwppc_rad

        return Sact

    # Inlined from Methods.Machine.CondType13.comp_width
    def comp_width(self):
        """Compute the width of the conductor

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        W: float
            Width of the conductor [m]

        """

        return (2 * self.Wins_wire + self.Wwire) * self.Nwppc_tan

    # Inlined from Methods.Machine.CondType13.comp_width_wire
    def comp_width_wire(self):
        """Return wire diameter

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        H: float
            Diameter of the wire [m]

        """

        return self.Wwire

    # Inlined from Methods.Machine.CondType13.is_round_wire
    def is_round_wire(self):
        """Return if wire is round

        Parameters
        ----------
        self : CondType13
            A CondType13 object

        Returns
        -------
        is_round_wire: bool
            is_round_wire is always True since wire is round

        """

        return True

    # Inlined from Methods.Machine.CondType13.plot
    def plot(self, is_show_fig=True, fig=None, ax=None):
        """Plot a Conductor in a matplotlib fig

        Parameters
        ----------
        self : CondType13
            A CondType13 object
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        None
        """

        # TODO

        pass

    # Inlined from Methods.Machine.CondType13.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_add_schematics=True,
        is_add_main_line=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : CondType13
            A CondType13 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        """

        # TODO

        pass
