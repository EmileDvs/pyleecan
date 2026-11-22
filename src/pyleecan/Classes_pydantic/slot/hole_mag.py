# Experimental pydantic model generated from Generator/ClassesRef/Slot/HoleMag.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

from ...classes_common.parents import container_or_parent
from .hole import Hole

if TYPE_CHECKING:
    from ..machine.lamination import Lamination


class HoleMag(Hole):
    """Hole with magnets for lamination (abstract)

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Slot"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Slot.HoleMag.comp_mass_magnet_id
    def comp_mass_magnet_id(self, index: int, lam: Lamination | None = None) -> float:
        """Compute the mass of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleMag
            A HoleMag object
        index : int
            Index of the magnet to compute the surface
        lam : Lamination
            Lamination of the hole (default: the parent of the hole)

        Returns
        -------
        Mmag: float
            Mass of the Magnet [m**2]
        """
        lam = container_or_parent(self, lam, "lam")

        mag_list = self.get_magnet_list()
        if mag_list[index] is None:
            return 0
        else:
            if mag_list[index].Lmag is None:
                Lmag = lam.L1
            else:
                Lmag = mag_list[index].Lmag
            return self.comp_surface_magnet_id(index) * Lmag

    # Inlined from Methods.Slot.HoleMag.comp_mass_magnets
    def comp_mass_magnets(self, lam: Lamination | None = None) -> float:
        """Compute the mass of the hole magnets (some of them may be missing)

        Parameters
        ----------
        self : HoleMag
            A HoleMag object
        lam : Lamination
            Lamination of the hole (default: the parent of the hole)

        Returns
        -------
        Mmag: float
            mass of the magnets [kg]
        """
        lam = container_or_parent(self, lam, "lam")

        M = 0
        mag_list = self.get_magnet_list()
        for ii, mag in enumerate(mag_list):
            if mag is not None:
                Smag = self.comp_surface_magnet_id(ii)
                if mag.Lmag is None:
                    Lmag = lam.L1
                else:
                    Lmag = mag.Lmag
                # Check material definition
                if mag.mat_type.struct.rho is None:
                    raise Exception(
                        "Error: For magnet material "
                        + str(mag.mat_type.name)
                        + " struct.rho is not set"
                    )
                M += Smag * Lmag * mag.mat_type.struct.rho

        return M

    # Inlined from Methods.Slot.HoleMag.comp_surface_magnets
    def comp_surface_magnets(self) -> float:
        """Compute the surface of all the magnet(s)

        Parameters
        ----------
        self : HoleMag
            A HoleMag object

        Returns
        -------
        Smag: float
            Surface of all the Magnet(s) [m**2]
        """

        mag_list = self.get_magnet_list()
        Smag = 0
        for ii in range(len(mag_list)):
            Smag += self.comp_surface_magnet_id(ii)
        return Smag

    # Inlined from Methods.Slot.HoleMag.comp_volume_magnets
    def comp_volume_magnets(self, lam: Lamination | None = None) -> float:
        """Compute the volume of the hole magnets (some of them may be missing)

        Parameters
        ----------
        self : HoleMag
            A HoleMag object
        lam : Lamination
            Lamination of the hole (default: the parent of the hole)

        Returns
        -------
        Vmag: float
            volume of the magnets [m**3]
        """
        lam = container_or_parent(self, lam, "lam")

        V = 0
        mag_list = self.get_magnet_list()
        for ii, mag in enumerate(mag_list):
            if mag is not None:
                Smag = self.comp_surface_magnet_id(ii)
                if mag.Lmag is None:
                    Lmag = lam.L1
                else:
                    Lmag = mag.Lmag
                V += Smag * Lmag

        return V

    # Inlined from Methods.Slot.HoleMag.get_magnet_list
    def get_magnet_list(self) -> list:
        """Return the list of magnet (including None)

        Parameters
        ----------
        self : HoleMag
            A HoleMag object

        Returns
        -------
        magnet_list : list
            List of Magnet

        """

        magnet_list = []
        if hasattr(self, "magnet_dict"):
            for value in self.magnet_dict.values():
                magnet_list.append(value)
        else:
            mag_id = 0
            while hasattr(self, "magnet_" + str(mag_id)):
                magnet_list.append(getattr(self, "magnet_" + str(mag_id)))
                mag_id += 1
        return magnet_list

    # Inlined from Methods.Slot.HoleMag.has_magnet
    def has_magnet(self) -> bool:
        """Return if the Hole has magnet

        Parameters
        ----------
        self : HoleMag
            A HoleMag object

        Returns
        -------
        has_magnet : bool
            True

        """

        return True
