# Experimental dataclass generated from Generator/ClassesRef/Loss/LossModelJoule.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .loss_model import LossModel


@dataclass(eq=False)
class LossModelJoule(LossModel):
    """Joule loss model

    Attributes
    ----------
    type_skin_effect : int
        0 to ignore skin effect, 1 to consider it
        Default: 1
    """

    type_skin_effect: int = 1
    """0 to ignore skin effect, 1 to consider it"""

    # Inlined from Methods.Loss.LossModelJoule.comp_coeff
    def comp_coeff(self, T_op=20, T_ref=20):
        """Compute the skin effect factor on resistance for the conductors from "Design of Rotating Electrical Machines", J. Pyrhonen, second edition
        All parameters are defined p.270 / 271
        In this method, the returned value is the one from the reference divided by the frequency, as the effect of
        frequency will be taken into account in the coeff_dict

        Parameters
        ----------
        self : LossModelJoule
            a LossModelJoule object
        T_op: float
            Conductor operational temperature [degC]
        T_ref: float
            Conductor reference temperature [degC]

        Returns
        ----------
        kr_skin : float
            skin effect coeff for resistance at given frequency and temperature
        """

        if self.parent.parent.parent is None:
            raise Exception("Cannot calculate core losses if simu is not in an Output")
        else:
            output = self.parent.parent.parent

        machine = output.simu.machine
        lamination = machine.stator if "stator" in self.group else machine.rotor
        conductor = lamination.winding.conductor

        # Compute slot average width
        slot = conductor.parent.parent.slot
        b = slot.comp_width()

        # Get number of turns in series per coil
        zt = conductor.parent.Ntcoil

        # check if wires are round or rectangular
        is_round_wire = conductor.is_round_wire()

        # conductor height
        hc0 = conductor.comp_height_wire()
        # conductor width
        bc0 = conductor.comp_width_wire()
        # Number of circumferential adjacent wires
        za = conductor.comp_nb_circumferential_wire()
        # Number of radial adjacent wires
        zp = conductor.comp_nb_radial_wire()
        # Equivalent height of conductor
        hc = zp * hc0

        # Electrical conductivity accounting for temperature increase
        sigma = conductor.cond_mat.elec.get_conductivity(T_op=T_op, T_ref=T_ref)

        # Magnetic permeability
        mu0 = 4 * np.pi * 1e-7
        if conductor.cond_mat.mag is None or conductor.cond_mat.mag.mur_lin is None:
            mur = 1
        else:
            mur = conductor.cond_mat.mag.mur_lin

        # reduced conductor height Eq(5.24) p.270 divided by the frequency + adding relative permeatibility
        ksi = hc * np.sqrt(np.pi * mu0 * mur * sigma * za * bc0 / b)

        if not isinstance(ksi, float):
            # Avoid numerical error with 0
            ksi[ksi == 0] = 1e-4

        # average resistance factor
        if is_round_wire:
            # Use round wire approximation Eq(5.30) p.271
            # --> kr_skin = 1 + 0.59 * ((zt ** 2 - 0.2) / 9) * ksi ** 4
            k = 0.59 * ((zt**2 - 0.2) / 9) * ksi**4
        else:
            # Use rectangular wire approximation Eq(5.29) p.271
            # --> kr_skin = 1 + (zt ** 2 - 0.2) / 9 * ksi ** 4
            k = (zt**2 - 0.2) / 9 * ksi**4

        return k

    # Inlined from Methods.Loss.LossModelJoule.comp_loss
    def comp_loss(self):
        """Calculate joule losses in stator windings

        Parameters
        ----------
        self: LossModelJoule
            a LossModelJoule object

        Returns
        -------
        Pjoule_density : ndarray
            Joule loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """

        if self.parent.parent is None:
            raise ValueError(
                "Cannot calculate joule losses if simu is not in an Output"
            )
        else:
            output = self.parent.parent.parent

        if output.elec is None:
            raise ValueError("Cannot calculate joule losses if OutElec is None")

        if self.parent.is_get_meshsolution and output.mag is None:
            raise ValueError("Cannot calculate joule losses if OutMag is None")

        machine = output.simu.machine
        lam = machine.stator if "stator" in self.group else machine.rotor
        T_op = self.parent.Tsta if "stator" in self.group else self.parent.Trot

        OP = output.elec.OP
        felec = OP.get_felec()

        Rs = lam.comp_resistance_wind(T=T_op)
        qs = lam.winding.qs

        if self.type_skin_effect > 0:
            # Account for skin effect
            k = self.comp_coeff(
                T_op=T_op,
            )
        else:
            k = 0

        # Calculate overall joule losses
        # #TODO if the model is applied to the rotor of an SCIM, use the rotor current computed from the EEC.
        Id_Iq = OP.get_Id_Iq()
        coeff = qs * Rs * (Id_Iq["Id"] ** 2 + Id_Iq["Iq"] ** 2)
        Pjoule = coeff * (1 + k * felec**2)

        per_a = output.geo.per_a
        if output.geo.is_antiper_a:
            per_a *= 2

        Lst = lam.L1

        # Get surface elements for windings
        ms = output.mag.meshsolution
        Se = ms.mesh.get_element_area()[ms.group[self.group]]

        # Constant component and twice the electrical frequency have same joule density values
        freqs = np.array([felec])
        Pjoule_density = np.zeros((freqs.size, Se.size))
        Pjoule_density[0, :] = Pjoule / (per_a * Lst * np.sum(Se))

        A = coeff * k
        B = coeff
        self.coeff_dict = {"2": A, "0": B}

        return Pjoule_density, freqs
