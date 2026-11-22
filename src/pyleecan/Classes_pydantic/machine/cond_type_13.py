# Experimental pydantic model generated from Generator/ClassesRef/Machine/CondType13.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

from pydantic import Field

from .conductor import Conductor

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from .lamination import Lamination
    from .winding import Winding


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

    Wwire: float = Field(default=0.015, ge=0, json_schema_extra={"unit": "m"})
    """cf schematics, single wire diameter without insulation [m]"""
    Wins_cond: float = Field(default=0.015, ge=0, json_schema_extra={"unit": "m"})
    """(advanced) cf schematics, winding coil insulation diameter [m]"""
    Nwppc_rad: int = Field(default=1, ge=1)
    """cf schematics, stator winding number of preformed wires (strands) in parallel per coil along radial (vertical) direction"""
    Nwppc_tan: int = Field(default=1, ge=1)
    """cf schematics, stator winding number of preformed wires (strands) in parallel per coil along tangential (horizontal) direction"""
    Wins_wire: float = Field(default=0, ge=0, json_schema_extra={"unit": "m"})
    """(advanced) cf schematics, winding strand insulation thickness [m]"""
    Kwoh: float = Field(default=0.5, ge=0)
    """winding overhang factor which describes the fact that random round wire end-windings can be more or less compressed (0.5 for small motors, 0.8 for large motors) - can be used to tune the average turn length (relevant if type_cond==1)"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Machine.CondType13.comp_height
    def comp_height(self) -> float:
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
    def comp_height_wire(
        self, winding: Winding | None = None, lam: Lamination | None = None
    ) -> float:
        """Return wire diameter

        Parameters
        ----------
        self : CondType13
            A CondType13 object
        winding : Winding, optional
            Winding holding the object (default: the parent)
        lam : Lamination, optional
            Lamination of the winding (default: the parent of the winding)

        Returns
        -------
        H: float
            Diameter of the wire [m]

        """

        return self.Wwire

    # Inlined from Methods.Machine.CondType13.comp_nb_circumferential_wire
    def comp_nb_circumferential_wire(self) -> int:
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
    def comp_nb_radial_wire(self) -> int:
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
    def comp_surface(self) -> float:
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
    def comp_surface_active(self) -> float:
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
    def comp_width(self) -> float:
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
    def comp_width_wire(
        self, winding: Winding | None = None, lam: Lamination | None = None
    ) -> float:
        """Return wire diameter

        Parameters
        ----------
        self : CondType13
            A CondType13 object
        winding : Winding, optional
            Winding holding the object (default: the parent)
        lam : Lamination, optional
            Lamination of the winding (default: the parent of the winding)

        Returns
        -------
        H: float
            Diameter of the wire [m]

        """

        return self.Wwire

    # Inlined from Methods.Machine.CondType13.is_round_wire
    def is_round_wire(self) -> bool:
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
    def plot(
        self,
        is_show_fig: bool = True,
        fig: Figure | None = None,
        ax: Axes | None = None,
    ):
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
        is_default: bool = False,
        is_add_schematics: bool = True,
        is_add_main_line: bool = True,
        save_path: str | None = None,
        is_show_fig: bool = True,
        fig: Figure | None = None,
        ax: Axes | None = None,
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
