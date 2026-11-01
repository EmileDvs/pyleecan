# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Converter/Convert.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Converter/Convert
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes._frozen import FrozenClass

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Functions.Converter.Utils.ConvertionError import ConvertionError
from pyleecan import __version__
from os import path
from pyleecan.Classes.MachineIPMSM import MachineIPMSM
from pyleecan.Classes.MachineSIPMSM import MachineSIPMSM
from pyleecan.Classes.MachineSCIM import MachineSCIM
from pyleecan.Classes.MachineWRSM import MachineWRSM
from pyleecan.Classes.CondType12 import CondType12
from pyleecan.Classes.CondType11 import CondType11
from pyleecan.Classes.VentilationCirc import VentilationCirc
from pyleecan.Classes.VentilationPolar import VentilationPolar
from pyleecan.Classes.VentilationTrap import VentilationTrap
from pyleecan.Classes.HoleM52 import HoleM52
from pyleecan.Classes.HoleM57 import HoleM57
from pyleecan.Classes.HoleM60 import HoleM60
from pyleecan.Classes.HoleM61 import HoleM61
from pyleecan.Classes.HoleM62 import HoleM62
from pyleecan.Classes.HoleM63 import HoleM63
from pyleecan.Classes.SlotM11 import SlotM11
from pyleecan.Classes.SlotM12 import SlotM12
from pyleecan.Classes.SlotM13 import SlotM13
from pyleecan.Classes.SlotM14 import SlotM14
from pyleecan.Classes.SlotM15 import SlotM15
from pyleecan.Classes.SlotM16 import SlotM16
from pyleecan.Classes.SlotM19 import SlotM19
from pyleecan.Classes.SlotW63 import SlotW63
from pyleecan.Classes.SlotW62 import SlotW62
from pyleecan.Classes.SlotW29 import SlotW29
from pyleecan.Classes.Skew import Skew
from pyleecan.Classes.SlotW11_2 import SlotW11_2
from pyleecan.Classes.SlotW23 import SlotW23
from pyleecan.Classes.SlotW26 import SlotW26
from pyleecan.Classes.SlotW30 import SlotW30
from pyleecan.Classes.SlotW11 import SlotW11
from pyleecan.Classes.SlotW14 import SlotW14
from pyleecan.Classes.SlotW21 import SlotW21
from pyleecan.Classes.Material import Material

import numpy as np
from pyleecan.Classes._check import InitUnKnowClassError


class Convert(FrozenClass):
    """initialisation of conversion abstract"""

    VERSION = 1

    # cf Methods.Converter.Convert.convert_to_other
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

    # cf Methods.Converter.Convert.convert_to_P
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
        file_name_extension = path.basename(file_path)
        self.machine.name = path.splitext(file_name_extension)[0]

        self.get_logger().info("End of conversion, obj machine is create\n\n\n")

        return self.machine

    # cf Methods.Converter.Convert.machine_type.select_IPMSM_rules
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

    # cf Methods.Converter.Convert.machine_type.select_SCIM_rules
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

    # cf Methods.Converter.Convert.machine_type.select_SIPMSM_rules
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

    # cf Methods.Converter.Convert.machine_type.select_WRSM_rules
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

    # cf Methods.Converter.Convert.select_LamSlotWind_rules
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

    # cf Methods.Converter.Convert.select_machine_rules
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

    # cf Methods.Converter.Convert.Step.select_bar_rules
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

    # cf Methods.Converter.Convert.Step.select_conductor_rules
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

    # cf Methods.Converter.Convert.Step.select_duct_rules
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

    # cf Methods.Converter.Convert.Step.select_hole_rules
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

    # cf Methods.Converter.Convert.Step.select_lamination_rules
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

    # cf Methods.Converter.Convert.Step.select_magnet_rules
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

    # cf Methods.Converter.Convert.Step.select_material_rules
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

    # cf Methods.Converter.Convert.Step.select_notch_rules
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

    # cf Methods.Converter.Convert.Step.select_pole_rules
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

    # cf Methods.Converter.Convert.Step.select_skew_rules
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

    # cf Methods.Converter.Convert.Step.select_slot_rotor_rules
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

    # cf Methods.Converter.Convert.Step.select_slot_rules
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

    # cf Methods.Converter.Convert.Step.select_winding_rules
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        other_unit_dict=-1,
        other_dict=-1,
        machine=None,
        rules_list=-1,
        is_P_to_other=False,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "other_unit_dict" in list(init_dict.keys()):
                other_unit_dict = init_dict["other_unit_dict"]
            if "other_dict" in list(init_dict.keys()):
                other_dict = init_dict["other_dict"]
            if "machine" in list(init_dict.keys()):
                machine = init_dict["machine"]
            if "rules_list" in list(init_dict.keys()):
                rules_list = init_dict["rules_list"]
            if "is_P_to_other" in list(init_dict.keys()):
                is_P_to_other = init_dict["is_P_to_other"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.other_unit_dict = other_unit_dict
        self.other_dict = other_dict
        self.machine = machine
        self.rules_list = rules_list
        self.is_P_to_other = is_P_to_other

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Convert_str = ""
        if self.parent is None:
            Convert_str += "parent = None " + linesep
        else:
            Convert_str += "parent = " + str(type(self.parent)) + " object" + linesep
        Convert_str += "other_unit_dict = " + str(self.other_unit_dict) + linesep
        Convert_str += "other_dict = " + str(self.other_dict) + linesep
        if self.machine is not None:
            tmp = self.machine.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Convert_str += "machine = " + tmp
        else:
            Convert_str += "machine = None" + linesep + linesep
        Convert_str += (
            "rules_list = "
            + linesep
            + str(self.rules_list).replace(linesep, linesep + "\t")
            + linesep
        )
        Convert_str += "is_P_to_other = " + str(self.is_P_to_other) + linesep
        return Convert_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.other_unit_dict != self.other_unit_dict:
            return False
        if other.other_dict != self.other_dict:
            return False
        if other.machine != self.machine:
            return False
        if other.rules_list != self.rules_list:
            return False
        if other.is_P_to_other != self.is_P_to_other:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if other._other_unit_dict != self._other_unit_dict:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._other_unit_dict)
                    + ", other="
                    + str(other._other_unit_dict)
                    + ")"
                )
                diff_list.append(name + ".other_unit_dict" + val_str)
            else:
                diff_list.append(name + ".other_unit_dict")
        if other._other_dict != self._other_dict:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._other_dict)
                    + ", other="
                    + str(other._other_dict)
                    + ")"
                )
                diff_list.append(name + ".other_dict" + val_str)
            else:
                diff_list.append(name + ".other_dict")
        if (other.machine is None and self.machine is not None) or (
            other.machine is not None and self.machine is None
        ):
            diff_list.append(name + ".machine None mismatch")
        elif self.machine is not None:
            diff_list.extend(
                self.machine.compare(
                    other.machine,
                    name=name + ".machine",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._rules_list != self._rules_list:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._rules_list)
                    + ", other="
                    + str(other._rules_list)
                    + ")"
                )
                diff_list.append(name + ".rules_list" + val_str)
            else:
                diff_list.append(name + ".rules_list")
        if other._is_P_to_other != self._is_P_to_other:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_P_to_other)
                    + ", other="
                    + str(other._is_P_to_other)
                    + ")"
                )
                diff_list.append(name + ".is_P_to_other" + val_str)
            else:
                diff_list.append(name + ".is_P_to_other")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        if self.other_unit_dict is not None:
            for key, value in self.other_unit_dict.items():
                S += getsizeof(value) + getsizeof(key)
        if self.other_dict is not None:
            for key, value in self.other_dict.items():
                S += getsizeof(value) + getsizeof(key)
        S += getsizeof(self.machine)
        if self.rules_list is not None:
            for value in self.rules_list:
                S += getsizeof(value)
        S += getsizeof(self.is_P_to_other)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        Convert_dict = dict()
        Convert_dict["other_unit_dict"] = (
            self.other_unit_dict.copy() if self.other_unit_dict is not None else None
        )
        Convert_dict["other_dict"] = (
            self.other_dict.copy() if self.other_dict is not None else None
        )
        if self.machine is None:
            Convert_dict["machine"] = None
        else:
            Convert_dict["machine"] = self.machine.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        Convert_dict["rules_list"] = (
            self.rules_list.copy() if self.rules_list is not None else None
        )
        Convert_dict["is_P_to_other"] = self.is_P_to_other
        # The class name is added to the dict for deserialisation purpose
        Convert_dict["__class__"] = "Convert"
        return Convert_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.other_unit_dict is None:
            other_unit_dict_val = None
        else:
            other_unit_dict_val = self.other_unit_dict.copy()
        if self.other_dict is None:
            other_dict_val = None
        else:
            other_dict_val = self.other_dict.copy()
        if self.machine is None:
            machine_val = None
        else:
            machine_val = self.machine.copy()
        if self.rules_list is None:
            rules_list_val = None
        else:
            rules_list_val = self.rules_list.copy()
        is_P_to_other_val = self.is_P_to_other
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            other_unit_dict=other_unit_dict_val,
            other_dict=other_dict_val,
            machine=machine_val,
            rules_list=rules_list_val,
            is_P_to_other=is_P_to_other_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.other_unit_dict = None
        self.other_dict = None
        if self.machine is not None:
            self.machine._set_None()
        self.rules_list = None
        self.is_P_to_other = None

    def _get_other_unit_dict(self):
        """getter of other_unit_dict"""
        return self._other_unit_dict

    def _set_other_unit_dict(self, value):
        """setter of other_unit_dict"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("other_unit_dict", value, "dict")
        self._other_unit_dict = value

    other_unit_dict = property(
        fget=_get_other_unit_dict,
        fset=_set_other_unit_dict,
        doc="""convertion unit file .mot into unit_dict

        :Type: dict
        """,
    )

    def _get_other_dict(self):
        """getter of other_dict"""
        return self._other_dict

    def _set_other_dict(self, value):
        """setter of other_dict"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("other_dict", value, "dict")
        self._other_dict = value

    other_dict = property(
        fget=_get_other_dict,
        fset=_set_other_dict,
        doc="""convertion file .mot in dict

        :Type: dict
        """,
    )

    def _get_machine(self):
        """getter of machine"""
        return self._machine

    def _set_machine(self, value):
        """setter of machine"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "machine"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Machine = import_class("pyleecan.Classes", "Machine", "machine")
            value = Machine()
        check_var("machine", value, "Machine")
        self._machine = value

        if self._machine is not None:
            self._machine.parent = self

    machine = property(
        fget=_get_machine,
        fset=_set_machine,
        doc="""machine pyleecan

        :Type: Machine
        """,
    )

    def _get_rules_list(self):
        """getter of rules_list"""
        return self._rules_list

    def _set_rules_list(self, value):
        """setter of rules_list"""
        if type(value) is int and value == -1:
            value = list()
        check_var("rules_list", value, "list")
        self._rules_list = value

    rules_list = property(
        fget=_get_rules_list,
        fset=_set_rules_list,
        doc="""list differents rules

        :Type: list
        """,
    )

    def _get_is_P_to_other(self):
        """getter of is_P_to_other"""
        return self._is_P_to_other

    def _set_is_P_to_other(self, value):
        """setter of is_P_to_other"""
        check_var("is_P_to_other", value, "bool")
        self._is_P_to_other = value

    is_P_to_other = property(
        fget=_get_is_P_to_other,
        fset=_set_is_P_to_other,
        doc="""booleen to select the direction of conversion

        :Type: bool
        """,
    )
