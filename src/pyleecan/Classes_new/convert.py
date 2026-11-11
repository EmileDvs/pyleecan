# Experimental dataclass generated from Generator/ClassesRef/Converter/Convert.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
from dataclasses import dataclass, field
from typing import Any

from .. import __version__
from ._error import ConvertionError
from ._pyleecan_class import PyleecanClass
from .cond_type_11 import CondType11
from .cond_type_12 import CondType12
from .hole_m_52 import HoleM52
from .hole_m_57 import HoleM57
from .hole_m_60 import HoleM60
from .hole_m_61 import HoleM61
from .hole_m_62 import HoleM62
from .hole_m_63 import HoleM63
from .machine import Machine
from .machine_ipmsm import MachineIPMSM
from .machine_scim import MachineSCIM
from .machine_sipmsm import MachineSIPMSM
from .machine_wrsm import MachineWRSM
from .material import Material
from .skew import Skew
from .slot_m_11 import SlotM11
from .slot_m_12 import SlotM12
from .slot_m_13 import SlotM13
from .slot_m_14 import SlotM14
from .slot_m_15 import SlotM15
from .slot_m_16 import SlotM16
from .slot_m_19 import SlotM19
from .slot_w_11 import SlotW11
from .slot_w_11_2 import SlotW11_2
from .slot_w_14 import SlotW14
from .slot_w_21 import SlotW21
from .slot_w_23 import SlotW23
from .slot_w_26 import SlotW26
from .slot_w_29 import SlotW29
from .slot_w_30 import SlotW30
from .slot_w_62 import SlotW62
from .slot_w_63 import SlotW63
from .ventilation_circ import VentilationCirc
from .ventilation_polar import VentilationPolar
from .ventilation_trap import VentilationTrap


@dataclass(eq=False)
class Convert(PyleecanClass):
    """initialisation of conversion abstract

    Attributes
    ----------
    other_unit_dict : dict
        convertion unit file .mot into unit_dict
        Default: -1
    other_dict : dict
        convertion file .mot in dict
        Default: -1
    machine : Machine or None
        machine pyleecan
        Default: None
    rules_list : list
        list differents rules
        Default: []
    is_P_to_other : bool
        booleen to select the direction of conversion
        Default: False
    """

    other_unit_dict: dict[str, Any] = field(default_factory=dict)
    """convertion unit file .mot into unit_dict"""
    other_dict: dict[str, Any] = field(default_factory=dict)
    """convertion file .mot in dict"""
    machine: Machine | None = field(default=None, metadata={"default_class": "Machine"})
    """machine pyleecan"""
    rules_list: list[Any] = field(default_factory=list)
    """list differents rules"""
    is_P_to_other: bool = False
    """booleen to select the direction of conversion"""

    # Inlined from Methods.Converter.Convert.convert_to_other
    def convert_to_other(self, machine):
        """conversion obj machine in dict

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        machine : Machine
            A pyleecan machine

        Returns
        ---------
        other_dict : dict
            A dict with the conversion obj machine
        """
        self.machine = machine
        self.is_P_to_other = True
        self.other_dict = {}
        self.rules_list = []

        self.init_other_unit()

        self.get_logger().info(f"Pyleecan version : {__version__}")
        self.get_logger().info("Conversion obj machine into dict")

        # conversion machine in dict
        self.select_machine_rules()

        # conversion rule in dict
        for rule in self.rules_list:
            try:
                self.other_dict = rule.convert_to_other(
                    self.other_dict, self.machine, self.other_unit_dict
                )
            except Exception as e:
                raise ConvertionError(
                    f"Error while running rule {rule.get_name()}:\n{e}"
                )

        self.get_logger().info("End of conversion, dict is create")

        self.get_logger()

        return self.other_dict

    # Inlined from Methods.Converter.Convert.convert_to_P
    def convert_to_P(self, file_path):
        """Convert a "other" file to a Pyleecan machine

        Parameters
        ----------
        self : Convert
            A Convert object
        file_path : str
            A path to "other" file to convert

        Returns
        ---------
        machine : Machine
            The converted pyleecan machine
        """
        self.is_P_to_other = False  # Select rules direction

        # add log
        self.get_logger().info(f"Pyleecan version : {__version__}")
        self.get_logger().info(f"Path file use to convert : {file_path}")
        # conversion file in dict
        self.get_logger().info("Conversion file .mot into dict")
        self.convert_other_to_dict(file_path)

        # To be sure rules_list is empty
        self.rules_list = []

        self.get_logger().info("Conversion dict into obj machine")

        # conversion dict into machine
        self.select_machine_rules()

        comp = 0
        # rule consersion into obj machine
        for rule in self.rules_list:
            try:
                # Uses polymorphism to choose type rule
                self.machine = rule.convert_to_P(
                    self.other_dict, self.machine, self.other_unit_dict
                )
            except Exception as e:
                self.get_logger().info(
                    f"Error while running rule {rule.get_name()}:\n{e}"
                )
                # raise ConvertionError(f"Error while running rule {rule.get_name()}:\n{e}")
            comp += 1
        # Get machine name from the .mot file name
        # Example :
        #   file_path = \path\to\your\mot\file\SCIM.mot
        #   => self.machine.name = SCIM
        file_name_extension = os.path.basename(file_path)
        self.machine.name = os.path.splitext(file_name_extension)[0]

        self.get_logger().info("End of conversion, obj machine is create\n\n\n")

        return self.machine

    # Inlined from Methods.Converter.Convert.machine_type.select_IPMSM_rules
    def select_IPMSM_rules(self):
        """select step to have rules for motor IPMSM

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object

        """
        # step for stator
        self.select_LamSlotWind_rules(is_stator=True)

        # step for rotor
        is_stator = False
        self.select_hole_rules(is_stator)
        self.select_lamination_rules(is_stator)
        self.select_skew_rules(is_stator)

    # Inlined from Methods.Converter.Convert.machine_type.select_SCIM_rules
    def select_SCIM_rules(self):
        """select step to have rules for motor SCIM

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object

        """
        # step for stator
        self.select_LamSlotWind_rules(is_stator=True)

        # step for rotor
        is_stator = False
        self.select_slot_rotor_rules(is_stator)
        self.select_bar_rules(is_stator)
        self.select_lamination_rules(is_stator)
        self.select_skew_rules(is_stator)

    # Inlined from Methods.Converter.Convert.machine_type.select_SIPMSM_rules
    def select_SIPMSM_rules(self):
        """select step to have rules for motor SIPMSM

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        # step for stator
        self.select_LamSlotWind_rules(is_stator=True)

        # step for rotor
        is_stator = False
        self.select_magnet_rules(is_stator)
        self.select_lamination_rules(is_stator)
        self.select_skew_rules(is_stator)

    # Inlined from Methods.Converter.Convert.machine_type.select_WRSM_rules
    def select_WRSM_rules(self):
        """select step to have rules for motor WRSM

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object

        """
        # step for stator
        self.select_LamSlotWind_rules(is_stator=True)

        # step for rotor
        is_stator = False
        self.select_pole_rules(is_stator)
        self.select_lamination_rules(is_stator)
        self.select_winding_rules(is_stator)
        self.select_conductor_rules(is_stator)
        self.select_skew_rules(is_stator)

    # Inlined from Methods.Converter.Convert.select_LamSlotWind_rules
    def select_LamSlotWind_rules(self, is_stator):
        """select all steps related to lamination

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object

        is_stator : bool
            True lam is stator, False lam is rotor
        """

        self.select_slot_rules(is_stator)
        self.select_lamination_rules(is_stator)
        self.select_winding_rules(is_stator)
        self.select_conductor_rules(is_stator)

    # Inlined from Methods.Converter.Convert.select_machine_rules
    def select_machine_rules(self):
        """select the correct machine to add rules
        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """
        # selection machine type, with implementation in obj machine or in dict
        if self.is_P_to_other:
            self.convert_machine_to_other()
        else:
            self.convert_machine_to_P()
        # add machine rule. Independante of the machine type and of the conversion direction
        self.add_rule_machine_type()

        # selection motor_type
        if isinstance(self.machine, MachineSIPMSM):
            # particularity for SIPMSM with airgap, rule to change machine dimension
            self.select_SIPMSM_machine_dimension()
            self.select_SIPMSM_rules()

        elif isinstance(self.machine, MachineIPMSM):
            self.add_rule_machine_dimension()
            self.select_IPMSM_rules()

        elif isinstance(self.machine, MachineSCIM):
            self.add_rule_machine_dimension()
            self.select_SCIM_rules()

        elif isinstance(self.machine, MachineWRSM):
            self.add_rule_machine_dimension()
            self.select_WRSM_rules()

        else:
            raise NotImplementedError("machine is not implemented yet")

        self.select_material_rules("machine.shaft.mat_type")
        self.select_material_rules("machine.frame.mat_type")

    # Inlined from Methods.Converter.Convert.Step.select_bar_rules
    def select_bar_rules(self, is_stator):
        """selects step to add bar rules

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor

        """

        self.add_rule_rotor_bar(is_stator)

        self.get_logger().error(
            "Approximation for rotor bar conversion. In pyleecan Rotor bar is centered on the slot contrary to MC Rotor bar could be more flexible"
        )

        self.select_material_rules("machine.rotor.ring_mat")

    # Inlined from Methods.Converter.Convert.Step.select_conductor_rules
    def select_conductor_rules(self, is_stator):
        """selects step to add rules for conductor

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor

        """

        # select slot type and add it to obj machine or in dict
        if self.is_P_to_other:
            self.convert_conductor_to_other(is_stator)
        else:
            self.convert_conductor_to_P(is_stator)

        if is_stator:
            conductor = self.machine.stator.winding.conductor
        else:
            conductor = self.machine.rotor.winding.conductor

        # add the correct rule depending on the rotor
        if isinstance(conductor, CondType12):
            self.add_rule_condtype12(is_stator)

        elif isinstance(conductor, CondType11):
            self.add_rule_condtype11(is_stator)

        else:
            raise TypeError("Error type of conductor doesn't exist")

        if is_stator:
            self.select_material_rules("machine.stator.winding.conductor.cond_mat")
            self.get_logger().info("Insulator material, Not Implemented")
            # self.select_material_rules("machine.stator.winding.conductor.ins_mat")

        else:
            self.select_material_rules("machine.rotor.winding.conductor.cond_mat")
            # self.select_material_rules("machine.rotor.winding.conductor.ins_mat")
            self.get_logger().info("Insulator material, Not Implemented")

    # Inlined from Methods.Converter.Convert.Step.select_duct_rules
    def select_duct_rules(self, is_stator):
        """selects step to add rules for duct

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor
        """

        # In Pyleecan :
        #   Multiple set of notch
        #   Multiple type of notch
        # In Motor-Cad :
        #   Multi set of notch
        #   Single type of notch

        # selection of number and add in machine
        if self.is_P_to_other:
            self.convert_duct_to_other(is_stator)
        else:
            self.convert_duct_to_P(is_stator)

        if is_stator:
            axial_vent = self.machine.stator.axial_vent
        else:
            axial_vent = self.machine.rotor.axial_vent

        # add rules based on the number of duct in the machine
        duct_id = 0
        for duct in axial_vent:
            if not isinstance(duct, axial_vent[0].__class__):
                continue

            if isinstance(duct, VentilationCirc):
                self.add_rule_ventilationCirc(is_stator, duct_id)

            elif isinstance(duct, VentilationPolar):
                self.add_rule_ventilationPolar(is_stator, duct_id)

            elif isinstance(duct, VentilationTrap):
                self.add_rule_ventilationTrap(is_stator, duct_id)

            duct_id += 1

    # Inlined from Methods.Converter.Convert.Step.select_hole_rules
    def select_hole_rules(self, is_stator):
        """selects step to add rules for hole and adds hole into obj machine

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor

        """

        # In Pyleecan :
        #   Multiple set of notch
        #   Multiple type of notch
        # In Motor-Cad :
        #   Multi set of notch  (Only for some type)
        #   Single type of notch

        if is_stator:
            raise ValueError("Hole are just in rotor")

        if self.is_P_to_other:
            self.convert_hole_to_other()
        else:
            self.convert_hole_to_P()

        # Number of magnet in Hole
        dict_nb_magnet = {
            "HoleM52": 1,
            "HoleM57": 2,
            "HoleM60": 2,
            "HoleM61": 4,
            "HoleM62": 1,
            "HoleM63": 1,
        }

        # The counter solve the case where self.machine.rotor.hole = [HoleM62, HoleM57, HoleM62]
        hole_id = 0
        for hole in self.machine.rotor.hole:
            # Ensure that all the added rules are for the same slot type
            if not isinstance(hole, self.machine.rotor.hole[0].__class__):
                continue

            number_magnet = dict_nb_magnet[
                self.machine.rotor.hole[0].__class__.__name__
            ]

            # add the correct rule depending on the hole
            if isinstance(hole, HoleM62):
                self.add_rule_holeM62(hole_id)

            elif isinstance(hole, HoleM63):
                self.add_rule_holeM63(hole_id)

            elif isinstance(hole, HoleM61):
                self.add_rule_holeM61(hole_id)

            elif isinstance(hole, HoleM52):
                self.add_rule_holeM52(hole_id)

            elif isinstance(hole, HoleM57):
                self.add_rule_holeM57(hole_id)

            elif isinstance(hole, HoleM60):
                self.add_rule_holeM60(hole_id)

            for number in range(number_magnet):
                self.select_material_rules(
                    f"machine.rotor.hole[{hole_id}].magnet_{number}.mat_type"
                )

                # set type_magnetization at parallel (type_magnetization = 1)
                path = f"self.machine.rotor.hole[{hole_id}].magnet_{number}"
                setattr(
                    eval(path),
                    "type_magnetization",
                    1,
                )

            hole_id += 1

    # Inlined from Methods.Converter.Convert.Step.select_lamination_rules
    def select_lamination_rules(self, is_stator):
        """selects step to add rules for lamination

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor

        """

        self.add_rule_lamination(is_stator)
        self.select_duct_rules(is_stator)
        self.select_notch_rules(is_stator)

        if is_stator:
            self.select_material_rules("machine.stator.mat_type")
        else:
            self.select_material_rules("machine.rotor.mat_type")

    # Inlined from Methods.Converter.Convert.Step.select_magnet_rules
    def select_magnet_rules(self, is_stator):
        """select step to add rules for magnet and convert the magnet

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor

        """

        # In Pyleecan :
        #   Multiple set of notch
        #   Multiple type of notch
        # In Motor-Cad :
        #   Single set of notch
        #   Single type of notch

        # set the machine or dict with the corect conversion of magnet
        if self.is_P_to_other:
            self.convert_magnet_to_other()

        else:
            self.convert_magnet_to_P()

        # add the correct rule depending on the hole

        if isinstance(self.machine.rotor.slot, SlotM11):
            self.add_rule_slotM11()

        elif isinstance(self.machine.rotor.slot, SlotM12):
            self.add_rule_slotM12()

        elif isinstance(self.machine.rotor.slot, SlotM13):
            self.add_rule_slotM13()

        elif isinstance(self.machine.rotor.slot, SlotM14):
            self.add_rule_slotM14()

        elif isinstance(self.machine.rotor.slot, SlotM15):
            self.add_rule_slotM15()

        elif isinstance(self.machine.rotor.slot, SlotM16):
            self.add_rule_slotM16()

        self.select_material_rules("machine.rotor.magnet.mat_type")

    # Inlined from Methods.Converter.Convert.Step.select_material_rules
    def select_material_rules(self, path_P):
        """selects rules for material

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor

        """

        if self.is_P_to_other:
            type_material = self.convert_material_to_other(path_P)
        else:
            type_material = self.convert_material_to_P(path_P)

        if type_material != "":
            self.add_rule_material(path_P, type_material)
            self.add_rule_material_magnetics(path_P, type_material)

    # Inlined from Methods.Converter.Convert.Step.select_notch_rules
    def select_notch_rules(self, is_stator):
        """selects step to add rules for notch

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor
        """
        # In Pyleecan :
        #   Multiple set of notch
        #   Multiple type of notch
        # In Motor-Cad :
        #   Single set of notch
        #   Single type of notch

        # selection of number and add in machine
        if self.is_P_to_other:
            self.convert_notch_to_other(is_stator)
        else:
            self.convert_notch_to_P(is_stator)

        if is_stator:
            notch = self.machine.stator.notch
        else:
            notch = self.machine.rotor.notch

        # add rules based on the number of notch in the machine
        for nb_notch, notch in enumerate(notch):
            if isinstance(notch.notch_shape, SlotM19):
                self.add_rule_notch_slotM19(is_stator, nb_notch)
            else:
                self.get_logger().error("Only rules for slotM19 are defined")

    # Inlined from Methods.Converter.Convert.Step.select_pole_rules
    def select_pole_rules(self, is_stator):
        """selects step to add rules for pole

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor

        """

        if is_stator:
            raise KeyError("Those rules are for rotor slot only")

        if self.is_P_to_other:
            self.convert_pole_to_other()

        else:
            self.convert_pole_to_P()

        slot = self.machine.rotor.slot
        # add the correct rule depending on the pole
        if isinstance(slot, SlotW62):
            self.add_rule_salient_pole_slotW62()

        elif isinstance(slot, SlotW63):
            self.add_rule_parallel_tooth_slotW63()

        elif isinstance(slot, SlotW29):
            self.add_rule_parallel_slot_slotW29()

        self.select_material_rules("machine.rotor.slot.wedge_mat")

    # Inlined from Methods.Converter.Convert.Step.select_skew_rules
    def select_skew_rules(self, is_stator):
        """selects step to add rules for skew

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor

        """

        if self.is_P_to_other:
            self.convert_skew_to_other()
        else:
            self.convert_skew_to_P()

        if isinstance(self.machine.rotor.skew, Skew):
            self.add_rule_skew()

    # Inlined from Methods.Converter.Convert.Step.select_slot_rotor_rules
    def select_slot_rotor_rules(self, is_stator):
        """selects step to add rules for slot in rotor and converts slot

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor

        """
        # In Pyleecan :
        #   Single set of slot
        #   Single type of slot
        # In Motor-Cad :
        #   Single set of slot
        #   Multiple type of slot (possibility to have 2 slot)

        # select slot type and add it to obj machine or in dict
        if self.is_P_to_other:
            self.convert_slot_rotor_to_other()
        else:
            self.convert_slot_rotor_to_P()

        slot = self.machine.rotor.slot
        # add the correct rule depending on the slot
        if isinstance(slot, SlotW11_2):
            self.add_rule_rotor_slotW11_2(is_stator)
        elif isinstance(slot, SlotW23):
            self.add_rule_rotor_slotW23(is_stator)
        elif isinstance(slot, SlotW26):
            self.add_rule_rotor_slotW26(is_stator)
        elif isinstance(slot, SlotW30):
            self.add_rule_rotor_slotW30(is_stator)

        self.select_material_rules("machine.rotor.slot.wedge_mat")

    # Inlined from Methods.Converter.Convert.Step.select_slot_rules
    def select_slot_rules(self, is_stator):
        """selects step to add rules for slot and converts slot

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor

        """

        # In Pyleecan :
        #   Single set of slot
        #   Single type of slot
        # In Motor-Cad :
        #   Single set of slot
        #   Single type of slot

        # select slot type and add it to obj machine or in dict
        if self.is_P_to_other:
            self.convert_slot_to_other()
        else:
            self.convert_slot_to_P()

        slot = self.machine.stator.slot
        # add the correct rule depending on the slot
        if isinstance(slot, SlotW11):
            self.add_rule_slotW11(is_stator)
        elif isinstance(slot, SlotW14):
            self.add_rule_slotW14(is_stator)
        elif isinstance(slot, SlotW21):
            self.add_rule_slotW21(is_stator)
        elif isinstance(slot, SlotW23):
            self.add_rule_slotW23(is_stator)
        elif isinstance(slot, SlotW29):
            self.add_rule_slotW29(is_stator)

        if isinstance(self.machine.stator.slot.wedge_mat, Material):
            self.select_material_rules("machine.stator.slot.wedge_mat")

    # Inlined from Methods.Converter.Convert.Step.select_winding_rules
    def select_winding_rules(self, is_stator):
        """select step to add rules for winding

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor
        """

        if isinstance(self.machine, MachineWRSM) and not is_stator:
            # WRSM has particular winding
            self.machine.rotor.winding.qs = 1
            self.machine.rotor.winding.Nlayer = 2
            self.machine.rotor.winding.is_change_layer = False
            self.machine.rotor.winding.coil_pitch = 1
            self.machine.rotor.winding.Ntcoil = 1
        else:
            self.add_rule_winding(is_stator)
