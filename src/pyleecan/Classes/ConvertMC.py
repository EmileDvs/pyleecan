# File generated according to Generator/ClassesRef/Converter/ConvertMC.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Converter/ConvertMC"""

from os.path import isfile, join

import numpy as np
from pyleecan.Classes.CondType11 import CondType11
from pyleecan.Classes.CondType12 import CondType12
from pyleecan.Classes.CondType13 import CondType13
from pyleecan.Classes.Convert import Convert
from pyleecan.Classes.HoleM52 import HoleM52
from pyleecan.Classes.HoleM57 import HoleM57
from pyleecan.Classes.HoleM60 import HoleM60
from pyleecan.Classes.HoleM61 import HoleM61
from pyleecan.Classes.HoleM62 import HoleM62
from pyleecan.Classes.HoleM63 import HoleM63
from pyleecan.Classes.LamHole import LamHole
from pyleecan.Classes.LamSlotMag import LamSlotMag
from pyleecan.Classes.LamSlotWind import LamSlotWind
from pyleecan.Classes.LamSquirrelCage import LamSquirrelCage
from pyleecan.Classes.MachineIPMSM import MachineIPMSM
from pyleecan.Classes.MachineSCIM import MachineSCIM
from pyleecan.Classes.MachineSIPMSM import MachineSIPMSM
from pyleecan.Classes.MachineWRSM import MachineWRSM
from pyleecan.Classes.Material import Material
from pyleecan.Classes.NotchEvenDist import NotchEvenDist
from pyleecan.Classes.RuleComplex import RuleComplex
from pyleecan.Classes.RuleEquation import RuleEquation
from pyleecan.Classes.RuleSimple import RuleSimple
from pyleecan.Classes.Skew import Skew
from pyleecan.Classes.SlotM11 import SlotM11
from pyleecan.Classes.SlotM12 import SlotM12
from pyleecan.Classes.SlotM13 import SlotM13
from pyleecan.Classes.SlotM14 import SlotM14
from pyleecan.Classes.SlotM15 import SlotM15
from pyleecan.Classes.SlotM16 import SlotM16
from pyleecan.Classes.SlotM19 import SlotM19
from pyleecan.Classes.SlotW11 import SlotW11
from pyleecan.Classes.SlotW11_2 import SlotW11_2
from pyleecan.Classes.SlotW14 import SlotW14
from pyleecan.Classes.SlotW21 import SlotW21
from pyleecan.Classes.SlotW23 import SlotW23
from pyleecan.Classes.SlotW26 import SlotW26
from pyleecan.Classes.SlotW29 import SlotW29
from pyleecan.Classes.SlotW30 import SlotW30
from pyleecan.Classes.SlotW61 import SlotW61
from pyleecan.Classes.SlotW62 import SlotW62
from pyleecan.Classes.SlotW63 import SlotW63
from pyleecan.Classes.VentilationCirc import VentilationCirc
from pyleecan.Classes.VentilationPolar import VentilationPolar
from pyleecan.Classes.VentilationTrap import VentilationTrap
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class ConvertMC(Convert):
    """convertorMC abstract"""

    VERSION = 1

    # cf Methods.Converter.ConvertMC.convert_to_other.convert_conductor_to_other
    def convert_conductor_to_other(self, is_stator):
        """selects step to add rules for conductor

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """
        # selection if conductor is in stator or rotor
        if is_stator:
            conductor_type = self.machine.stator.winding.conductor
        else:
            conductor_type = self.machine.rotor.winding.conductor

        if isinstance(conductor_type, CondType12):
            conductor_name = "AWG_Table"

        elif isinstance(conductor_type, CondType13):
            conductor_name = "Rectangular"
        else:
            raise NotImplementedError(
                f"Type of conductor {conductor_type.__class__.__name__} has not equivalent or has not implement"
            )

        # writting in dict
        if "[Winding_Design]" not in self.other_dict:
            self.other_dict["[Winding_Design]"] = {"Wire_Type": conductor_name}
        else:
            self.other_dict["[Winding_Design]"]["Wire_Type"] = conductor_name

        self.get_logger().info(
            f"Conversion {conductor_type.__class__.__name__} into {conductor_name}"
        )

    # cf Methods.Converter.ConvertMC.convert_to_other.convert_duct_to_other
    def convert_duct_to_other(self, is_stator):
        """selects step to add rules for duct

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor
        """
        # Single type
        # Multi set

        if is_stator:
            lam_name_MC = "Stator"
            axial_vent = self.machine.stator.axial_vent

        else:
            lam_name_MC = "Rotor"
            axial_vent = self.machine.rotor.axial_vent

        # If there is any axial_vent, then do nothing
        if len(axial_vent) == 0:
            return

        elif len(axial_vent) > 1:
            for duct in axial_vent:
                if isinstance(duct, axial_vent[0].__class__):
                    self.get_logger().error(
                        "A Motor-cad machine can only have one type of axial duct"
                    )
                    break

        # selection type duct, single type in Motor-CAD
        if isinstance(axial_vent[0], VentilationCirc):
            # CircularDuct
            duct_MC_name = "Rotor_Circular_Ducts"

        elif isinstance(axial_vent[0], VentilationPolar):
            # Arcduct
            duct_MC_name = "Rotor_Arc_Ducts"

        elif isinstance(axial_vent[0], VentilationTrap):
            # RectangularDuct
            duct_MC_name = "Rotor_Rectangular_Ducts"
        else:
            raise NotImplementedError(
                f"Type of duct {axial_vent[0].__name__} has not equivalent or has not been implementated"
            )

        # writting in dict
        if "[Through_Vent]" not in self.other_dict:
            self.other_dict["[Through_Vent]"] = {
                f"{lam_name_MC}_Duct_Type": duct_MC_name
            }
        else:
            self.other_dict["[Through_Vent]"][f"{lam_name_MC}_Duct_Type"] = duct_MC_name

        self.get_logger().info(
            f"Conversion {axial_vent[0].__name__} into {duct_MC_name}"
        )

    # cf Methods.Converter.ConvertMC.convert_to_other.convert_hole_to_other
    def convert_hole_to_other(self):
        """Selects correct hole and implements it in dict

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object

        Returns
        ---------
        len_hole : int
            The number of hole
        """

        # conversion to motor-cad
        hole = self.machine.rotor.hole[0]
        hole_type = type(hole).__name__

        # Check that every set of hole have the same type
        for current_hole in self.machine.rotor.hole:
            if isinstance(current_hole, hole.__class__):
                self.get_logger().error(
                    "In motor-cad, we have just the possibility to set the same type of hole, so we select the first hole"
                )

        # selection type of Slot
        if isinstance(hole, HoleM52):
            name_hole = "Interior_Flat(web)"

        elif isinstance(hole, HoleM57):
            name_hole = "Interior_V(web)"

        elif isinstance(hole, HoleM60):
            name_hole = "Interior_V(simple)"
            self.get_logger().warning(f"Approximation for W3, Magnet_Post")

        elif isinstance(hole, HoleM61):
            name_hole = "Interior_U-Shape"

        elif isinstance(hole, HoleM62):
            if self.machine.rotor.hole.W0_is_rad == False:
                name_hole = "Embedded_Parallel"
            else:
                name_hole = "Embedded_Radial"

        elif isinstance(hole, HoleM63):
            if hole.top_flat == False:
                name_hole = "Embedded_Breadleaof"
            else:
                name_hole = "Interior_Flat(simple)"

        else:
            raise NotImplementedError(
                f"Type of hole {hole_type} has not equivalent or has not been implementated"
            )

        # writting in dict
        if "[Design_Options]" not in self.other_dict:
            self.other_dict["[Design_Options]"] = {"BPM_Rotor": name_hole}
        else:
            self.other_dict["[Design_Options]"]["BPM_Rotor"] = name_hole

        self.get_logger().info(f"Conversion {hole_type} into {name_hole}")

    # cf Methods.Converter.ConvertMC.convert_to_other.convert_machine_to_other
    def convert_machine_to_other(self):  # conversion to MotorCAD
        """Update other_dict with the correct machine type

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """
        # check the direction of conversion
        motor_type = type(self.machine).__name__

        # selection type of machine

        if isinstance(self.machine, MachineSIPMSM):
            name_machine = "BPM"

        elif isinstance(self.machine, MachineIPMSM):
            name_machine = "BPM"

        elif isinstance(self.machine, MachineSCIM):
            name_machine = "IM"

        elif isinstance(self.machine, MachineWRSM):
            name_machine = "SYNC"

        else:
            raise NotImplementedError(
                f"Machine {motor_type} has not equivalent or has not been implementated"
            )

        self.get_logger().info(f"Conversion {motor_type} into {name_machine}")

        # writting in dict
        if "[Calc_Options]" not in self.other_dict:
            self.other_dict["[Calc_Options]"] = {"Motor_Type": name_machine}
        else:
            self.other_dict["[Calc_Options]"]["Motor_Type"] = name_machine

    # cf Methods.Converter.ConvertMC.convert_to_other.convert_magnet_to_other
    def convert_magnet_to_other(self):
        """Selects correct magnet and implements it in dict

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        # conversion to Motor-CAD
        slot = self.machine.rotor.slot
        magnet_type = type(slot).__name__

        # selection type of Slot
        if isinstance(slot, SlotM11) and self.machine.rotor.slot.H0 == 0:
            if slot.H0 == 0:
                # magnet is on surface of rotor
                name_slot = "Surface_Radial"
            else:
                name_slot = "Inset_Radial"

        elif isinstance(slot, SlotM15):
            if slot.H0 == 0:
                # magnet is on surface of rotor
                name_slot = "Surface_Parallel"
            else:
                name_slot = "Inset_Parallel"

        elif isinstance(slot, SlotM12):
            name_slot = "Inset_Breadleaof"

        elif isinstance(slot, SlotM13):
            name_slot = "Surface_Breadleaof"

        elif isinstance(slot, SlotM16):
            name_slot = "Spoke"

        else:
            raise NotImplementedError(
                f"Type of magnet {magnet_type} has not equivalent or has not been implementated"
            )

        # writting magnet type in other_dict
        if "[Design_Options]" not in self.other_dict:
            self.other_dict["[Design_Options]"] = {"BPM_Rotor": name_slot}
        else:
            self.other_dict["[Design_Options]"]["BPM_Rotor"] = name_slot

        self.get_logger().info(f"Conversion {magnet_type} into {name_slot}")

    # cf Methods.Converter.ConvertMC.convert_to_other.convert_material_to_other
    def convert_material_to_other(self, is_stator, name):
        """Selects correct material and implements it in dict

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        return

    # cf Methods.Converter.ConvertMC.convert_to_other.convert_notch_to_other
    def convert_notch_to_other(self, is_stator):
        """selection step to add rules for notch

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor
        """

        if is_stator:
            len_nocth = len(self.machine.stator.notch)
        else:
            len_nocth = len(self.machine.rotor.notch)

        # If there is any notch, then do nothing
        if len_nocth == 0:
            return

        if not is_stator:
            # A MC machine has the possibility to have a single notch set
            if len_nocth > 1:
                self.get_logger().info(
                    "A Motor-cad machine can only have one notch set"
                )
                self.get_logger().info("Only the first notch set will be added")

            if isinstance(self.machine.rotor.notch[0].notch_shape, SlotM19):
                self.add_rule_notch(is_stator)
                self.get_logger().warning(
                    "Approximation: top of slot is flat in Pyleecan contrary to MC top is rounded"
                )

            else:
                self.get_logger().error("Only the slotM19 can be converted")

        else:
            self.get_logger().error("Motor-CAD machine can't have stator notch")

    # cf Methods.Converter.ConvertMC.convert_to_other.convert_pole_to_other
    def convert_pole_to_other(self):
        """Selects correct pole and implements it in dict
        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        Returns
        ---------
        """
        # conversion to motor-cad
        pole_type = self.machine.rotor.slot

        # selection type of pole
        if isinstance(pole_type, SlotW61):
            name_pole = "Sync_Salient_Pole"

        elif isinstance(pole_type, SlotW62):
            name_pole = "Sync_Parallel_Tooth"

        elif isinstance(pole_type, SlotW29):
            name_pole = "Sync_Parallel_Slot"

        else:
            raise NotImplementedError(
                f"Type of pole {pole_type.__class__.__name__} has not equivalent or has not been implementated"
            )

        # writting in dict
        if "[Design_Options]" not in self.other_dict:
            self.other_dict["[Design_Options]"] = {"Sync_Rotor": name_pole}
        else:
            self.other_dict["[Design_Options]"]["Sync_Rotor"] = name_pole

        self.get_logger().info(
            f"Conversion {pole_type.__class__.__name__} into {name_pole}"
        )

    # cf Methods.Converter.ConvertMC.convert_to_other.convert_skew_to_other
    def convert_skew_to_other(self):
        """Selects correct skew and implements it in dict
        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        Returns
        ---------
        """

        if isinstance(self.machine.rotor.skew, Skew):
            self.add_rule_skew()

    # cf Methods.Converter.ConvertMC.convert_to_other.convert_slot_rotor_to_other
    def convert_slot_rotor_to_other(self):
        """Selects correct slot for rotor and implements it in dict

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """
        # conversion to pyleecan
        slot = self.machine.rotor.slot

        # selection type of Slot
        if isinstance(slot, SlotW11_2):
            name_slot = "Parallel_Tooth"

        elif isinstance(slot, SlotW23):
            name_slot = "Rectangular"

        elif isinstance(slot, SlotW26):
            name_slot = "Round"

        elif isinstance(slot, SlotW30):
            name_slot = "Pear"

        else:
            raise NotImplementedError(
                f"Type of slot {name_slot} has not equivalent or has not been implementated"
            )

        self.get_logger().info(f"Conversion {slot.__class__.__name__} into {name_slot}")

        # writting in dict
        if "[Design_Options]" not in self.other_dict:
            self.other_dict["[Design_Options]"] = {"Top_Bar": name_slot}
        else:
            self.other_dict["[Design_Options]"]["Top_Bar"] = name_slot

    # cf Methods.Converter.ConvertMC.convert_to_other.convert_slot_to_other
    def convert_slot_to_other(self):
        """Selects correct slot and implements it in dict

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        # conversion to pyleecan
        slot = self.machine.stator.slot

        # selection type of Slot
        if isinstance(slot, SlotW11):
            name_slot = "Parallel_Tooth"

        elif isinstance(slot, SlotW14):
            name_slot = "Parallel_tooth_SqB"

        elif isinstance(slot, SlotW21):
            name_slot = "Parallel_Slot"

        elif isinstance(slot, SlotW23):
            name_slot = "Tapered_slot"

        elif isinstance(slot, SlotW29):
            name_slot = "Form_Wound"

        else:
            raise NotImplementedError(
                f"Type of slot {name_slot} has not equivalent or has not been implementated"
            )
        self.get_logger().info(f"Conversion {slot.__class__.__name__} into {name_slot}")

        # writting in dict
        if "[Calc_Options]" not in self.other_dict:
            self.other_dict["[Calc_Options]"] = {"Slot_Type": name_slot}
        else:
            self.other_dict["[Calc_Options]"]["Slot_Type"] = name_slot

    # cf Methods.Converter.ConvertMC.convert_to_other.init_other_unit
    def init_other_unit(self):
        """Selects units and creates a dict with all conversion

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        self.other_unit_dict = {}

        # set length
        # pyleecan unit=m, MC unit = mm
        self.other_unit_dict["m"] = 0.001

        self.other_unit_dict["rad"] = 1
        self.other_unit_dict["deg"] = 180 / np.pi

        # conversion electrical degree
        pole_pair_number = self.machine.get_pole_pair_number()
        self.other_unit_dict["ED"] = (4 / pole_pair_number) * (np.pi / 180)

        self.other_unit_dict[None] = 1  # No unit => No scale
        self.other_unit_dict[""] = 1  # No unit => No scale
        self.other_unit_dict["-"] = 1  # No unit => No scale
        self.other_unit_dict["[]"] = 1  # No unit => No scale

    # cf Methods.Converter.ConvertMC.convert_to_P.convert_conductor_to_P
    def convert_conductor_to_P(self, is_stator):
        """selects step to add rules for conductor in stator

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """
        if is_stator:
            winding = self.machine.stator.winding
        else:
            winding = self.machine.rotor.winding

        conductor_type = self.other_dict["[Winding_Design]"]["Wire_Type"]

        if conductor_type in [
            "AWG_Table",
            "Metric_Table",
            "Diameter_Input",
            "SWG_Table",
        ]:
            winding.conductor = CondType12()

        elif conductor_type == "Rectangular":
            winding.conductor = CondType11()
            winding.conductor.Nwppc_rad = 1
            winding.conductor.Nwppc_tan = 2
        else:
            raise NotImplementedError(
                f"Type of conductor {conductor_type} has not equivalent or has not implement"
            )

        self.get_logger().info(
            f"Conversion {conductor_type} into {winding.conductor.__class__.__name__}"
        )

    # cf Methods.Converter.ConvertMC.convert_to_P.convert_duct_to_P
    def convert_duct_to_P(self, is_stator):
        """selection step to add rules for duct

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True lam is in stator, False lam is in rotor

        """
        # selection of lamination
        if is_stator:
            lam_name = "Stator"
            axial_vent = self.machine.stator.axial_vent

            # selection type layers
            if f"{lam_name}_Duct_Type" in self.other_dict["[Through_Vent]"]:
                type_duct = self.other_dict["[Through_Vent]"][f"{lam_name}_Duct_Type"]
            else:
                type_duct = f"No_{lam_name}_Ducts"

            # Selection type of duct
            if type_duct == f"No_{lam_name}_Ducts":
                return

            else:
                # CircularDuct
                if type_duct == "Circ_Ducts":
                    Ventilation_class = VentilationCirc

                # RectangularDuct
                elif type_duct == "Rect_Ducts":
                    # Error convert is not Implemented
                    self.get_logger().info("Rect_Ducts, Not Implemented")
                    # Ventilation_class = VentilationTrap
                    return

                else:
                    raise NotImplementedError(
                        f"Type of duct {type_duct} has any equivalent in pyleecan or has not been implemented"
                    )

            number_duct = self.other_dict["[Through_Vent]"]["CircularDuctLayers"]

        else:
            lam_name = "Rotor"
            axial_vent = self.machine.rotor.axial_vent

            # selection type layers
            if f"{lam_name}_Duct_Type" in self.other_dict["[Through_Vent]"]:
                type_duct = self.other_dict["[Through_Vent]"][f"{lam_name}_Duct_Type"]
            else:
                type_duct = f"No_{lam_name}_Ducts"

            # Selection type of duct
            if type_duct == f"No_{lam_name}_Ducts":
                self.get_logger().debug(f"No duct to convert at {lam_name}")
                return

            else:
                # CircularDuct
                if type_duct == f"{lam_name}_Circ_Ducts" or type_duct == "Circ_Ducts":
                    Ventilation_class = VentilationCirc

                # Shaft_spoke
                elif type_duct == f"{lam_name}_Shaft_Spoke_Ducts":
                    self.get_logger().info(f"ShaftSpoke ins't define in pyleecan")

                # Arcduct
                elif type_duct == f"{lam_name}_Arc_Ducts":
                    Ventilation_class = VentilationPolar

                # RectangularDuct
                elif type_duct == f"{lam_name}_Rect_Ducts" or type_duct == "Rect_Ducts":
                    # Error convert is not Implemented
                    self.get_logger().info("Rect_Ducts, Not Implemented")
                    return
                    # Ventilation_class = VentilationTrap

                else:
                    raise NotImplementedError(
                        f"Type of duct {type_duct} has any equivalent in pyleecan or has not been implemented"
                    )

                number_duct = self.other_dict["[Through_Vent]"][
                    f"{lam_name}CircularDuctLayers"
                ]

        # Duplication of the sets
        for duct_id in range(number_duct):
            axial_vent.append(Ventilation_class())

        self.get_logger().info(
            f"Conversion {type_duct} into {number_duct} {Ventilation_class.__name__}"
        )

    # cf Methods.Converter.ConvertMC.convert_to_P.convert_hole_to_P
    def convert_hole_to_P(self):
        """Selects correct hole and implements it in obj machine

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object

        Returns
        ---------
        len_hole : int
            The number of hole
        """

        hole_type = self.other_dict["[Design_Options]"]["BPM_Rotor"]

        # Motor-CAD cannot have 2 different types of holes
        # initialisation to set the hole in rotor
        self.machine.rotor = LamHole()
        self.machine.rotor.is_stator = False
        self.machine.rotor.is_internal = True

        # set the hole in obj machine, and add particularity to hole
        if hole_type == "Embedded_Parallel":
            self.machine.rotor.hole.append(HoleM62())
            self.machine.rotor.hole[0].W0_is_rad = False

        elif hole_type == "Embedded_Radial":
            self.machine.rotor.hole.append(HoleM62())
            self.machine.rotor.hole[0].W0_is_rad = True

        elif hole_type == "Embedded_Breadloaf":
            self.machine.rotor.hole.append(HoleM63())
            self.machine.rotor.hole[0].top_flat = False

        elif hole_type == "Interior_Flat_Simple":
            self.machine.rotor.hole.append(HoleM63())
            self.machine.rotor.hole[0].top_flat = True
            self.get_logger().warning(
                f"HoleM63 : Approximation for H1, Pole Arc isn't present in Pyleecan"
            )

        elif hole_type == "Interior_Flat_Web":
            self.machine.rotor.hole.append(HoleM52())
            self.machine.rotor.hole[0].H2 = 0

        # possibility to have many set for the same Hole
        elif hole_type == "Interior_VSimple":
            number_hole = self.other_dict["[Dimensions]"]["VMagnet_Layers"]
            for hole_id in range(number_hole):
                self.machine.rotor.hole.append(HoleM60())

        elif hole_type == "Interior_VShape":
            number_hole = self.other_dict["[Dimensions]"]["VMagnet_Layers"]
            for hole_id in range(number_hole):
                self.machine.rotor.hole.append(HoleM57())
                self.get_logger().warning(
                    "HoleM57 : Approximation check the settings for HoleM57"
                )

        elif hole_type == "Interior_UShape":
            number_hole = self.other_dict["[Dimensions]"]["Magnet_Layers"]
            for hole_id in range(number_hole):
                self.machine.rotor.hole.append(HoleM61())

        else:
            raise NotImplementedError(
                f"Type of hole {hole_type} has not equivalent in pyleecan or has not been implementated"
            )

        # writing exception/approximation for Hole
        if isinstance(self.machine.rotor.hole[0], HoleM60):
            self.get_logger().warning(f"HoleM60 : Approximation for W3, Magnet_Post")

        if isinstance(self.machine.rotor.hole[0], HoleM63):
            self.get_logger().warning(f"HoleM63 : Approximation for W0")

        if isinstance(self.machine.rotor.hole[0], HoleM57):
            self.get_logger().warning(
                f"HoleM57 : Approximation Pole Arc has not equivalent in pyleecan "
            )

        self.get_logger().info(
            f"Conversion {hole_type} into {type(self.machine.rotor.hole[0]).__name__}"
        )

    # cf Methods.Converter.ConvertMC.convert_to_P.convert_machine_to_P
    def convert_machine_to_P(self):
        """Update machine with the correct machine type

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """
        # conversion to Pyleecan
        motor_type = self.other_dict["[Calc_Options]"]["Motor_Type"]
        magnet_type = self.other_dict["[Design_Options]"]["BPM_Rotor"]

        # select machine type abd create it
        if motor_type == "BPM":
            if magnet_type in [
                "Surface_Radial",
                "Surface_Parallel",
                "Surface_Breadloaf",
                "Inset_Radial",
                "Inset_Parallel",
                "Inset_Breadloaf",
            ]:
                self.machine = MachineSIPMSM()
            else:
                # "Embedded_Parallel"
                # "Embedded_Radial"
                # "Embedded_Breadleaof"
                # "Interior_Flat(simple)"
                # "Interior_Flat(web)"
                # "Interior_V(simple)"
                # "Interior_V(web)"
                # "Interior_U-Shape"

                self.machine = MachineIPMSM()

        elif motor_type == "IM":
            self.machine = MachineSCIM()

        elif motor_type == "SYNC":
            self.machine = MachineWRSM()

        else:
            # exception if machine as not an equivalent in pyleecan
            raise NotImplementedError(
                f"Machine {motor_type} has not equivalent in pyleecan or has not been implementated"
            )

        self.get_logger().info(
            f"Conversion {motor_type} into {type(self.machine).__name__}"
        )

    # cf Methods.Converter.ConvertMC.convert_to_P.convert_magnet_to_P
    def convert_magnet_to_P(self):
        """Selects correct magnet and implements it in obj machine

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """
        # conversion to pyleecan
        magnet_type = self.other_dict["[Design_Options]"]["BPM_Rotor"]

        # initialisation to set the slot in stator
        self.machine.rotor = LamSlotMag()

        # set the slot in obj machine, and add particularity
        if magnet_type == "Surface_Radial":
            self.machine.rotor.slot = SlotM14()
            self.machine.rotor.slot.H0 = 0  # slot is on surface

        elif magnet_type == "Surface_Parallel":
            self.machine.rotor.slot = SlotM15()
            self.machine.rotor.slot.H0 = 0  # slot is on surface

        elif magnet_type == "Surface_Breadloaf":
            self.machine.rotor.slot = SlotM13()
            self.machine.rotor.slot.H0 = 0  # slot is on surface

        elif magnet_type == "Inset_Radial":
            self.machine.rotor.slot = SlotM11()

        elif magnet_type == "Inset_Parallel":
            self.machine.rotor.slot = SlotM15()
            self.machine.rotor.slot.H0 = 0.001  # To pass the check for inset parallel
            self.get_logger().warning(
                "Approximation for slotM15 hasn't equivalent in Pyleecan"
            )

        elif magnet_type == "Inset_Breadloaf":
            self.machine.rotor.slot = SlotM12()

        elif magnet_type == "Spoke":
            self.machine.rotor.slot = SlotM16()

        else:
            raise NotImplementedError(
                f"type of magnet {magnet_type} has not equivalent in pyleecan or has not been implementated"
            )

        self.machine.rotor.is_stator = False
        self.machine.rotor.is_internal = True
        other_value = self.other_dict["[Dimensions]"]["Pole_Number"]
        self.machine.rotor.set_pole_pair_number(other_value // 2)

        self.get_logger().info(
            f"Conversion {magnet_type} into {type(self.machine.rotor.slot).__name__}"
        )

    # cf Methods.Converter.ConvertMC.convert_to_P.convert_material_to_P
    def convert_material_to_P(self, path_P):
        """Selects correct material path and return path in file.mot

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object

        Returns
        ---------
        material_path : string
            Path to select material in file .mot
        """

        # creation material dict
        dict_material = {
            "machine.shaft.mat_type": ("Material_Shaft_[A]"),
            "machine.frame.mat_type": (""),  # Material_Housing_Active
            "machine.rotor.slot.wedge_mat": ("Material_RotorWedge"),
            "machine.rotor.winding.conductor.cond_mat": ("Material_Copper_-_Active"),
            "machine.rotor.winding.conductor.ins_mat": (""),
            "machine.rotor.mat_type": ("Material_Rotor_Lam_Tooth"),
            "machine.rotor.ring_mat": ("Material_Rotor_Cage_Top"),
            "machine.stator.slot.wedge_mat": ("Material_SlotWedge"),
            "machine.rotor.magnet.mat_type": ("Material_Magnet"),
            "machine.stator.mat_type": ("Material_Stator_Lam_Tooth"),
            "machine.stator.winding.conductor.cond_mat": ("Material_Copper_-_Active"),
            "machine.stator.winding.conductor.ins_mat": (""),
        }

        if "[" in path_P:
            path_P_split = path_P.split("[")
            # check if material is a hole
            if path_P_split[0] == "machine.rotor.hole":
                material_path = "Material_Magnet"
            else:
                IndexError("Problem in material path")

        # select the correct position of material into dict
        else:
            material_path = dict_material[path_P]

        if material_path != "":
            try:
                material_path = self.other_dict["[Material]"][material_path]
            except:
                material_path = ""

        return material_path

    # cf Methods.Converter.ConvertMC.convert_to_P.convert_notch_to_P
    def convert_notch_to_P(self, is_stator):
        """selects step to add rules for notch

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : bool
            True slot is in stator, False slot is in rotor
        """
        if not is_stator:
            # In .mot file :
            #   If the machine have notch => PoleNotchDepth > 1
            #   If the machine have any notch => PoleNotchDepth do not exist
            #                                    OR PoleNotchDepth = 0
            if "PoleNotchDepth" in self.other_dict["[Dimensions]"]:
                Notch_depth = self.other_dict["[Dimensions]"]["PoleNotchDepth"]
            else:
                Notch_depth = 0

            if Notch_depth != 0:
                # MC has one set of notch and just equivalent of slotM19
                self.machine.rotor.notch.append(NotchEvenDist())
                self.machine.rotor.notch[0].notch_shape = SlotM19()

                self.get_logger().info("Add notch for rotor")
                self.get_logger().warning(
                    "Approximation: top of slot is flat in Pyleecan contrary to MC top is rounded"
                )
        else:
            self.get_logger().error("MC machine can't have notch in stator")

    # cf Methods.Converter.ConvertMC.convert_to_P.convert_other_to_dict
    def convert_other_to_dict(self, file_path):
        """converts file .mot into dict and creates other_unit_dict

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        file_path : str
            Path to the file to convert

        Returns
        ----------
        other_dict: dict
            dict with param present in file .mot without unit
        other_unit_dict : dict
            dict with unit to make conversion (key: unit family, value: factor)
        """

        list_path = file_path.split(".")
        if not list_path[-1] == "mot":
            raise ValueError("The file is not a .mot, please select a .mot to convert")
        if not isfile(file_path):
            raise ValueError(f"Error: This file doesn't exist: {file_path}")
        else:
            with open(join(file_path, file_path)) as file:
                ####
                # .mot files are organized as follow:
                # the file is compose different part, with a title into [], and after a list of value, after restart an other part, we have a space
                # Example :
                # [Dimensions]
                # Stator_Lam_Dia=130
                # Stator_Bore=80
                # Airgap=1

                # [Design_Options]
                # BPM_Rotor=Surface_Radial
                # Top_Bar=Round
                # Bottom_Bar=Rectangular
                ####

                ####
                # other_dict = {
                #   [Dimensions] = {
                #        Stator_Lam_Dia : 130
                #        Stator_Bore : 80
                #        Airgap : 1
                #       }
                #
                #   [Design_Options] = {
                #       BPM_Rotor : Surface_Radial
                #       Top_Bar : Round
                #       Bottom_Bar : Rectangular
                #       }
                # }
                ####

                other_dict = {}
                for line in file:
                    # deleted \n in line
                    line = line.strip("\n")
                    # separation different part like .mot
                    if line == "":
                        pass
                    elif line[0] == "[":
                        temp_dict = {}
                        other_dict[line] = temp_dict

                    else:
                        # lb = line before =
                        lb = line.split("=")
                        value = lb[1]

                        # changement type after equal (value)
                        if self.isint(value):
                            value = int(value)
                        elif value == "True":
                            value = True
                        elif value == ("False"):
                            value = False
                        elif self.isfloat(value):
                            value = float(value)

                        if value == (""):
                            pass
                        else:
                            temp_dict[lb[0]] = value

                # Extract unit dict
                other_unit_dict_temp = other_dict["[Units]"]
                other_unit_dict = {}

                # set length
                unit = other_unit_dict_temp["Units_Length"]
                if unit == "mm":
                    other_unit_dict["m"] = 0.001
                    # we want to have m so we need to multiply by 0.001
                elif unit == "m":
                    other_unit_dict["m"] = 1

                other_unit_dict["rad"] = 1
                other_unit_dict["deg"] = np.pi / 180

                pole_number = other_dict["[Dimensions]"]["Pole_Number"]

                other_unit_dict["ED"] = (2 / pole_number) * (np.pi / 180)
                # we want to have rad so we need to multiply by 2/pole_number
                other_unit_dict[None] = 1  # No unit => No scale
                other_unit_dict[""] = 1  # No unit => No scale
                other_unit_dict["-"] = 1  # No unit => No scale
                other_unit_dict["[]"] = 1  # No unit => No scale

                self.other_dict = other_dict
                self.other_unit_dict = other_unit_dict

    @staticmethod
    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def isint(value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    # cf Methods.Converter.ConvertMC.convert_to_P.convert_pole_to_P
    def convert_pole_to_P(self):
        """Selects correct pole and implements it in obj machine

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object

        """

        pole_type = self.other_dict["[Design_Options]"]["Sync_Rotor"]

        # initialisation to set the pole in rotor
        self.machine.rotor = LamSlotWind()
        self.machine.rotor.is_stator = False
        self.machine.rotor.is_internal = True

        # set the pole in obj machine, and add particularity to pole
        if pole_type == "Sync_Salient_Pole":
            self.machine.rotor.slot = SlotW62()

        elif pole_type == "Sync_Parallel_Tooth":
            self.machine.rotor.slot = SlotW63()

        elif pole_type == "Sync_Parallel_Slot":
            self.machine.rotor.slot = SlotW29()
            self.machine.rotor.slot.H1 = 0
            self.get_logger().info(
                "Approximation for tip angle, not possible in pyleecan"
            )

        else:
            raise NotImplementedError(
                f"Type of pole {pole_type} has not equivalent in pyleecan or has not been implementated"
            )

        self.get_logger().info(
            f"Conversion {pole_type} into {type(self.machine.rotor.slot).__name__}"
        )

        if isinstance(pole_type, SlotW63):
            self.get_logger().warning(
                f"SlotW62 : Approximation for W2 has not equivalent in Motor-CAD"
            )

    # cf Methods.Converter.ConvertMC.convert_to_P.convert_skew_to_P
    def convert_skew_to_P(self):
        """Selects correct skew and implements it in obj machine

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """
        # conversion to pyleecan
        if "SkewType" in self.other_dict["[Magnetics]"]:
            skew_type = self.other_dict["[Magnetics]"]["SkewType"]
        else:
            skew_type = 0

        if skew_type == 2:
            # initialisation to set the skew in rotor
            self.machine.rotor.skew = Skew()

            self.get_logger().info(f"Conversion skew ")

    # cf Methods.Converter.ConvertMC.convert_to_P.convert_slot_rotor_to_P
    def convert_slot_rotor_to_P(self):
        """Selects correct slot for rotor and implements it in obj machine

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """
        slot_type = self.other_dict["[Design_Options]"]["Top_Bar"]

        # initialisation to set the slot in rotor
        self.machine.rotor = LamSquirrelCage()
        self.machine.rotor.is_stator = False
        self.machine.rotor.is_internal = True

        # set the slot in obj machine, and add particularity
        if slot_type == "Parallel_Tooth":
            self.machine.rotor.slot = SlotW11_2()
            self.machine.rotor.slot.is_cstt_tooth = True
            self.machine.rotor.slot.H1_is_rad = True

        elif slot_type == "Round":
            self.machine.rotor.slot = SlotW26()
            self.machine.rotor.slot.H1 = 0
            self.machine.rotor.slot.R2 = 0

        elif slot_type == "Rectangular":
            self.machine.rotor.slot = SlotW23()
            self.machine.rotor.slot.H1_is_rad = True

        elif slot_type == "Pear":
            self.machine.rotor.slot = SlotW30()

        else:
            raise NotImplementedError(
                f"Type of slot {slot_type} has not equivalent or has not been implementated"
            )

        self.get_logger().info(
            f"Conversion {slot_type} into {type(self.machine.rotor.slot).__name__}"
        )

        # Motor-Cad has possibility to have 2 slots, nested one on top of the other
        # We have dicided to select just the top_BAR
        if self.other_dict["[Design_Options]"]["Bottom_Bar"] != None:
            self.get_logger().error(
                f"Conversion with 2 slot in rotor is not accept in Pyleecan"
            )

    # cf Methods.Converter.ConvertMC.convert_to_P.convert_slot_to_P
    def convert_slot_to_P(self):
        """Selects correct slot and implements it in obj machine

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """
        slot_type = self.other_dict["[Calc_Options]"]["Slot_Type"]

        # initialisation to set the slot in stator
        dict_machine = self.machine.stator.as_dict()
        self.machine.stator = LamSlotWind(init_dict=dict_machine)

        # set the slot in obj machine, and add particularity
        if slot_type == "Parallel_Tooth":
            if self.other_dict["[Dimensions]"]["Slot_Corner_Radius"] == 0:
                self.machine.stator.slot = SlotW23()
                self.machine.stator.slot.is_cstt_tooth = True
                self.machine.stator.slot.H1_is_rad = True
                self.machine.stator.is_internal = False

            else:
                self.machine.stator.slot = SlotW11()
                self.machine.stator.slot.is_cstt_tooth = True
                self.machine.stator.slot.H1_is_rad = True
                self.machine.stator.is_internal = False
                self.get_logger().warning(
                    "Approximation: top of slot is flat in Pyleecan contrary to MC top is rounded"
                )

        elif slot_type == "Parallel_Tooth_SqBase":
            self.machine.stator.slot = SlotW14()
            self.machine.stator.is_internal = False
            self.machine.stator.slot.H1_is_rad = True
            self.machine.stator.slot.wedge_type = 1

        elif slot_type == "Parallel_Slot":
            self.machine.stator.slot = SlotW21()
            self.machine.stator.slot.H1_is_rad = True
            self.machine.stator.is_internal = False

        elif slot_type == "Tapered_Slot":
            if self.other_dict["[Dimensions]"]["Slot_Corner_Radius"] == 0:
                self.machine.stator.slot = SlotW23()
                self.machine.stator.slot.is_cstt_tooth = False
                self.machine.stator.slot.H1_is_rad = True
                self.machine.stator.is_internal = False

            else:
                self.machine.stator.slot = SlotW11()
                self.machine.stator.slot.is_cstt_tooth = False
                self.machine.stator.slot.H1_is_rad = True
                self.machine.stator.is_internal = False
                self.get_logger().warning(
                    "Approximation: top of slot is flat in Pyleecan contrary to MC top is rounded"
                )

        elif slot_type == "Form_Wound":
            self.machine.stator.slot = SlotW29()
            self.machine.stator.is_internal = False
            self.machine.stator.slot.wedge_type = 1

        elif slot_type == "Slotless":
            self.get_logger().error("Slotless has not equivalent in Pyleecan")

        else:
            raise NotImplementedError(
                f"type of slot {slot_type} has not equivalent in pyleecan or has not been implementated"
            )

        self.get_logger().info(
            f"Conversion {slot_type} into {type(self.machine.stator.slot).__name__}"
        )

        # selection type of wedge
        if "Wedge_Model" in self.other_dict["[Winding_Design]"]:
            wedge = self.other_dict["[Winding_Design]"]["Wedge_Model"]

        else:
            wedge = "Air"

        # set the correct wedge
        if wedge == "Air":
            self.machine.stator.slot.wedge_mat = None
        elif wedge == "Wedge":
            self.machine.stator.slot.wedge_mat = Material()
        elif wedge == "Wound_Space":
            self.machine.stator.slot.wedge_mat = None
            self.get_logger().info(
                f"Conversion Wound_Space for {type(self.machine.stator.slot).name} has no equivalent in pyleecan. No wedge defined in the converted slot"
            )

        else:
            self.machine.stator.slot.wedge_mat = None
            self.get_logger().warning(
                f"Error for conversion of wedge (unknow wedge type: {wedge}). No wedge defined in the converted slot"
            )

    # cf Methods.Converter.ConvertMC.Rules.add_rule_machine_dimension
    def add_rule_machine_dimension(self):
        """Create and adapt all the rules related to machine dimensions (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Stator_Bore"],
                P_obj_path="machine.stator.Rint",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Stator_Lam_Dia"],
                P_obj_path="machine.stator.Rext",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

        # shaft

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Shaft_Dia"],
                P_obj_path="machine.rotor.Rint",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Shaft_Dia"],
                P_obj_path="machine.shaft.Drsh",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        if self.is_P_to_other == True:
            self.rules_list.append(
                RuleEquation(
                    param=[
                        {
                            "src": "other",
                            "path": ["[Dimensions]", "Airgap"],
                            "variable": "y",
                        },
                        {
                            "src": "pyleecan",
                            "path": "machine.rotor.Rext",
                            "variable": "a",
                        },
                        {
                            "src": "pyleecan",
                            "path": "machine.stator.Rint",
                            "variable": "b",
                        },
                    ],
                    unit_type="m",
                    equation="y= b-a",
                    file_name=__file__,
                )
            )

        else:
            self.rules_list.append(
                RuleEquation(
                    param=[
                        {
                            "src": "other",
                            "path": ["[Dimensions]", "Stator_Bore"],
                            "variable": "y",
                        },
                        {
                            "src": "other",
                            "path": ["[Dimensions]", "Airgap"],
                            "variable": "a",
                        },
                        {
                            "src": "pyleecan",
                            "path": "machine.rotor.Rext",
                            "variable": "x",
                        },
                    ],
                    unit_type="m",
                    equation="y/2-a= x ",
                    file_name=__file__,
                )
            )

        # frame

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Motor_Length"],
                P_obj_path="machine.frame.Lfra",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Stator_Lam_Dia"],
                P_obj_path="machine.frame.Rint",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Housing_Dia"],
                P_obj_path="machine.frame.Rext",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.add_rule_machine_dimension_surface_magnet
    def add_rule_machine_dimension_surface_magnet(self):
        """Create and adapt all the rules related to machine dimensions (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Stator_Bore"],
                P_obj_path="machine.stator.Rint",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Stator_Lam_Dia"],
                P_obj_path="machine.stator.Rext",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

        # shaft
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Shaft_Dia"],
                P_obj_path="machine.rotor.Rint",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Shaft_Dia"],
                P_obj_path="machine.shaft.Drsh",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        if self.is_P_to_other == True:
            self.rules_list.append(
                RuleEquation(
                    param=[
                        {
                            "src": "other",
                            "path": ["[Dimensions]", "Airgap"],
                            "variable": "y",
                        },
                        {
                            "src": "pyleecan",
                            "path": "machine.rotor.Rext",
                            "variable": "a",
                        },
                        {
                            "src": "pyleecan",
                            "path": "machine.stator.Rint",
                            "variable": "b",
                        },
                        {
                            "src": "pyleecan",
                            "path": "machine.rotor.slot.H1",
                            "variable": "c",
                        },
                    ],
                    unit_type="m",
                    equation="y= b-a-c ",
                    file_name=__file__,
                )
            )

        if not self.is_P_to_other:
            self.rules_list.append(
                RuleEquation(
                    param=[
                        {
                            "src": "other",
                            "path": ["[Dimensions]", "Stator_Bore"],
                            "variable": "y",
                        },
                        {
                            "src": "other",
                            "path": ["[Dimensions]", "Airgap"],
                            "variable": "a",
                        },
                        {
                            "src": "other",
                            "path": ["[Dimensions]", "Magnet_Thickness"],
                            "variable": "b",
                        },
                        {
                            "src": "pyleecan",
                            "path": "machine.rotor.Rext",
                            "variable": "x",
                        },
                    ],
                    unit_type="m",
                    equation="y/2-a-b= x ",
                    file_name=__file__,
                )
            )
        else:
            self.rules_list.append(
                RuleEquation(
                    param=[
                        {
                            "src": "other",
                            "path": ["[Dimensions]", "Stator_Bore"],
                            "variable": "y",
                        },
                        {
                            "src": "other",
                            "path": ["[Dimensions]", "Airgap"],
                            "variable": "a",
                        },
                        {
                            "src": "pyleecan",
                            "path": "machine.rotor.slot.H1",
                            "variable": "b",
                        },
                        {
                            "src": "pyleecan",
                            "path": "machine.rotor.Rext",
                            "variable": "x",
                        },
                    ],
                    unit_type="m",
                    equation="y/2-a-b= x ",
                    file_name=__file__,
                )
            )

        # frame
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Motor_Length"],
                P_obj_path="machine.frame.Lfra",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Stator_Lam_Dia"],
                P_obj_path="machine.frame.Rint",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Housing_Dia"],
                P_obj_path="machine.frame.Rext",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.add_rule_machine_type
    def add_rule_machine_type(self):
        """Create and adapt all the rules related to machine type
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        self.rules_list.append(
            RuleComplex(fct_name="set_pole_pair_number", folder="MotorCAD")
        )

    # cf Methods.Converter.ConvertMC.Rules.add_rule_material
    def add_rule_material(self, path_P, material):
        """Create and adapt all the rules related to machine dimensions (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        # elec
        self.rules_list.append(
            RuleSimple(
                other_key_list=[f"[{material}]", "ElectricalResistivity"],
                P_obj_path=f"{path_P}.elec.rho",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=[f"[{material}]", "TempCoefElectricalResistivity"],
                P_obj_path=f"{path_P}.elec.alpha",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        # Mechanics
        self.rules_list.append(
            RuleSimple(
                other_key_list=[f"[{material}]", "Density"],
                P_obj_path=f"{path_P}.struct.rho",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        if "PoissonsRatio" in self.other_dict[f"[{material}]"]:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=[f"[{material}]", "PoissonsRatio"],
                    P_obj_path=f"{path_P}.struct.nu_xy",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[f"[{material}]", "PoissonsRatio"],
                    P_obj_path=f"{path_P}.struct.nu_xz",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[f"[{material}]", "PoissonsRatio"],
                    P_obj_path=f"{path_P}.struct.nu_yz",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

        if "YoungsCoefficient" in self.other_dict[f"[{material}]"]:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=[f"[{material}]", "YoungsCoefficient"],
                    P_obj_path=f"{path_P}.struct.Ex",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )
            self.rules_list.append(
                RuleSimple(
                    other_key_list=[f"[{material}]", "YoungsCoefficient"],
                    P_obj_path=f"{path_P}.struct.Ey",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )
            self.rules_list.append(
                RuleSimple(
                    other_key_list=[f"[{material}]", "YoungsCoefficient"],
                    P_obj_path=f"{path_P}.struct.Ez",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

        if self.is_P_to_other == False:
            if (
                "YoungsCoefficient" in self.other_dict[f"[{material}]"]
                and "PoissonsRatio" in self.other_dict[f"[{material}]"]
            ):
                # into file .mot
                # a = YoungsCoefficient
                # b = PoissonsRatio
                # into Pyleecan
                # x = Gxy
                self.rules_list.append(
                    RuleEquation(
                        param=[
                            {
                                "src": "other",
                                "path": [f"[{material}]", "YoungsCoefficient"],
                                "variable": "a",
                            },
                            {
                                "src": "other",
                                "path": [f"[{material}]", "PoissonsRatio"],
                                "variable": "b",
                            },
                            {
                                "src": "pyleecan",
                                "path": f"{path_P}.struct.Gxy",
                                "variable": "x",
                            },
                        ],
                        unit_type="",
                        equation="a/(2*(1+b))=x",
                        file_name=__file__,
                    )
                )
                # into file .mot
                # a = YoungsCoefficient
                # b = PoissonsRatio
                # into Pyleecan
                # x = Gxz
                self.rules_list.append(
                    RuleEquation(
                        param=[
                            {
                                "src": "other",
                                "path": [f"[{material}]", "YoungsCoefficient"],
                                "variable": "a",
                            },
                            {
                                "src": "other",
                                "path": [f"[{material}]", "PoissonsRatio"],
                                "variable": "b",
                            },
                            {
                                "src": "pyleecan",
                                "path": f"{path_P}.struct.Gxz",
                                "variable": "x",
                            },
                        ],
                        unit_type="",
                        equation="a/(2*(1+b))=x",
                        file_name=__file__,
                    )
                )

                # into file .mot
                # a = YoungsCoefficient
                # b = PoissonsRatio
                # into Pyleecan
                # x = Gyz
                self.rules_list.append(
                    RuleEquation(
                        param=[
                            {
                                "src": "other",
                                "path": [f"[{material}]", "YoungsCoefficient"],
                                "variable": "a",
                            },
                            {
                                "src": "other",
                                "path": [f"[{material}]", "PoissonsRatio"],
                                "variable": "b",
                            },
                            {
                                "src": "pyleecan",
                                "path": f"{path_P}.struct.Gyz",
                                "variable": "x",
                            },
                        ],
                        unit_type="",
                        equation="a/(2*(1+b))=x",
                        file_name=__file__,
                    )
                )

    # cf Methods.Converter.ConvertMC.Rules.add_rule_material_magnetics
    def add_rule_material_magnetics(self, path_P, material):
        """Create and adapt all the rules related to machine dimensions (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        if "MagneturValue" in self.other_dict[f"[{material}]"]:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=[f"[{material}]", "MagneturValue"],
                    P_obj_path=f"{path_P}.mag.mur_lin",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

        if "MagnetBrValue" in self.other_dict[f"[{material}]"]:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=[f"[{material}]", "MagnetBrValue"],
                    P_obj_path=f"{path_P}.mag.Brm20",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

        if "MagnetTempCoefBr" in self.other_dict[f"[{material}]"]:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=[f"[{material}]", "MagnetTempCoefBr"],
                    P_obj_path=f"{path_P}.mag.alpha_Br",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

        if "LaminationThickness" in self.other_dict[f"[{material}]"]:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=[f"[{material}]", "LaminationThickness"],
                    P_obj_path=f"{path_P}.mag.Wlam",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

        self.rules_list.append(
            RuleComplex(
                fct_name="curve_B(H)",
                folder="MotorCAD",
                param_dict={"material": material, "path_P": path_P},
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.add_rule_skew
    def add_rule_skew(self):
        """Create and adapt all the rules related to skew
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        self.rules_list.append(
            RuleComplex(
                fct_name="skew",
                folder="MotorCAD",
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Hole.add_rule_holeM52
    def add_rule_holeM52(self, hole_id):
        """Create and adapt all the rules related to Hole
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        hole_id : int
            A int to know the number of hole
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Number"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].Zh",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Bridge_Thickness"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Thickness"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Width"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Web_Thickness"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].W3",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Hole.add_rule_holeM57
    def add_rule_holeM57(self, hole_id):
        """Create and adapt all the rules related to Hole
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        hole_id : int
            A int to know the number of hole
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Number"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].Zh",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"BridgeThickness_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"MagnetThickness_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].H2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"PoleVAngle_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].W0",
                unit_type="deg",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"VShapeMagnetPost_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].W1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"WebThickness_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].W3",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"MagnetBarWidth_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].W4",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleComplex(
                fct_name="interior_V_web_holeM57",
                folder="MotorCAD",
                param_dict={"hole_id": hole_id},
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Hole.add_rule_holeM60
    def add_rule_holeM60(self, hole_id):
        """Create and adapt all the rules related to Hole
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        hole_id : int
            A int to know the number of hole
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Number"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].Zh",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"MagnetThickness_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"BridgeThickness_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"PoleVAngle_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].W0",
                unit_type="deg",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"MagnetBarWidth_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].W1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleEquation(
                param=[
                    {
                        "src": "other",
                        "path": ["[Dimensions]", f"VSimpleWidth_Array[{hole_id}]"],
                        "variable": "y",
                    },
                    {
                        "src": "other",
                        "path": ["[Dimensions]", f"MagnetThickness_Array[{hole_id}]"],
                        "variable": "a",
                    },
                    {
                        "src": "pyleecan",
                        "path": f"machine.rotor.hole[{hole_id}].W2",
                        "variable": "x",
                    },
                ],
                unit_type="m",
                equation="y+a = x",
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"VSimpleMagnetPost_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].W3",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Hole.add_rule_holeM61
    def add_rule_holeM61(self, hole_id):
        """Create and adapt all the rules related to Hole
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        hole_id : int
            A int to know the number of hole
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Number"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].Zh",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Magnet_Thickness"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"BridgeThickness_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].H2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"WebThickness_Array[{hole_id}]"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].W3",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Magnet_Post"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleComplex(
                fct_name="interior_U_shape_holeM61",
                folder="MotorCAD",
                param_dict={"hole_id": hole_id},
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Hole.add_rule_holeM62
    def add_rule_holeM62(self, hole_id):
        """Create and adapt all the rules related to Hole
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        hole_id : int
            A int to know the number of hole
        """
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Number"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].Zh",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Magnet_Thickness"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Magnet_Embed_Depth"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        if not self.machine.rotor.hole[hole_id].W0_is_rad:
            self.rules_list.append(
                RuleComplex(
                    fct_name="embedded_parallel_holeM62",
                    folder="MotorCAD",
                    param_dict={
                        "hole_id": hole_id,
                    },
                )
            )

        else:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=["[Dimensions]", f"Magnet_Arc_[ED]"],
                    P_obj_path=f"machine.rotor.hole[{hole_id}].W0",
                    unit_type="ED",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

    # cf Methods.Converter.ConvertMC.Rules.Hole.add_rule_holeM63
    def add_rule_holeM63(self, hole_id):
        """Create and adapt all the rules related to Hole
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        hole_id : int
            A int to know the number of hole
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Number"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].Zh",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Magnet_Thickness"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Bridge_Thickness"],
                P_obj_path=f"machine.rotor.hole[{hole_id}].H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        if self.machine.rotor.hole[hole_id].top_flat == False:
            self.rules_list.append(
                RuleComplex(
                    fct_name="embedded_breadloaf_holeM63",
                    folder="MotorCAD",
                    param_dict={
                        "hole_id": hole_id,
                    },
                )
            )

        else:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=["[Dimensions]", f"Magnet_Width"],
                    P_obj_path=f"machine.rotor.hole[{hole_id}].W0",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

    # cf Methods.Converter.ConvertMC.Rules.Lamination.add_rule_lamination
    def add_rule_lamination(self, is_stator):
        """Create and adapt all the rules related to lamination (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """

        # definie the correct position in rotor or in stator
        if is_stator:
            lam_name = "stator"
            lam_name_MC = "Stator"
        else:
            lam_name = "rotor"
            lam_name_MC = "Rotor"

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"{lam_name_MC}_Lam_Length"],
                P_obj_path=f"machine.{lam_name}.L1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Miscellaneous]", f"Stacking_Factor_[{lam_name_MC}]"],
                P_obj_path=f"machine.{lam_name}.Kf1",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Lamination.add_rule_notch_slotM19
    def add_rule_notch_slotM19(self, is_stator, nb_notch):
        """Create and adapt all the rules related to lamination (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        nb_notch : int
            number oh notch
        """
        self.rules_list.append(
            RuleSimple(
                other_key_list=[
                    "[Dimensions]",
                    "PoleNotchDepth",
                ],
                P_obj_path=f"machine.rotor.notch[0].notch_shape.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=[
                    "[Dimensions]",
                    "Pole_Number",
                ],
                P_obj_path=f"machine.rotor.notch[0].notch_shape.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleComplex(fct_name="add_notch_slotM19", folder="MotorCAD")
        )

    # cf Methods.Converter.ConvertMC.Rules.Lamination.add_rule_ventilationCirc
    def add_rule_ventilationCirc(self, is_stator, duct_id):
        """Create and adapt all the rules related to lamination (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        duct_id : int
            a int to know the number of duct
        """
        duct_id_mc = duct_id + 1
        if is_stator:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"CircularDuctL{duct_id_mc}Channels",
                    ],
                    P_obj_path=f"machine.stator.axial_vent[{duct_id}].Zh",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"iCircularDuctL{duct_id_mc}RadialDiameter",
                    ],
                    P_obj_path=f"machine.stator.axial_vent[{duct_id}].H0",
                    unit_type="m",
                    scaling_to_P=0.5,
                    file_name=__file__,
                )
            )
            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"CircularDuctL{duct_id_mc}OffsetAngle",
                    ],
                    P_obj_path=f"machine.stator.axial_vent[{duct_id}].Alpha0",
                    unit_type="deg",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"CircularDuctL{duct_id_mc}ChannelDiameter",
                    ],
                    P_obj_path=f"machine.stator.axial_vent[{duct_id}].D0",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            if not self.is_P_to_other:
                self.rules_list.append(
                    RuleEquation(
                        param=[
                            {
                                "src": "other",
                                "path": [
                                    "[Dimensions]",
                                    "Pole_Number",
                                ],
                                "variable": "a",
                            },
                            {
                                "src": "pyleecan",
                                "path": f"machine.stator.axial_vent[{duct_id}].Alpha0",
                                "variable": "b",
                            },
                            {
                                "src": "pyleecan",
                                "path": f"machine.stator.axial_vent[{duct_id}].Alpha0",
                                "variable": "x",
                            },
                        ],
                        unit_type="",
                        equation="(pi/a= x+b)",
                        file_name=__file__,
                    )
                )

        else:
            lam_name_MC = "Rotor"
            lam_name_py = "rotor"

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}CircularDuctLayer_Channels[{duct_id}]",
                    ],
                    P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].Zh",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}CircularDuctLayer_RadialDiameter[{duct_id}]",
                    ],
                    P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].H0",
                    unit_type="m",
                    scaling_to_P=0.5,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}CircularDuctLayer_OffsetAngle[{duct_id}]",
                    ],
                    P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].Alpha0",
                    unit_type="deg",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}CircularDuctLayer_ChannelDiameter[{duct_id}]",
                    ],
                    P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].D0",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            if not self.is_P_to_other:
                self.rules_list.append(
                    RuleEquation(
                        param=[
                            {
                                "src": "other",
                                "path": [
                                    "[Dimensions]",
                                    "Pole_Number",
                                ],
                                "variable": "a",
                            },
                            {
                                "src": "pyleecan",
                                "path": f"machine.{lam_name_py}.axial_vent[{duct_id}].Alpha0",
                                "variable": "b",
                            },
                            {
                                "src": "pyleecan",
                                "path": f"machine.{lam_name_py}.axial_vent[{duct_id}].Alpha0",
                                "variable": "x",
                            },
                        ],
                        unit_type="",
                        equation="(pi/a= x+b)",
                        file_name=__file__,
                    )
                )

    # cf Methods.Converter.ConvertMC.Rules.Lamination.add_rule_ventilationPolar
    def add_rule_ventilationPolar(self, is_stator, duct_id):
        """Create and adapt all the rules related to lamination (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        duct_id : int
            a int to know the number of duct
        """

        if is_stator:
            self.get_logger().info("stator_duct, not implemented")
            return
        else:
            lam_name_MC = "Rotor"
            lam_name_py = "rotor"

        self.rules_list.append(
            RuleSimple(
                other_key_list=[
                    "[Through_Vent]",
                    f"{lam_name_MC}ArcDuctLayer_InnerDiameter[{duct_id}]",
                ],
                P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].H0",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=[
                    "[Through_Vent]",
                    f"{lam_name_MC}CircularDuctLayer_OffsetAngle[{duct_id}]",
                ],
                P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].Alpha0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=[
                    "[Through_Vent]",
                    f"{lam_name_MC}ArcDuctLayer_Depth[{duct_id}]",
                ],
                P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].D0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=[
                    "[Through_Vent]",
                    f"{lam_name_MC}CircularDuctLayer_Channels[{duct_id}]",
                ],
                P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].Zh",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleComplex(
                fct_name="arc_duct_polar",
                folder="MotorCAD",
                param_dict={
                    "duct_id": duct_id,
                    "lam_name_py": lam_name_py,
                    "lam_name_MC": lam_name_MC,
                },
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Lamination.add_rule_ventilationTrap
    def add_rule_ventilationTrap(self, is_stator, duct_id):
        """Create and adapt all the rules related to duct
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        duct_id : int
            a int to know the number of duct
        """

        if is_stator:
            lam_name_MC = "Stator"

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"iCircularDuctL{duct_id}RadialDiameter",
                    ],
                    P_obj_path=f"machine.stator.axial_vent[{duct_id}].H0",
                    unit_type="m",
                    scaling_to_P=0.5,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}RectangularDuctLayer_OffsetAngle[{duct_id}]",
                    ],
                    P_obj_path=f"machine.stator.axial_vent[{duct_id}].Alpha0",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}RectangularDuctLayer_ChannelDiameter[{duct_id}]",
                    ],
                    P_obj_path=f"machine.stator.axial_vent[{duct_id}].D0",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"CircularDuctL{duct_id}Channels",
                    ],
                    P_obj_path=f"machine.stator.axial_vent[{duct_id}].Zh",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}RectangularDuctLayer_Width[{duct_id}]",
                    ],
                    P_obj_path=f"machine.stator.axial_vent[{duct_id}].W1",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}RectangularDuctLayer_Width[{duct_id}]",
                    ],
                    P_obj_path=f"machine.stator.axial_vent[{duct_id}].W2",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

        else:
            lam_name_MC = "Rotor"
            lam_name_py = "rotor"

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}RectangularDuctlayers_RadialDiameter[{duct_id}]",
                    ],
                    P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].H0",
                    unit_type="m",
                    scaling_to_P=0.5,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}RectangularDuctLayer_OffsetAngle[{duct_id}]",
                    ],
                    P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].Alpha0",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}RectangularDuctLayer_ChannelDiameter[{duct_id}]",
                    ],
                    P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].D0",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}RectangularDuctLayer_Channels[{duct_id}]",
                    ],
                    P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].Zh",
                    unit_type="",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}RectangularDuctLayer_Width[{duct_id}]",
                    ],
                    P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].W1",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=[
                        "[Through_Vent]",
                        f"{lam_name_MC}RectangularDuctLayer_Width[{duct_id}]",
                    ],
                    P_obj_path=f"machine.{lam_name_py}.axial_vent[{duct_id}].W2",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

    # cf Methods.Converter.ConvertMC.Rules.Pole.add_rule_parallel_slot_slotW29
    def add_rule_parallel_slot_slotW29(self):
        """Create and adapt all the rules related to Pole
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Rotor_Poles"],
                P_obj_path=f"machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"PoleTipRadialDepth"],
                P_obj_path=f"machine.rotor.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"SyncRotorSlot_Depth"],
                P_obj_path=f"machine.rotor.slot.H2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"SyncRotorSlot_Width"],
                P_obj_path=f"machine.rotor.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"SyncRotorSlot_Width"],
                P_obj_path=f"machine.rotor.slot.W1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"SyncRotorSlot_Width"],
                P_obj_path=f"machine.rotor.slot.W2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Pole.add_rule_parallel_tooth_slotW63
    def add_rule_parallel_tooth_slotW63(self):
        """Create and adapt all the rules related to Pole
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Rotor_Poles"],
                P_obj_path="machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Pole_Depth"],
                P_obj_path="machine.rotor.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Rotor_Pole_Angle"],
                P_obj_path="machine.rotor.slot.H1",
                unit_type="deg",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        # W2 has no equivalent in MC
        # self.rules_list.append(
        #     RuleSimple(
        #         other_key_list=["[Dimensions]", f""],
        #         P_obj_path=f"machine.rotor.slot.W2",
        #         unit_type="m",
        #         scaling_to_P=1,
        #         file_name=__file__,
        #     )
        # )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "PoleTipRadialDepth"],
                P_obj_path="machine.rotor.slot.H2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Pole_Width"],
                P_obj_path="machine.rotor.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleEquation(
                param=[
                    {
                        "src": "other",
                        "path": ["[Dimensions]", "Pole_Tip_Width"],
                        "variable": "y",
                    },
                    {
                        "src": "other",
                        "path": ["[Dimensions]", "Pole_Width"],
                        "variable": "a",
                    },
                    {
                        "src": "pyleecan",
                        "path": "machine.rotor.slot.W1",
                        "variable": "x",
                    },
                ],
                unit_type="m",
                equation="2*y + a = x",
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Pole.add_rule_salient_pole_slotW62
    def add_rule_salient_pole_slotW62(self):
        """Create and adapt all the rules related to Pole
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Rotor_Poles"],
                P_obj_path=f"machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Depth"],
                P_obj_path=f"machine.rotor.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Rotor_Coil_Width"],
                P_obj_path=f"machine.rotor.slot.W2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Rotor_Coil_Depth"],
                P_obj_path=f"machine.rotor.slot.H2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Width"],
                P_obj_path=f"machine.rotor.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Liner_Pole_Tip"],
                P_obj_path=f"machine.rotor.slot.H3",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Liner_Pole_Side"],
                P_obj_path=f"machine.rotor.slot.W3",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleEquation(
                param=[
                    {
                        "src": "other",
                        "path": ["[Dimensions]", "Slot_Depth"],
                        "variable": "y",
                    },
                    {
                        "src": "other",
                        "path": ["[Dimensions]", "Pole_Tip_Width"],
                        "variable": "a",
                    },
                    {
                        "src": "pyleecan",
                        "path": f"machine.rotor.slot.W1",
                        "variable": "x",
                    },
                ],
                unit_type="m",
                equation="2*y + a = x",
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleComplex(fct_name="salient_pole_slotW62", folder="MotorCAD")
        )

    # cf Methods.Converter.ConvertMC.Rules.Rotor_Magnet.add_rule_slotM11
    def add_rule_slotM11(self):
        """Create and adapt all the rules related to slotM11
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Number"],
                P_obj_path=f"machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Arc_[ED]"],
                P_obj_path=f"machine.rotor.slot.W0",
                unit_type="ED",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Arc_[ED]"],
                P_obj_path=f"machine.rotor.slot.W1",
                unit_type="ED",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Thickness"],
                P_obj_path=f"machine.rotor.slot.H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Thickness"],
                P_obj_path=f"machine.rotor.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Rotor_Magnet.add_rule_slotM12
    def add_rule_slotM12(self):
        """Create and adapt all the rules related to slotM12
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Number"],
                P_obj_path=f"machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Thickness"],
                P_obj_path=f"machine.rotor.slot.H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleComplex(fct_name="inset_breadloaf_slotM12", folder="MotorCAD")
        )

    # cf Methods.Converter.ConvertMC.Rules.Rotor_Magnet.add_rule_slotM13
    def add_rule_slotM13(self):
        """Create and adapt all the rules related to slotM13
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Number"],
                P_obj_path=f"machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Thickness"],
                P_obj_path=f"machine.rotor.slot.H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleComplex(fct_name="surface_breadloaf_slotM13", folder="MotorCAD")
        )

    # cf Methods.Converter.ConvertMC.Rules.Rotor_Magnet.add_rule_slotM14
    def add_rule_slotM14(self):
        """Create and adapt all the rules related to slotM14
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Number"],
                P_obj_path=f"machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Arc_[ED]"],
                P_obj_path=f"machine.rotor.slot.W0",
                unit_type="ED",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Arc_[ED]"],
                P_obj_path=f"machine.rotor.slot.W1",
                unit_type="ED",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Thickness"],
                P_obj_path=f"machine.rotor.slot.H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleComplex(fct_name="surface_radial_slotM14", folder="MotorCAD")
        )

    # cf Methods.Converter.ConvertMC.Rules.Rotor_Magnet.add_rule_slotM15
    def add_rule_slotM15(self):
        """Create and adapt all the rules related to slotM15
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Number"],
                P_obj_path=f"machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Thickness"],
                P_obj_path=f"machine.rotor.slot.H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Arc_[ED]"],
                P_obj_path=f"machine.rotor.slot.W0",
                unit_type="ED",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        if self.machine.rotor.slot.H0 != 0:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=["[Dimensions]", "Magnet_Thickness"],
                    P_obj_path=f"machine.rotor.slot.H0",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )
            self.rules_list.append(
                RuleComplex(fct_name="inset_parallel_slotM15", folder="MotorCAD")
            )

        else:
            self.rules_list.append(
                RuleComplex(fct_name="surface_parallel_slotM15", folder="MotorCAD")
            )

    # cf Methods.Converter.ConvertMC.Rules.Rotor_Magnet.add_rule_slotM16
    def add_rule_slotM16(self):
        """Create and adapt all the rules related to slotM16
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", f"Pole_Number"],
                P_obj_path=f"machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Opening"],
                P_obj_path=f"machine.rotor.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Thickness"],
                P_obj_path=f"machine.rotor.slot.W1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Inset"],
                P_obj_path=f"machine.rotor.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Magnet_Inset"],
                P_obj_path=f"machine.rotor.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Slot.add_rule_slotW11
    def add_rule_slotW11(self, is_stator):
        """Create and adapt all the rules related to slotW11 (lam radius,...)
        Extend self.rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            True slot is in stator, False slot is in rotor
        """
        # definie the correct position in rotor or in stator
        if is_stator == True:
            lam_name = "stator"
        else:
            lam_name = "rotor"

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Number"],
                P_obj_path=f"machine.{lam_name}.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Opening"],
                P_obj_path=f"machine.{lam_name}.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        if self.machine.stator.slot.is_cstt_tooth:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=["[Dimensions]", "Tooth_Width"],
                    P_obj_path=f"machine.{lam_name}.slot.W3",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

        else:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=["[Dimensions]", "Slot_Width_Top"],
                    P_obj_path=f"machine.{lam_name}.slot.W1",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=["[Dimensions]", "Slot_Width_Bottom"],
                    P_obj_path=f"machine.{lam_name}.slot.W2",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Tooth_Tip_Depth"],
                P_obj_path=f"machine.{lam_name}.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Corner_Radius"],
                P_obj_path=f"machine.{lam_name}.slot.R1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        if not self.is_P_to_other:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=["[Dimensions]", "Tooth_Tip_Angle"],
                    P_obj_path=f"machine.{lam_name}.slot.H1",
                    unit_type="deg",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleComplex(fct_name="slotW11_H1", folder="MotorCAD")
            )

            self.rules_list.append(
                RuleEquation(
                    param=[
                        {
                            "src": "other",
                            "path": ["[Dimensions]", "Slot_Depth"],
                            "variable": "y",
                        },
                        {
                            "src": "pyleecan",
                            "path": f"machine.{lam_name}.slot.H2",
                            "variable": "x",
                        },
                        {
                            "src": "pyleecan",
                            "path": f"machine.{lam_name}.slot.H1",
                            "variable": "a",
                        },
                        {
                            "src": "pyleecan",
                            "path": f"machine.{lam_name}.slot.H0",
                            "variable": "b",
                        },
                    ],
                    unit_type="m",
                    equation="y = b+a+x",
                    file_name=__file__,
                )
            )

        else:
            raise ValueError(
                "Conversion of tooth_tip_depth_H1 impossible because it is not in rad"
            )

    # cf Methods.Converter.ConvertMC.Rules.Slot.add_rule_slotW14
    def add_rule_slotW14(self, is_stator):
        """Create and adapt all the rules related to slotW14 (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """
        if is_stator == True:
            lam_name = "stator"
        else:
            lam_name = "rotor"

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Number"],
                P_obj_path=f"machine.{lam_name}.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Opening"],
                P_obj_path=f"machine.{lam_name}.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Tooth_Width"],
                P_obj_path=f"machine.{lam_name}.slot.W3",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Tooth_Tip_Depth"],
                P_obj_path=f"machine.{lam_name}.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Tooth_Tip_Angle"],
                P_obj_path=f"machine.{lam_name}.slot.H1",
                unit_type="deg",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(RuleComplex(fct_name="slotW14_H1", folder="MotorCAD"))

        self.rules_list.append(
            RuleEquation(
                param=[
                    {
                        "src": "other",
                        "path": ["[Dimensions]", "Slot_Depth"],
                        "variable": "y",
                    },
                    {
                        "src": "pyleecan",
                        "path": f"machine.{lam_name}.slot.H3",
                        "variable": "x",
                    },
                    {
                        "src": "pyleecan",
                        "path": f"machine.{lam_name}.slot.H1",
                        "variable": "a",
                    },
                    {
                        "src": "pyleecan",
                        "path": f"machine.{lam_name}.slot.H0",
                        "variable": "b",
                    },
                ],
                unit_type="m",
                equation="y = x+a+b",
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Slot.add_rule_slotW21
    def add_rule_slotW21(self, is_stator):
        """Create and adapt all the rules related to slotW21 (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """
        if is_stator == True:
            lam_name = "stator"
        else:
            lam_name = "rotor"

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Number"],
                P_obj_path=f"machine.{lam_name}.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Opening"],
                P_obj_path=f"machine.{lam_name}.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Tooth_Width"],
                P_obj_path=f"machine.{lam_name}.slot.W1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Tooth_Width"],
                P_obj_path=f"machine.{lam_name}.slot.W2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Tooth_Tip_Depth"],
                P_obj_path=f"machine.{lam_name}.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        if not self.is_P_to_other:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=["[Dimensions]", "Tooth_Tip_Angle"],
                    P_obj_path=f"machine.{lam_name}.slot.H1",
                    unit_type="deg",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleComplex(fct_name="slotW21_H1", folder="MotorCAD")
            )

            self.rules_list.append(
                RuleEquation(
                    param=[
                        {
                            "src": "other",
                            "path": ["[Dimensions]", "Slot_Depth"],
                            "variable": "y",
                        },
                        {
                            "src": "pyleecan",
                            "path": f"machine.{lam_name}.slot.H2",
                            "variable": "x",
                        },
                        {
                            "src": "pyleecan",
                            "path": f"machine.{lam_name}.slot.H1",
                            "variable": "a",
                        },
                        {
                            "src": "pyleecan",
                            "path": f"machine.{lam_name}.slot.H0",
                            "variable": "b",
                        },
                    ],
                    unit_type="m",
                    equation="y = b+a+x",
                    file_name=__file__,
                )
            )

    # cf Methods.Converter.ConvertMC.Rules.Slot.add_rule_slotW23
    def add_rule_slotW23(self, is_stator):
        """Create and adapt all the rules related to slotW23 (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """

        if is_stator == True:
            lam_name = "stator"
        else:
            lam_name = "rotor"

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Number"],
                P_obj_path=f"machine.{lam_name}.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Opening"],
                P_obj_path=f"machine.{lam_name}.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        if self.machine.stator.slot.is_cstt_tooth:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=["[Dimensions]", "Tooth_Width"],
                    P_obj_path=f"machine.{lam_name}.slot.W3",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )
        else:
            self.rules_list.append(
                RuleSimple(
                    other_key_list=["[Dimensions]", "Slot_Width_Top"],
                    P_obj_path=f"machine.{lam_name}.slot.W1",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

            self.rules_list.append(
                RuleSimple(
                    other_key_list=["[Dimensions]", "Slot_Width_Bottom"],
                    P_obj_path=f"machine.{lam_name}.slot.W2",
                    unit_type="m",
                    scaling_to_P=1,
                    file_name=__file__,
                )
            )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Tooth_Tip_Depth"],
                P_obj_path=f"machine.{lam_name}.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Depth"],
                P_obj_path=f"machine.{lam_name}.slot.H2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Tooth_Tip_Angle"],
                P_obj_path=f"machine.{lam_name}.slot.H1",
                unit_type="deg",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Slot.add_rule_slotW29
    def add_rule_slotW29(self, is_stator):
        """Create and adapt all the rules related to slotW29 (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """

        if is_stator == True:
            lam_name = "stator"
        else:
            lam_name = "rotor"

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Number"],
                P_obj_path=f"machine.{lam_name}.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Width"],
                P_obj_path=f"machine.{lam_name}.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleEquation(
                param=[
                    {
                        "src": "other",
                        "path": ["[Dimensions]", "FormWound_WedgeInset"],
                        "variable": "y",
                    },
                    {
                        "src": "other",
                        "path": ["[Dimensions]", "Slot_Width"],
                        "variable": "a",
                    },
                    {
                        "src": "pyleecan",
                        "path": f"machine.{lam_name}.slot.W1",
                        "variable": "x",
                    },
                ],
                unit_type="m",
                equation="y+a = x",
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Width"],
                P_obj_path=f"machine.{lam_name}.slot.W2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "FormWound_WedgeDepth"],
                P_obj_path=f"machine.{lam_name}.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "FormWound_WedgeThickness"],
                P_obj_path=f"machine.{lam_name}.slot.H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Slot_Depth"],
                P_obj_path=f"machine.{lam_name}.slot.H2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Slot.rotor.add_rule_rotor_slotW11_2
    def add_rule_rotor_slotW11_2(self, is_stator):
        """Create and adapt all the rules related to slotW11 (lam radius,...)
        Extend rules_list within Converter object
        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """
        if is_stator:
            raise KeyError("Those rules are for rotor slot only")

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Rotor_Bars"],
                P_obj_path=f"machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Opening_[T]"],
                P_obj_path=f"machine.rotor.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Rotor_Tooth_Width_T"],
                P_obj_path=f"machine.rotor.slot.W3",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Opening_Depth_[T]"],
                P_obj_path=f"machine.rotor.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Corner_Radius[T]"],
                P_obj_path=f"machine.rotor.slot.R1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Tip_Angle_[T]"],
                P_obj_path=f"machine.rotor.slot.H1",
                unit_type="deg",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        if not self.is_P_to_other:
            self.rules_list.append(
                RuleComplex(fct_name="rotor_slotW11_H1", folder="MotorCAD")
            )

            self.rules_list.append(
                RuleEquation(
                    param=[
                        {
                            "src": "other",
                            "path": ["[Dimensions]", "Bar_Depth_[T]"],
                            "variable": "y",
                        },
                        {
                            "src": "pyleecan",
                            "path": f"machine.rotor.slot.H2",
                            "variable": "x",
                        },
                        {
                            "src": "pyleecan",
                            "path": f"machine.rotor.slot.H1",
                            "variable": "a",
                        },
                        {
                            "src": "pyleecan",
                            "path": f"machine.rotor.slot.H0",
                            "variable": "b",
                        },
                    ],
                    unit_type="m",
                    equation="y = b+a+x",
                    file_name=__file__,
                )
            )

    # cf Methods.Converter.ConvertMC.Rules.Slot.rotor.add_rule_rotor_slotW23
    def add_rule_rotor_slotW23(self, is_stator):
        """Create and adapt all the rules related to slotW23
        Extend rules_list within Converter object
        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """
        if is_stator:
            raise KeyError("Those rules are for rotor slot only")

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Rotor_Bars"],
                P_obj_path=f"machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Opening_[T]"],
                P_obj_path=f"machine.rotor.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Width_[T]"],
                P_obj_path=f"machine.rotor.slot.W1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Opening_Depth_[T]"],
                P_obj_path=f"machine.rotor.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Tip_Angle_[T]"],
                P_obj_path=f"machine.rotor.slot.H1",
                unit_type="deg",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Depth_[T]"],
                P_obj_path=f"machine.rotor.slot.H2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Width_[T]"],
                P_obj_path=f"machine.rotor.slot.W2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Slot.rotor.add_rule_rotor_slotW26
    def add_rule_rotor_slotW26(self, is_stator):
        """Create and adapt all the rules related to slotW23 (lam radius,...)
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """
        if is_stator:
            raise KeyError("Those rules are for rotor slot only")

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Rotor_Bars"],
                P_obj_path=f"machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Opening_[T]"],
                P_obj_path=f"machine.rotor.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Opening_Depth_[T]"],
                P_obj_path=f"machine.rotor.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Width_[T]"],
                P_obj_path=f"machine.rotor.slot.R1",
                unit_type="m",
                scaling_to_P=0.5,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Slot.rotor.add_rule_rotor_slotW30
    def add_rule_rotor_slotW30(self, is_stator):
        """Create and adapt all the rules related to slotW23 (lam radius,...)
        Extend rules_list within Converter object
        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            A booleen to know, position in lamination
        """
        if is_stator:
            raise KeyError("Those rules are for rotor slot only")

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Rotor_Bars"],
                P_obj_path=f"machine.rotor.slot.Zs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Opening_[T]"],
                P_obj_path=f"machine.rotor.slot.W0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Opening_Depth_[T]"],
                P_obj_path=f"machine.rotor.slot.H0",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Rotor_Tooth_Width_T"],
                P_obj_path=f"machine.rotor.slot.W3",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "Bar_Depth_[T]"],
                P_obj_path=f"machine.rotor.slot.H1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "BarT_Opening_Radius"],
                P_obj_path=f"machine.rotor.slot.R1",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Dimensions]", "BarT_Opening_Radius"],
                P_obj_path=f"machine.rotor.slot.R2",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

    # cf Methods.Converter.ConvertMC.Rules.Winding.add_rule_condtype11
    def add_rule_condtype11(self, is_stator):
        """Create and adapt all the rules related to condtype11
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            True slot is in stator, False slot is in rotor
        """
        # definie the correct position in rotor or in stator
        if is_stator == True:
            lam_name = "stator"
        else:
            lam_name = "rotor"

        # conversion problem, possibility of having these rules
        """
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Magnetics]", "NumberStrandsHand"],
                P_obj_path=f"machine.{lam_name}.winding.conductor.Nwppc_rad",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Magnetics]", "NumberStrandsHand"],
                P_obj_path=f"machine.{lam_name}.winding.conductor.Nwppc_tan",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )"""

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Winding_Design]", "Copper_Height"],
                P_obj_path=f"machine.{lam_name}.winding.conductor.Wwire",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Winding_Design]", "Copper_Width"],
                P_obj_path=f"machine.{lam_name}.winding.conductor.Hwire",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        # not implemented
        """
        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Calc_Options]", "WireInsThicknessCalculation"],
                P_obj_path=f"machine.{lam_name}.winding.conductor.Wins_wire",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )"""

        self.rules_list.append(
            RuleComplex(fct_name="end_winding_lenght", folder="MotorCAD")
        )

    # cf Methods.Converter.ConvertMC.Rules.Winding.add_rule_condtype12
    def add_rule_condtype12(self, is_stator):
        """Create and adapt all the rules related to condtype12
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            True slot is in stator, False slot is in rotor
        """
        # definie the correct position in rotor or in stator
        if is_stator:
            lam_name = "stator"
        else:
            lam_name = "rotor"

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Magnetics]", "NumberStrandsHand"],
                P_obj_path=f"machine.{lam_name}.winding.conductor.Nwppc",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Winding_Design]", "Copper_Diameter"],
                P_obj_path=f"machine.{lam_name}.winding.conductor.Wwire",
                unit_type="m",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        # Not implemented
        """
        self.rules_list.append(
            RuleEquation(
                param=[
                    {
                        "src": "other",
                        "path": ["[Winding_Design]", "Copper_Diameter"],
                        "variable": "y",
                    },
                    {
                        "src": "other",
                        "path": ["[Winding_Design]", "Wire_Diameter"],
                        "variable": "b",
                    },
                    {
                        "src": "pyleecan",
                        "path": f"machine.{lam_name}.winding.conductor.Wins_wire",
                        "variable": "x",
                    },
                ],
                unit_type="m",
                equation="y/2 + b/2 = x",
                file_name=__file__,
            )
        )
        """
        self.rules_list.append(
            RuleComplex(fct_name="end_winding_lenght", folder="MotorCAD")
        )

    # cf Methods.Converter.ConvertMC.Rules.Winding.add_rule_rotor_bar
    def add_rule_rotor_bar(self, is_stator):
        """Create and adapt all the rules related to condtype12
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            True slot is in stator, False slot is in rotor
        """
        # definie the correct position in rotor or in stator
        if is_stator:
            raise KeyError("Those rules are for rotor slot only")

        self.rules_list.append(RuleComplex(fct_name="rotor_bar", folder="MotorCAD"))

    # cf Methods.Converter.ConvertMC.Rules.Winding.add_rule_winding
    def add_rule_winding(self, is_stator):
        """Create and adapt all the rules related to winding
        Extend rules_list within Converter object

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        is_stator : Bool
            True slot is in stator, False slot is in rotor
        """
        # definie the correct position in rotor or in stator
        if is_stator == True:
            lam_name = "stator"
        else:
            lam_name = "rotor"

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Magnetics]", "MagPhases"],
                P_obj_path=f"machine.{lam_name}.winding.qs",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Magnetics]", "MagTurnsConductor"],
                P_obj_path=f"machine.{lam_name}.winding.Ntcoil",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Magnetics]", "MagThrow"],
                P_obj_path=f"machine.{lam_name}.winding.coil_pitch",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleSimple(
                other_key_list=["[Magnetics]", "ParallelPaths"],
                P_obj_path=f"machine.{lam_name}.winding.Npcp",
                unit_type="",
                scaling_to_P=1,
                file_name=__file__,
            )
        )

        self.rules_list.append(
            RuleComplex(
                fct_name="winding_layer",
                folder="MotorCAD",
                param_dict={is_stator: lam_name},
            )
        )

    # cf Methods.Converter.ConvertMC.select_SIPMSM_machine_dimension
    def select_SIPMSM_machine_dimension(self):
        """select the correct rule for machine dimension
        if the slot is in surface conversion to machine dimension is different

        Parameters
        ----------
        self : ConvertMC
            A ConvertMC object
        """
        if self.is_P_to_other:
            magnet_name = type(self.machine.rotor.slot).__name__
            if (
                magnet_name in ["SlotM11", "SlotM13", "SlotM15"]
                and self.machine.rotor.slot.H0 == 0
            ):
                self.add_rule_machine_dimension_surface_magnet()
            else:
                # "HoleM62"
                # "HoleM63"
                # "HoleM52"
                # "HoleM60"
                # "HoleM57"
                # "HoleM61"
                self.add_rule_machine_dimension()

        else:
            magnet_name = self.other_dict["[Design_Options]"]["BPM_Rotor"]
            if magnet_name in [
                "Surface_Radial",
                "Surface_Parallel",
                "Surface_Breadloaf",
            ]:
                self.add_rule_machine_dimension_surface_magnet()
            else:
                # "Embedded_Parallel"
                # "Embedded_Radial"
                # "Embedded_Breadleaof"
                # "Interior_Flat(simple)"
                # "Interior_Flat(web)"
                # "Interior_V(simple)"
                # "Interior_V(web)"
                # "Interior_U-Shape"

                self.add_rule_machine_dimension()

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
        # Call Convert init
        super(ConvertMC, self).__init__(
            other_unit_dict=other_unit_dict,
            other_dict=other_dict,
            machine=machine,
            rules_list=rules_list,
            is_P_to_other=is_P_to_other,
        )
        # The class is frozen (in Convert init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        ConvertMC_str = ""
        # Get the properties inherited from Convert
        ConvertMC_str += super(ConvertMC, self).__str__()
        return ConvertMC_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Convert
        if not super(ConvertMC, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Convert
        diff_list.extend(
            super(ConvertMC, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Convert
        S += super(ConvertMC, self).__sizeof__()
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

        # Get the properties inherited from Convert
        ConvertMC_dict = super(ConvertMC, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        ConvertMC_dict["__class__"] = "ConvertMC"
        return ConvertMC_dict

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

        # Set to None the properties inherited from Convert
        super(ConvertMC, self)._set_None()
