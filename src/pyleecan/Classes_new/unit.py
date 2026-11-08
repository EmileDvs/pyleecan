# Experimental dataclass generated from Generator/ClassesRef/GUI_Option/Unit.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class Unit(PyleecanClass):
    """Unit

    Attributes
    ----------
    unit_m : int
        0: use m, 1: use mm
        Default: 0; Minimum: 0; Maximum: 1
    unit_rad : int
        0: use rad, 1: use deg
        Default: 0; Minimum: 0; Maximum: 1
    unit_m2 : int
        0: use m^2, 1: use mm^2
        Default: 0; Minimum: 0; Maximum: 1
    """

    unit_m: int = 0
    """0: use m, 1: use mm"""
    unit_rad: int = 0
    """0: use rad, 1: use deg"""
    unit_m2: int = 0
    """0: use m^2, 1: use mm^2"""

    # Inlined from Methods.GUI_Option.Unit.get_m
    def get_m(self, value):
        """Convert the value the correct m unit (to display in GUI)

        Parameters
        ----------
        self : Unit
            A Unit object
        value : float
            Value to convert

        Returns
        -------
        value : float
            Converted value in the current unit

        """
        if value is None:
            return None
        if self.unit_m == 1:  # Convert to mm
            return value * 1000
        else:
            return value

    # Inlined from Methods.GUI_Option.Unit.get_m2
    def get_m2(self, value):
        """Convert the value the correct m² unit (to display in GUI)

        Parameters
        ----------
        self : Unit
            A Unit object
        value : float
            Value to convert

        Returns
        -------
        value : float
            Value in the current unit
        """
        if value is None:
            return None
        if self.unit_m2 == 1:  # Convert to mm^2
            return value * 1000000
        else:
            return value

    # Inlined from Methods.GUI_Option.Unit.get_m2_name
    def get_m2_name(self):
        """Return the name of the current area unit

        Parameters
        ----------
        self : Unit
            A Unit object

        Returns
        -------
        unit_name : str
            Name of the current unit
        """
        if self.unit_m2 == 1:
            return "mm²"
        else:
            return "m²"

    # Inlined from Methods.GUI_Option.Unit.get_m_name
    def get_m_name(self):
        """Return the name of the length unit ([m] by default)

        Parameters
        ----------
        self : Unit
            A Unit object

        Returns
        -------
        unit_name: str
            Name of the current unit
        """
        if self.unit_m == 1:
            return "mm"
        else:
            return "m"

    # Inlined from Methods.GUI_Option.Unit.set_m
    def set_m(self, value):
        """Convert the value the correct m unit (to set in the object in m)

        Parameters
        ----------
        self : Unit
            A Unit object
        value : float
            Value to convert

        Returns
        -------
        value: float
            value converted in [m]
        """
        if self.unit_m == 1:  # Convert to mm
            return value / 1000
        else:
            return value

    # Inlined from Methods.GUI_Option.Unit.set_m2
    def set_m2(self, value):
        """Convert the value the correct m² unit (to set in the object in m²)

        Parameters
        ----------
        self : Unit
            A Unit object
        value : float
            Value to convert

        Returns
        -------
        value : float
            value converted in [m²]
        """
        if self.unit_m2 == 1:  # Convert to mm²
            return value / 1000000
        else:
            return value
