# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleMag.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .hole import Hole


@dataclass(eq=False)
class HoleMag(Hole):
    """Hole with magnets for lamination (abstract)

    Attributes
    ----------
    """

    # Inlined from Methods.Slot.HoleMag.comp_mass_magnet_id
    def comp_mass_magnet_id(self, index):
        """Compute the mass of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleMag
            A HoleMag object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Mmag: float
            Mass of the Magnet [m**2]
        """

        mag_list = self.get_magnet_list()
        if mag_list[index] is None:
            return 0
        else:
            if mag_list[index].Lmag is None:
                Lmag = self.parent.L1
            else:
                Lmag = mag_list[index].Lmag
            return self.comp_surface_magnet_id(index) * Lmag

    # Inlined from Methods.Slot.HoleMag.comp_mass_magnets
    def comp_mass_magnets(self):
        """Compute the mass of the hole magnets (some of them may be missing)

        Parameters
        ----------
        self : HoleMag
            A HoleMag object

        Returns
        -------
        Mmag: float
            mass of the magnets [kg]
        """

        M = 0
        mag_list = self.get_magnet_list()
        for ii, mag in enumerate(mag_list):
            if mag is not None:
                Smag = self.comp_surface_magnet_id(ii)
                if mag.Lmag is None:
                    Lmag = self.parent.L1
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
    def comp_surface_magnets(self):
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
    def comp_volume_magnets(self):
        """Compute the volume of the hole magnets (some of them may be missing)

        Parameters
        ----------
        self : HoleMag
            A HoleMag object

        Returns
        -------
        Vmag: float
            volume of the magnets [m**3]
        """

        V = 0
        mag_list = self.get_magnet_list()
        for ii, mag in enumerate(mag_list):
            if mag is not None:
                Smag = self.comp_surface_magnet_id(ii)
                if mag.Lmag is None:
                    Lmag = self.parent.L1
                else:
                    Lmag = mag.Lmag
                V += Smag * Lmag

        return V

    # Inlined from Methods.Slot.HoleMag.get_magnet_list
    def get_magnet_list(self):
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
    def has_magnet(self):
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
