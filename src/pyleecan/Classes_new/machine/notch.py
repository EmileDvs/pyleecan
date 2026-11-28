# Experimental dataclass generated from Generator/ClassesRef/Machine/Notch.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from ...classes_common.errors import ParentMissingError
from ...classes_common.parents import container_or_parent
from .._legacy_class import LegacyClass
from ..material.material import Material

if TYPE_CHECKING:
    from .lamination import Lamination


@dataclass(eq=False)
class Notch(LegacyClass):
    """Notch

    Attributes
    ----------
    key_mat : Material or None
        The material of the key (if None, no key to add)
        Default: None
    """

    key_mat: Material | None = field(
        default=None, metadata={"default_class": "Material"}
    )
    """The material of the key (if None, no key to add)"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

    if TYPE_CHECKING:
        # Members of the daughter classes, for the type checkers
        # (not defined at runtime: no field, no method)

        def get_key_Ox_radius(self, *args: Any, **kwargs: Any) -> float | None: ...

    # Inlined from Methods.Machine.Notch.get_label
    def get_label(self, is_add_id: bool = True, lam: Lamination | None = None) -> str:
        """Return the label of the lamination (Stator-0 for instance)

        Parameters
        ----------
        self : Notch
            a Notch object
        is_add_id : bool
            True to add the "-X" part
        lam : Lamination, optional
            Lamination holding the notch (default: the parent)

        Returns
        -------
        label : str
            Label of the lamination

        """
        lam = container_or_parent(self, lam, "lam")

        if lam is not None:
            return lam.get_label(is_add_id=is_add_id)
        else:
            raise ParentMissingError("Error: The notch is not inside a Lamination")

    # Inlined from Methods.Machine.Notch.get_Rbo
    def get_Rbo(self, lam: Lamination | None = None) -> float:
        """Return the parent lamination bore radius
        (to make lam.notch[ii].notch_shape match lam.slot parent)

        Parameters
        ----------
        self : Notch
            A Notch object
        lam : Lamination, optional
            Lamination holding the notch (default: the parent)

        Returns
        -------
        Rbo: float
            The parent lamination bore radius [m]

        """
        lam = container_or_parent(self, lam, "lam")

        if lam is not None:
            return lam.get_Rbo()
        else:
            raise ParentMissingError("Error: The notch is not inside a Lamination")

    # Inlined from Methods.Machine.Notch.get_Ryoke
    def get_Ryoke(self, lam: Lamination | None = None) -> float:
        """Return the parent lamination yoke radius
        (to make lam.notch[ii].notch_shape match lam.slot parent)

        Parameters
        ----------
        self : Notch
            A Notch object
        lam : Lamination, optional
            Lamination holding the notch (default: the parent)

        Returns
        -------
        Ryoke: float
            The parent lamination yoke radius [m]

        """
        lam = container_or_parent(self, lam, "lam")

        if lam is not None:
            return lam.get_Ryoke()
        else:
            raise ParentMissingError("Error: The notch is not inside a Lamination")

    # Inlined from Methods.Machine.Notch.has_key
    def has_key(self) -> bool:
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
    def is_outwards(self, lam: Lamination | None = None) -> bool:
        """Return if the notch is outwards (on an external lamination) or inwards
        (on an internal lamination).
        (to make lam.notch[ii].notch_shape match lam.slot parent)

        Parameters
        ----------
        self : Notch
            A Notch object
        lam : Lamination, optional
            Lamination holding the notch (default: the parent)

        Returns
        -------
        is_outwards: bool
            True if the Lamination is not internal and false if not. For yoke notch,
            result is negated.
        """
        lam = container_or_parent(self, lam, "lam")
        if lam is not None:
            return lam.is_outwards()
        else:
            raise ParentMissingError("Error: The notch is not inside a Lamination")
