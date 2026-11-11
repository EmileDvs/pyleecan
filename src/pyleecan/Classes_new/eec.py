# Experimental dataclass generated from Generator/ClassesRef/Simulation/EEC.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
from dataclasses import dataclass, field

from ..Functions_new.Electrical.dqh_transformation import n2dqh_DataTime
from ._import import import_class
from ._pyleecan_class import PyleecanClass
from .magnetics import Magnetics
from .op import OP


@dataclass(eq=False)
class EEC(PyleecanClass):
    """Equivalent Electrical Circuit abstract class

    Attributes
    ----------
    type_skin_effect : int
        Skin effect for resistance and inductance
        Default: 1
    OP : OP or None
        Operating Point
        Default: None
    Tsta : float
        Average stator temperature for operational EEC calculation
        Unit: deg Celsius; Default: 20
    Trot : float
        Average rotor temperature for operational EEC calculation
        Unit: deg Celsius; Default: 20
    Xkr_skinS : float
        Skin effect coefficient for resistances at stator side
        Default: 1
    Xke_skinS : float
        Skin effect coefficient for inductances at stator side
        Default: 1
    Xkr_skinR : float
        Skin effect coefficient for resistances at rotor side
        Default: 1
    Xke_skinR : float
        Skin effect coefficient for inductances at rotor side
        Default: 1
    R1 : float or None
        Stator phase resistance
        Unit: Ohm; Default: None
    fluxlink : Magnetics or None
        Magnetic model for flux linkage calculation
        Default: None
    """

    type_skin_effect: int = 1
    """Skin effect for resistance and inductance"""
    OP: OP | None = field(default=None, metadata={"default_class": "OP"})
    """Operating Point"""
    Tsta: float = 20
    """Average stator temperature for operational EEC calculation"""
    Trot: float = 20
    """Average rotor temperature for operational EEC calculation"""
    Xkr_skinS: float = 1
    """Skin effect coefficient for resistances at stator side"""
    Xke_skinS: float = 1
    """Skin effect coefficient for inductances at stator side"""
    Xkr_skinR: float = 1
    """Skin effect coefficient for resistances at rotor side"""
    Xke_skinR: float = 1
    """Skin effect coefficient for inductances at rotor side"""
    R1: float | None = None
    """Stator phase resistance"""
    fluxlink: Magnetics | None = field(
        default=None, metadata={"default_class": "Magnetics"}
    )
    """Magnetic model for flux linkage calculation"""

    # Inlined from Methods.Simulation.EEC.comp_fluxlinkage
    def comp_fluxlinkage(self, machine=None, OP=None, Nt_tot=None):
        """Compute flux linkage using magnetic model in self.fluxlink

        Parameters
        ----------
        self : EEC
            an EEC object
        machine: Machine
            a Machine object
        OP: OP
            an OP object
        Nt_tot:
            Number of time steps for magnetic calculation

        Returns
        ----------
        Phi_dqh_mean: ndarray
            Flux linkage in dqh frame
        Phi_wind: DataND
            Stator flux linkage Data object
        """

        Simu1 = import_class("Simu1")
        InputCurrent = import_class("InputCurrent")
        MagFEMM = import_class("MagFEMM")

        if self.fluxlink is None:
            mag_model = MagFEMM()
        else:
            mag_model = self.fluxlink.copy()

        self.get_logger().info("Compute flux linkage with FEMM")

        if machine is None:
            machine = self.get_machine_from_parent()

        # Get simulation name and result path
        if isinstance(machine.parent, Simu1) and machine.parent.name not in [None, ""]:
            simu_name = machine.parent.name + "_FluxLinkFEMM"
            path_result = (
                os.path.join(machine.parent.path_result, "FluxLinkFEMM")
                if machine.parent.path_result not in [None, ""]
                else None
            )
        elif machine.name not in [None, ""]:
            simu_name = machine.name + "_FluxLinkFEMM"
            path_result = None
        else:
            simu_name = "FluxLinkFEMM"
            path_result = None

        # Define simulation
        p = machine.get_pole_pair_number()
        simu = Simu1(
            elec=None, name=simu_name, path_result=path_result, machine=machine
        )

        simu.input = InputCurrent(OP=OP, Na_tot=200 * p)
        simu.mag = mag_model
        if Nt_tot is not None:
            simu.input.Nt_tot = Nt_tot
        else:
            simu.input.Nt_tot = int(max(simu.mag.nb_worker * 5, 10) * p)

        # Run Simulation
        out = simu.run()

        # Post-Process
        stator_label = machine.stator.get_label()

        Phi_wind = out.mag.Phi_wind[stator_label]

        Phidqh = n2dqh_DataTime(Phi_wind, phase_dir=out.elec.phase_dir)
        Phi_dqh_mean = Phidqh.get_along("time=mean", "phase")[Phidqh.symbol]

        return Phi_dqh_mean, Phi_wind

    # Inlined from Methods.Simulation.EEC.comp_joule_losses
    def comp_joule_losses(self, out_dict, machine):
        """Compute the electrical Joule losses

        Parameters
        ----------
        self : EEC
            an EEC object
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in comp_parameters of EEC
        machine : Machine
            a Machine object

        Returns
        ------
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in EEC
        """

        raise self.AbstractClassError(
            "EEC is an abstract class, please create one of its daughters."
        )

    # Inlined from Methods.Simulation.EEC.comp_parameters
    def comp_parameters(self):
        """Compute and set the parameter attributes of the EEC that are not set.

        Parameters
        ----------
        self : EEC
            an EEC object

        """

        raise self.AbstractClassError(
            "EEC is an abstract class, please create one of its daughters."
        )

    # Inlined from Methods.Simulation.EEC.comp_R1
    def comp_R1(self, R1_ref=None, T_ref=None):
        """Compute the stator phase resistance for the equivalent electrical circuit

        Parameters
        ----------
        self : EEC
            an EEC object
        R1_ref : float
            reference resistance
        T_ref : float
            reference temperature

        """

        if R1_ref is None:
            # Compute at correct temperature
            machine = self.get_machine_from_parent()
            R1_ref = machine.stator.comp_resistance_wind(T=self.Tsta)
        elif T_ref is None:
            # Assume that the reference match EEC temperature (should not happend)
            pass
        else:  # Adpat the temperature
            # Get stator conductor
            machine = self.get_machine_from_parent()
            CondS = machine.stator.winding.conductor

            # Compute temperature effect on stator side
            Tfact1 = CondS.comp_temperature_effect(T_op=self.Tsta, T_ref=T_ref)
            R1_ref = R1_ref * Tfact1
        # Stator resistance
        self.R1 = R1_ref * self.Xkr_skinS

    # Inlined from Methods.Simulation.EEC.comp_skin_effect
    def comp_skin_effect(self):
        """Compute the skin effect factors (update value in object)

        Parameters
        ----------
        self : EEC
            An EEC objects
        """

        assert self.OP is not None
        assert self.Tsta is not None
        assert self.Trot is not None
        machine = self.get_machine_from_parent()
        CondS = machine.stator.winding.conductor
        felec = self.OP.get_felec()

        # compute skin_effect on stator side
        self.Xkr_skinS = CondS.comp_skin_effect_resistance(
            freq=felec, T_op=self.Tsta, T_ref=20
        )

        self.Xke_skinS = CondS.comp_skin_effect_inductance(
            freq=felec, T_op=self.Tsta, T_ref=20
        )

    # Inlined from Methods.Simulation.EEC.get_machine_from_parent
    def get_machine_from_parent(self):
        """Get machine object from parent

        Parameters
        ----------
        self : EEC
            an EEC object

        Returns
        ----------
        machine : Machine
            a Machine object
        """

        parent = self.parent
        # Try to find simulation parent (output.simu.elec.eec)
        while parent is not None and not hasattr(parent, "machine"):
            parent = parent.parent

        if parent is not None and hasattr(parent, "machine"):
            return parent.machine
        else:
            # Try to find output parent (output.elec.eec)
            parent = self.parent
            while parent is not None and not hasattr(parent, "simu"):
                parent = parent.parent
            if parent is not None:
                return parent.simu.machine
            else:
                return None

    # Inlined from Methods.Simulation.EEC.solve
    def solve(self):
        """Compute the parameters dict for the equivalent electrical circuit

        Parameters
        ----------
        self : EEC
            an EEC object

        Returns
        ------
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in EEC
        """

        raise self.AbstractClassError(
            "EEC is an abstract class, please create one of its daughters."
        )

    # Inlined from Methods.Simulation.EEC.solve_PWM
    def solve_PWM(self, output):
        """Get stator current harmonics due to PWM harmonics

        Parameters
        ----------
        self : EEC
            an EEC object
        output: Output
            An Output object
        is_dqh_freq: bool
            True to consider frequencies in dqh frame

        Returns
        ------
        Is_PWM : DataFreq
            Stator current harmonics as DataFreq
        """
        raise self.AbstractClassError(
            "EEC is an abstract class, please create one of its daughters."
        )

    # Inlined from Methods.Simulation.EEC.update_from_ref
    def update_from_ref(self, LUT_ref):
        """Compute and set the parameter attributes of the EEC from a reference LUT

        Parameters
        ----------
        self : EEC
            an EEC object
        LUT_ref : LUTdq
            a LUTdq object

        """

        raise self.AbstractClassError(
            "EEC is an abstract class, please create one of its daughters."
        )

    class AbstractClassError(Exception):
        pass
