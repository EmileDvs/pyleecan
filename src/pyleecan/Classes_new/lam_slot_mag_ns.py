# Experimental dataclass generated from Generator/ClassesRef/Machine/LamSlotMagNS.csv
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
from .slot import Slot


@dataclass(eq=False)
class LamSlotMagNS(LamSlotM):
    """Lamination with Slot for Magnets with uneven north/south

    Attributes
    ----------
    magnet_north : Magnet or None
        North Magnet of the lamination
        Default: None
    magnet_south : Magnet or None
        South Magnet of the lamination
        Default: None
    slot_south : Slot or None
        South slot of the lamination
        Default: None
    """

    magnet_north: Magnet | None = None
    """North Magnet of the lamination"""
    magnet_south: Magnet | None = None
    """South Magnet of the lamination"""
    slot_south: Slot | None = None
    """South slot of the lamination"""

    # Inlined from Methods.Machine.LamSlotMagNS.build_geometry
    def build_geometry(
        self, is_magnet=True, sym=1, alpha=0, delta=0, is_circular_radius=False
    ):
        """Build the geometry of the LamSlotMag

        Parameters
        ----------
        self : LamSlotMagNS
            LamSlotMagNS object
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
        mag_surf_list = []
        # Add North magnet surface(s)
        if is_magnet and self.magnet_north is not None:
            # Get the active surface to copy rotate
            Nrad, Ntan = self.get_dim_active()
            mag_layer_surf = self.slot.build_geometry_active(
                Nrad=Nrad,
                Ntan=Ntan,
                alpha=alpha,
                delta=delta,
            )

            # for each magnet to draw
            for ii in range(Zs // sym // 2):
                for surf in mag_layer_surf:
                    mag_surf = surf.copy()
                    # changing the slot reference number
                    mag_surf.label = update_RTS_index(
                        label=surf.label, S_id=ii * 2, surf_type_label=MAG_LAB
                    )
                    mag_surf.rotate(ii * 2 * slot_pitch)
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

        # Add South magnet surface(s)
        if is_magnet and self.magnet_south is not None:
            # Get the active surface to copy rotate
            Nrad, Ntan = self.get_dim_active()
            mag_layer_surf = self.slot_south.build_geometry_active(
                Nrad=Nrad,
                Ntan=Ntan,
                alpha=alpha,
                delta=delta,
            )

            # for each magnet to draw
            for ii in range(Zs // sym // 2):
                id_mag = ii * 2 + 1
                for surf in mag_layer_surf:
                    mag_surf = surf.copy()
                    # changing the slot reference number
                    mag_surf.label = update_RTS_index(
                        label=surf.label, S_id=id_mag, surf_type_label=MAG_LAB
                    )
                    mag_surf.rotate(id_mag * slot_pitch)
                    mag_surf_list.append(mag_surf)
            # Update the magnets BC (if magnet side matches sym lines ex: SlotM18)
            if self.slot_south.is_full_pitch_active() and sym > 1:
                for surf in mag_surf_list:
                    label_dict = decode_label(surf.label)
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

    # Inlined from Methods.Machine.LamSlotMagNS.check
    def check(self):
        """Check that the Lamination object is correct

        Parameters
        ----------
        self : LamSlotMagNS
            A LamSlotMagNS object

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
        self.slot_south.check()

        if self.comp_height_yoke() < 0:
            raise LMC_SlotTooLong("The Slot is too long for the lamination (HYoke <0)")

    # Inlined from Methods.Machine.LamSlotMagNS.comp_masses
    def comp_masses(self):
        """Compute the Lamination masses (Mlam, Mmag)

        Parameters
        ----------
        self : LamSlotMagNS
            A LamSlotMagNS object

        Returns
        -------
        M_dict: dict
            Lamination mass dictionary (Mtot, Mlam, Mmag) [kg]

        """

        M_dict = LamSlot.comp_masses(self)
        p = self.get_pole_pair_number()

        Mmag = 0
        if self.magnet_north is not None:
            Mmag += p * (
                self.slot.comp_surface_active()
                * self.magnet_north.Nseg
                * self.magnet_north.Lmag
                * self.magnet_north.mat_type.struct.rho
            )
        if self.magnet_south is not None:
            Mmag += p * (
                self.slot_south.comp_surface_active()
                * self.magnet_south.Nseg
                * self.magnet_south.Lmag
                * self.magnet_south.mat_type.struct.rho
            )
        M_dict["Mmag"] = Mmag
        M_dict["Mtot"] += Mmag

        return M_dict

    # Inlined from Methods.Machine.LamSlotMagNS.comp_periodicity_geo
    def comp_periodicity_geo(self):
        """Compute the geometric periodicity factor of the lamination

        Parameters
        ----------
        self : LamSlotMagNS
            A LamSlotMagNS object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        return self.comp_periodicity_spatial()

    # Inlined from Methods.Machine.LamSlotMagNS.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the lamination

        Parameters
        ----------
        self : LamSlotMagNS
            A LamSlotMagNS object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        p = self.get_pole_pair_number()

        nb_list = [p]
        # account for notches and bore
        if self.notch is not None:
            for notch in self.notch:
                nb_list.append(notch.comp_periodicity_spatial()[0])

        if self.bore:
            nb_list.append(self.bore.comp_periodicity_spatial()[0])
        if self.yoke:
            nb_list.append(self.yoke.comp_periodicity_spatial()[0])

        # compute the gcd of the list
        if len(nb_list) == 1:
            per_a = nb_list[0]
        else:
            per_a = np.gcd(nb_list[0], nb_list[1])
            for ii in range(2, len(nb_list)):
                per_a = np.gcd(per_a, nb_list[ii])
        is_antiper_a = False

        # Account for duct periodicity
        per_a, is_antiper_a = self.comp_periodicity_duct_spatial(per_a, is_antiper_a)
        per_a = int(per_a)

        return per_a, is_antiper_a

    # Inlined from Methods.Machine.LamSlotMagNS.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces (Slam, Svent, Sslot, Smag)

        Parameters
        ----------
        self : LamSlotMagNS
            A LamSlotMagNS object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Sslot, Smag) [m**2]

        """

        S_dict = LamSlot.comp_surfaces(self)
        Smag = 0
        if self.magnet_north is not None:
            Smag += self.slot.comp_surface_active()
        if self.magnet_south is not None:
            Smag += self.slot_south.comp_surface_active()

        S_dict["Smag"] = Smag

        return S_dict

    # Inlined from Methods.Machine.LamSlotMagNS.comp_volumes
    def comp_volumes(self):
        """Compute the Lamination volumes (Vlam, Vvent, Vslot, Vmag)

        Parameters
        ----------
        self : LamSlotMagNS
            A LamSlotMagNS object

        Returns
        -------
        V_dict: dict
            Lamination surface dictionary (Vlam, Vvent, Vslot, Vmag) [m**3]

        """

        V_dict = LamSlot.comp_volumes(self)
        Vmag = 0
        if self.magnet_north is not None:
            Vmag += self.slot.comp_surface_active() * self.magnet_north.Lmag
        if self.magnet_south is not None:
            Vmag += self.slot_south.comp_surface_active() * self.magnet_south.Lmag

        V_dict["Vmag"] = Vmag

        return V_dict

    # Inlined from Methods.Machine.LamSlotMagNS.get_all_mag_obj
    def get_all_mag_obj(self):
        """Return all the magnet object for all the layers

        Parameters
        ----------
        self : LamSlotMagNS
            A LamSlotMagNS object

        Returns
        -------
        mag_list : [Magnet]
            List of magnet object to define
        """

        if self.mur_lin_matrix is None and self.Brm20_matrix is None:
            if len(self.magnet_north.compare(self.magnet_south)) > 0:
                return [self.magnet_north, self.magnet_south]
            else:
                return [self.magnet_north]
        else:
            raise NotImplementedError(
                "Error, Magnet matrix is not available yet for uneven North/South machines"
            )

    # Inlined from Methods.Machine.LamSlotMagNS.get_magnet_by_label
    def get_magnet_by_label(self, label=None, label_dict=None):
        """Return the magnet corresponding to the label

        Parameters
        ----------
        self : LamSlotMagNS
            A LamSlotMagNS object
        label : str
            A surface id (ex Rotor-0_Magnet_R0-T0-S0)
        label_dict : dict
            Split dict of the label (to avoid decoding twice)

        Returns
        -------
        mag : Magnet
            The corresponding magnet object
        """

        # Decode the magnet label
        if label_dict is None and label is None:
            raise Exception("label_dict and label can't be both at None")
        if label_dict is None:
            label_dict = decode_label(label)

        if label_dict["S_id"] % 2 == 0:
            return self.magnet_north
        else:
            return self.magnet_south

    # Inlined from Methods.Machine.LamSlotMagNS.get_slot_desc_list
    def get_slot_desc_list(self, sym=1, is_bore=True):
        """Returns an ordered description of the slot

        Parameters
        ----------
        self : LamSlotMagNS
            A LamSlotMagNS object
        sym: int
            Number of symmetry
        is_bore : bool
            True generate desc of bore, else yoke

        Returns
        -------
        slot_desc : list
            trigo ordered list of dictionary with key:
                "begin_angle" : float [rad]
                "end_angle" : float [rad]
                "obj" : Slot / None for Radius
                "lines : lines corresponding to the radius part
                "label" : Radius/Notch/Slot
        """

        if self.slot.is_bore != is_bore and self.slot_south.is_bore != is_bore:
            return []

        slot_list = []
        opN = self.slot.comp_angle_opening()
        opS = self.slot_south.comp_angle_opening()
        Zs = self.slot.Zs

        for ii in range(Zs // sym):
            if ii % 2 == 0 and self.slot.is_bore == is_bore:  # North
                slot_dict = {}
                slot_dict["begin_angle"] = 2 * np.pi / Zs * ii - opN / 2 + np.pi / Zs
                slot_dict["end_angle"] = 2 * np.pi / Zs * ii + opN / 2 + np.pi / Zs
                slot_dict["obj"] = self.slot
                slot_dict["lines"] = self.slot.build_geometry()
                # Apply rotation
                for line in slot_dict["lines"]:
                    line.rotate((slot_dict["begin_angle"] + slot_dict["end_angle"]) / 2)
                slot_dict["label"] = "slot"
                slot_list.append(slot_dict)
            elif ii % 2 == 1 and self.slot_south.is_bore == is_bore:  # South
                slot_dict = {}
                slot_dict["begin_angle"] = 2 * np.pi / Zs * ii - opS / 2 + np.pi / Zs
                slot_dict["end_angle"] = 2 * np.pi / Zs * ii + opS / 2 + np.pi / Zs
                slot_dict["obj"] = self.slot_south
                slot_dict["lines"] = self.slot_south.build_geometry()
                # Apply rotation
                for line in slot_dict["lines"]:
                    line.rotate((slot_dict["begin_angle"] + slot_dict["end_angle"]) / 2)
                slot_dict["label"] = "slot"
                slot_list.append(slot_dict)
        return slot_list

    # Inlined from Methods.Machine.LamSlotMagNS.set_Lmag
    def set_Lmag(self, value):
        """Set the Length of the magnet

        Parameters
        ----------
        self : LamSlotMagNS
            A LamSlotMagNS object
        value : float
            Value to set [m]
        """

        self.magnet_north.Lmag = value
        self.magnet_south.Lmag = value
