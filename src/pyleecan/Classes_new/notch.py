# Experimental dataclass generated from Generator/ClassesRef/Machine/Notch.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from . import ParentMissingError
from ._pyleecan_class import PyleecanClass
from .lamination import Lamination
from .material import Material


@dataclass(eq=False)
class Notch(PyleecanClass):
    """Notch

    Attributes
    ----------
    key_mat : Material or None
        The material of the key (if None, no key to add)
        Default: None
    """

    key_mat: Material | None = None
    """The material of the key (if None, no key to add)"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Lamination,)):
            raise TypeError(
                "Notch parent must be an instance of Lamination, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Machine.Notch.get_label
    def get_label(self, is_add_id=True):
        """Return the label of the lamination (Stator-0 for instance)

        Parameters
        ----------
        self : Notch
            a Notch object
        is_add_id : bool
            True to add the "-X" part

        Returns
        -------
        label : str
            Label of the lamination

        """

        if self.parent is not None:
            return self.parent.get_label()
        else:
            raise ParentMissingError("Error: The notch is not inside a Lamination")

    # Inlined from Methods.Machine.Notch.get_Rbo
    def get_Rbo(self):
        """Return the parent lamination bore radius
        (to make lam.notch[ii].notch_shape match lam.slot parent)

        Parameters
        ----------
        self : Notch
            A Notch object

        Returns
        -------
        Rbo: float
            The parent lamination bore radius [m]

        """

        if self.parent is not None:
            return self.parent.get_Rbo()
        else:
            raise ParentMissingError("Error: The notch is not inside a Lamination")

    # Inlined from Methods.Machine.Notch.get_Ryoke
    def get_Ryoke(self):
        """Return the parent lamination yoke radius
        (to make lam.notch[ii].notch_shape match lam.slot parent)

        Parameters
        ----------
        self : Notch
            A Notch object

        Returns
        -------
        Ryoke: float
            The parent lamination yoke radius [m]

        """

        if self.parent is not None:
            return self.parent.get_Ryoke()
        else:
            raise ParentMissingError("Error: The notch is not inside a Lamination")

    # Inlined from Methods.Machine.Notch.has_key
    def has_key(self):
        """Check if a there is key in the notch

        Parameters
        ----------
        self : Notch
            A Notch object

        Returns
        -------
        has_key : bool
            True if the notch has a key
        """

        return self.key_mat is not None

    # Inlined from Methods.Machine.Notch.is_outwards
    def is_outwards(self):
        """Return if the notch is outwards (on an external lamination) or inwards
        (on an internal lamination).
        (to make lam.notch[ii].notch_shape match lam.slot parent)

        Parameters
        ----------
        self : Notch
            A Notch object

        Returns
        -------
        is_outwards: bool
            True if the Lamination is not internal and false if not. For yoke notch,
            result is negated.
        """
        if self.parent is not None:
            return self.parent.is_outwards()
        else:
            raise ParentMissingError("Error: The notch is not inside a Lamination")
