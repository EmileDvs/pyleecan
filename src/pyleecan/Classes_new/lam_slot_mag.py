# Experimental dataclass generated from Generator/ClassesRef/Machine/LamSlotMag.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ..Functions.labels import (
    BOUNDARY_PROP_LAB,
    COND_BOUNDARY_PROP_LAB,
    LAM_LAB,
    MAG_LAB,
    YOKE_LAB,
    YSML_LAB,
    YSMR_LAB,
    decode_label,
    update_RTS_index,
)
from ._error import LMC_SlotTooLong
from .lam_slot import LamSlot
from .lam_slot_m import LamSlotM
from .magnet import Magnet


@dataclass(eq=False)
class LamSlotMag(LamSlotM):
    """Lamination with Slot for Magnets

    Attributes
    ----------
    magnet : Magnet or None
        Magnet of the lamination
        Default: None
    """

    magnet: Magnet | None = None
    """Magnet of the lamination"""

    # Inlined from Methods.Machine.LamSlotMag.build_geometry
    def build_geometry(
        self, is_magnet=True, sym=1, alpha=0, delta=0, is_circular_radius=False
    ):
        """Build the geometry of the LamSlotMag

        Parameters
        ----------
        self : LamSlotMag
            LamSlotMag object
        is_magnet : bool
            If True build the magnet surfaces
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_circular_radius : bool
            True to add surfaces to "close" the Lamination radii

        Returns
        -------
        surf_list : list
            list of surfaces needed to draw the lamination

        """

        st = self.get_label()

        assert (self.slot.Zs % sym) == 0, (
            "ERROR, Wrong symmetry for "
            + st
            + " "
            + str(self.slot.Zs)
            + " slots and sym="
            + str(sym)
        )
        # getting the LamSlot surface
        surf_list = LamSlot.build_geometry(
            self,
            sym=sym,
            alpha=alpha,
            delta=delta,
            is_circular_radius=is_circular_radius,
        )

        Zs = self.slot.Zs
        slot_pitch = 2 * np.pi / Zs

        # Add the magnet surface(s)
        if is_magnet and self.magnet is not None:
            # Get the active surface to copy rotate
            Nrad, Ntan = self.get_dim_active()
            mag_layer_surf = self.slot.build_geometry_active(
                Nrad=Nrad,
                Ntan=Ntan,
                alpha=alpha,
                delta=delta,
            )

            # for each magnet to draw
            mag_surf_list = []
            for ii in range(Zs // sym):
                for surf in mag_layer_surf:
                    mag_surf = surf.copy()
                    # changing the slot reference number
                    mag_surf.label = update_RTS_index(
                        label=surf.label, S_id=ii, surf_type_label=MAG_LAB
                    )
                    mag_surf.rotate(ii * slot_pitch)
                    mag_surf_list.append(mag_surf)
            # Update the magnets BC (if magnet side matches sym lines ex: SlotM18)
            if self.slot.is_full_pitch_active() and sym > 1:
                for surf in mag_surf_list:
                    label_dict = decode_label(surf.label)
                    # Set BC on Right side / Ox
                    if label_dict["S_id"] == 0:
                        # Find the lines to add the BC
                        for line in surf.get_lines():
                            if (
                                line.prop_dict is not None
                                and COND_BOUNDARY_PROP_LAB in line.prop_dict
                                and line.prop_dict[COND_BOUNDARY_PROP_LAB] == YSMR_LAB
                            ):
                                line.prop_dict.update(
                                    {
                                        BOUNDARY_PROP_LAB: st
                                        + "_"
                                        + YSMR_LAB
                                        + "-"
                                        + str(label_dict["R_id"])
                                    }
                                )
                    # Set BC on Left side / last active surface
                    if label_dict["S_id"] == Zs // sym - 1:
                        # Find the lines to add the BC
                        for line in surf.get_lines():
                            if (
                                line.prop_dict is not None
                                and COND_BOUNDARY_PROP_LAB in line.prop_dict
                                and line.prop_dict[COND_BOUNDARY_PROP_LAB] == YSML_LAB
                            ):
                                line.prop_dict.update(
                                    {
                                        BOUNDARY_PROP_LAB: st
                                        + "_"
                                        + YSML_LAB
                                        + "-"
                                        + str(label_dict["R_id"])
                                    }
                                )
            # Update Magnets BC when no lamination
            if self.Rint == self.Rext and self.Rint != 0:
                label_yoke = self.get_label() + "_" + LAM_LAB + YOKE_LAB
                for surf in mag_surf_list:
                    label_dict = decode_label(surf.label)
                    if label_dict["R_id"] == 0:
                        for line in surf.get_lines():
                            if (
                                line.prop_dict is not None
                                and COND_BOUNDARY_PROP_LAB in line.prop_dict
                                and line.prop_dict[COND_BOUNDARY_PROP_LAB] == YOKE_LAB
                            ):
                                line.prop_dict.update({BOUNDARY_PROP_LAB: label_yoke})

            # Shift to have a tooth center on Ox
            for surf in mag_surf_list:
                surf.rotate(np.pi / Zs)
            surf_list.extend(mag_surf_list)

        return surf_list

    # Inlined from Methods.Machine.LamSlotMag.check
    def check(self):
        """Check that the Lamination object is correct

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object

        Returns
        -------
        None

        Raises
        _______
        LMC_SlotTooLong
            The Slot is too long for the lamination (HYoke <0)
        """
        super(type(self), self).check()

        self.slot.check()

        if self.comp_height_yoke() < 0:
            raise LMC_SlotTooLong("The Slot is too long for the lamination (HYoke <0)")

    # Inlined from Methods.Machine.LamSlotMag.comp_masses
    def comp_masses(self):
        """Compute the Lamination masses (Mlam, Mmag)

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object

        Returns
        -------
        M_dict: dict
            Lamination mass dictionary (Mtot, Mlam, Mmag) [kg]

        """

        M_dict = LamSlot.comp_masses(self)
        p = self.get_pole_pair_number()

        Mmag = (
            2
            * p
            * (
                self.slot.comp_surface_active()
                * self.magnet.Nseg
                * self.magnet.Lmag
                * self.magnet.mat_type.struct.rho
            )
        )

        M_dict["Mmag"] = Mmag
        M_dict["Mtot"] += Mmag

        return M_dict

    # Inlined from Methods.Machine.LamSlotMag.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces (Slam, Svent, Sslot, Smag)

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Sslot, Smag) [m**2]

        """

        S_dict = LamSlot.comp_surfaces(self)
        Smag = self.slot.comp_surface_active()

        S_dict["Smag"] = Smag

        return S_dict

    # Inlined from Methods.Machine.LamSlotMag.comp_volumes
    def comp_volumes(self):
        """Compute the Lamination volumes (Vlam, Vvent, Vslot, Vmag)

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object

        Returns
        -------
        V_dict: dict
            Lamination surface dictionary (Vlam, Vvent, Vslot, Vmag) [m**3]

        """

        V_dict = LamSlot.comp_volumes(self)
        Vmag = self.slot.comp_surface_active() * self.magnet.Lmag

        V_dict["Vmag"] = Vmag

        return V_dict

    # Inlined from Methods.Machine.LamSlotMag.get_all_mag_obj
    def get_all_mag_obj(self):
        """Return all the magnet object for all the layers

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object

        Returns
        -------
        mag_list : [Magnet]
            List of magnet object to define
        """

        mag_list = []
        if self.mur_lin_matrix is None and self.Brm20_matrix is None:
            return [self.magnet]
        elif self.mur_lin_matrix is not None:
            _, index_unique = np.unique(self.mur_lin_matrix, return_index=True)
            for ii, flat_index in enumerate(index_unique):
                mag_list.append(self.magnet.copy())
                mag_list[-1].mat_type.name = "Magnet_" + str(ii + 1)
                mag_list[-1].mat_type.mag.mur_lin = self.mur_lin_matrix.flat[flat_index]
                # Assume that if a magnet has a different mur_lin, it has a different Brm20
                # So unique is applied only on mur (no cross unique check)
                if self.Brm20_matrix is not None:
                    mag_list[-1].mat_type.mag.Brm20 = self.Brm20_matrix.flat[flat_index]
        else:  # Only change Brm20
            Brm20_val = np.unique(self.Brm20_matrix)
            for ii, Brm20 in enumerate(Brm20_val):
                mag_list.append(self.magnet.copy())
                mag_list[-1].mat_type.mag.Brm20 = Brm20
                mag_list[-1].mat_type.name = "Magnet_" + str(ii + 1)
                name_index += 1

        return mag_list

    # Inlined from Methods.Machine.LamSlotMag.get_magnet_by_label
    def get_magnet_by_label(self, label=None, label_dict=None):
        """Return the magnet corresponding to the label

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object
        label : str
            A surface id (ex Rotor-0_Magnet_R0-T0-S0)
        label_dict : dict
            Split dict of the label (to avoid decoding twice)

        Returns
        -------
        mag : Magnet
            The corresponding magnet object
        """

        # Usual case, all magnets are the same
        if self.mur_lin_matrix is None and self.Brm20_matrix is None:
            return self.magnet

        # Decode the magnet label
        if label_dict is None and label is None:
            raise Exception("label_dict and label can't be both at None")
        if label_dict is None:
            label_dict = decode_label(label)

        # Find the correct magnet to return
        mag_list = self.get_all_mag_obj()
        if self.mur_lin_matrix is not None:
            mur = self.mur_lin_matrix[
                label_dict["R_id"], label_dict["T_id"], label_dict["S_id"]
            ]
            mur_list = [mag.mat_type.mag.mur_lin for mag in mag_list]
            return mag_list[mur_list.index(mur)]
        elif self.Brm20_matrix is not None:
            Brm20 = self.Brm20_matrix[
                label_dict["R_id"], label_dict["T_id"], label_dict["S_id"]
            ]
            Brm20_list = [mag.mat_type.mag.Brm20 for mag in mag_list]
            return mag_list[Brm20_list.index(Brm20)]

    # Inlined from Methods.Machine.LamSlotMag.set_Lmag
    def set_Lmag(self, value):
        """Set the Length of the magnet

        Parameters
        ----------
        self : LamSlotMag
            A LamSlotMag object
        value : float
            Value to set [m]
        """

        self.magnet.Lmag = value
