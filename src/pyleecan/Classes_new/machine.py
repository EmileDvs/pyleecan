# Experimental dataclass generated from Generator/ClassesRef/Machine/Machine.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Polygon
from matplotlib.pyplot import subplots

from ..definitions import config_dict
from ..Functions.init_fig import init_fig
from ..Functions.labels import ROTOR_LAB, ROTOR_LAB_S, STATOR_LAB, STATOR_LAB_S
from ._pyleecan_class import PyleecanClass
from .convert import Convert
from .frame import Frame
from .material import Material
from .out_geo import OutGeo
from .shaft import Shaft
from .simulation import Simulation

ARC_NPOINT_D = 99
LINE_NPOINT_D = 1


@dataclass(eq=False)
class Machine(PyleecanClass):
    """Abstract class for machines

    Attributes
    ----------
    frame : Frame or None
        Machine's Frame
        Default: None
    shaft : Shaft or None
        Machine's Shaft
        Default: None
    name : str
        Name of the machine
        Default: "default_machine"
    desc : str or None
        Machine description
        Default: None
    type_machine : int
        Integer to store the machine type (for the GUI, should be replaced by a test of the object type)
        Default: 1
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Machine"
    """

    PATCH_COLOR_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR_ALPHA"]
    frame: Frame | None = None
    """Machine's Frame"""
    shaft: Shaft | None = None
    """Machine's Shaft"""
    name: str = "default_machine"
    """Name of the machine"""
    desc: str | None = None
    """Machine description"""
    type_machine: int = 1
    """Integer to store the machine type (for the GUI, should be replaced by a test of the object type)"""
    logger_name: str = "Pyleecan.Machine"
    """Name of the logger to use"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                Convert,
                Simulation,
            ),
        ):
            raise TypeError(
                "Machine parent must be an instance of Convert or Simulation, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Machine.Machine.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0):
        """Build the geometry of the machine

        Parameters
        ----------
        self : Machine
            Machine object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation

        Returns
        -------
        surf_list : list
            list of surfaces needed to draw the lamination

        """
        surf_list = []

        if self.frame is not None:
            surf_list.extend(
                self.frame.build_geometry(sym=sym, alpha=alpha, delta=delta)
            )

        if self.rotor.is_internal:
            # Adding the list of surfaces of the stator
            surf_list.extend(
                self.stator.build_geometry(sym=sym, alpha=alpha, delta=delta)
            )
            # Adding the list of surfaces of the rotor
            surf_list.extend(
                self.rotor.build_geometry(sym=sym, alpha=alpha, delta=delta)
            )
            # Add the shaft only for Internal Rotor
            if self.rotor.Rint > 0:
                surf_list.extend(
                    self.shaft.build_geometry(sym=sym, alpha=alpha, delta=delta)
                )
        else:
            # Adding the list of surfaces of the rotor
            surf_list.extend(
                self.rotor.build_geometry(sym=sym, alpha=alpha, delta=delta)
            )
            # Adding the list of surfaces of the stator
            surf_list.extend(
                self.stator.build_geometry(sym=sym, alpha=alpha, delta=delta)
            )

        return surf_list

    # Inlined from Methods.Machine.Machine.check
    def check(self):
        """Check that the Machine object is correct

        Parameters
        ----------
        self :
            A Machine object

        Returns
        -------
        None

        Raises
        _______
        MC_AbstractError
            Machine is an abstract class
        MC_StatorNotStator
            self.stator.is_stator must be True
        MC_RotorIsStator
            self.rotor.is_stator must be False
        MC_BothInternal
            self.rotor.is_internal and self.rotor.is_internal can't be both True
        MC_BothExternal
            self.rotor.is_internal and self.rotor.is_internal can't be both False
        MC_RotorDontFit
            The Rotor is too big to fit in the Stator
        MC_ShaftTooBig
            The Shaft is too big to fit in the Rotor
        MC_ShaftTooSmall
            The Shaft is too small to fit in the Rotor
        MC_MecAirgapError
            The Stator and the rotor don't fit because of magnet or short circuit ring
        """

        if type(self).__name__ == "Machine":
            raise MC_AbstractError("Machine is an abstract class")

        if not self.stator.is_stator:
            raise MC_StatorNotStator("self.stator.is_stator must be True")

        if self.rotor.is_stator:
            raise MC_RotorIsStator("self.rotor.is_stator must be False")

        if self.rotor.is_internal and self.stator.is_internal:
            raise MC_BothInternal(
                "self.rotor.is_internal and self.rotor.is_internal can't be both True"
            )

        if (not self.rotor.is_internal) and (not self.stator.is_internal):
            raise MC_BothExternal(
                "self.rotor.is_internal and self.rotor.is_internal can't be both False"
            )

        if self.rotor.is_internal:
            if self.rotor.Rext > self.stator.Rint:
                raise MC_RotorDontFit("The Rotor is too big to fit in the Stator")
            if self.shaft.Drsh / 2.0 > self.rotor.Rint:
                raise MC_ShaftTooBig("The Shaft is too big to fit in the Rotor")
            if self.shaft.Drsh / 2.0 < self.rotor.Rint:
                raise MC_ShaftTooSmall("The Shaft is too small to fit in the Rotor")
        else:
            if self.stator.Rext > self.rotor.Rint:
                raise MC_StatorDontFit("The Stator is too big to fit in the Rotor")

        if self.comp_width_airgap_mec() <= 0:
            raise MC_MecAirgapError(
                "The Stator and the rotor don't fit because "
                "of magnet or short circuit ring"
            )

        self.rotor.check()
        self.stator.check()

    # Inlined from Methods.Machine.Machine.comp_angle_rotor_initial
    def comp_angle_rotor_initial(self):
        """Set rotor initial angle as 0

        Parameters
        ----------
        self : Machine
            A: Machine object

        Returns
        -------
        angle_rotor_initial: float
            rotor initial angle set to 0 [rad]
        """

        return 0

    # Inlined from Methods.Machine.Machine.comp_desc_dict
    def comp_desc_dict(self):
        """Compute a dictionary with the main parameters/output of the machine

        Parameters
        ----------
        self : Machine
            A Machine object

        Returns
        -------
        desc_dict: list
            list of dictionary containing the main parameters of the machine
        """

        desc_dict = []

        # Machine Type
        desc_str = self.get_machine_type()
        desc_dict.append(
            dict(
                {
                    "name": "Type",
                    "path": "type(machine)",
                    "verbose": "Machine Type",
                    "type": str,
                    "unit": "",
                    "is_input": False,
                    "value": desc_str.split(" ")[0],
                }
            )
        )
        # Zs
        desc_dict.append(
            dict(
                {
                    "name": "Zs",
                    "path": "machine.stator.slot.Zs",
                    "verbose": "Stator slot number",
                    "type": int,
                    "unit": "",
                    "is_input": True,
                    "value": self.stator.slot.Zs,
                }
            )
        )
        # p
        desc_dict.append(
            dict(
                {
                    "name": "p",
                    "path": "machine.stator.winding.p",
                    "verbose": "Pole pair number",
                    "type": int,
                    "unit": "",
                    "is_input": True,
                    "value": self.stator.get_pole_pair_number(),
                }
            )
        )
        # is_inner_rotor
        if self.rotor.is_internal:
            inner = "Internal Rotor"
        else:
            inner = "External Rotor"
        desc_dict.append(
            dict(
                {
                    "name": "Topology",
                    "path": "machine.rotor.is_internal",
                    "verbose": "Topology",
                    "type": str,
                    "unit": "",
                    "is_input": False,
                    "value": inner,
                }
            )
        )
        # qs
        desc_dict.append(
            dict(
                {
                    "name": "qs",
                    "path": "machine.stator.winding.qs",
                    "verbose": "Stator phase number",
                    "type": int,
                    "unit": "",
                    "is_input": True,
                    "value": self.stator.winding.qs,
                }
            )
        )
        # Stator winding resistance
        try:
            Rwind = self.stator.comp_resistance_wind()
        except Exception:
            Rwind = None
        desc_dict.append(
            dict(
                {
                    "name": "Rwinds",
                    "path": "machine.stator.comp_resistance_wind()",
                    "verbose": "Stator winding resistance",
                    "type": float,
                    "unit": "Ohm",
                    "is_input": False,
                    "value": Rwind,
                }
            )
        )

        # Machine masses
        try:
            M_dict = self.comp_masses()
            Mmach = M_dict["All"]
        except Exception:
            M_dict = None
            Mmach = None
        desc_dict.append(
            dict(
                {
                    "name": "Mmachine",
                    "path": "machine.comp_masses()['All']",
                    "verbose": "Machine total mass",
                    "type": float,
                    "unit": "kg",
                    "is_input": False,
                    "value": Mmach,
                }
            )
        )

        # Stator lamination mass
        if M_dict is not None and "Stator-0" in M_dict and "Mlam" in M_dict["Stator-0"]:
            Mslam = M_dict["Stator-0"]["Mlam"]
        else:
            Mslam = None
        desc_dict.append(
            dict(
                {
                    "name": "Mslam",
                    "path": "machine.comp_masses()['Stator-0']['Mlam']",
                    "verbose": "Stator lamination mass",
                    "type": float,
                    "unit": "kg",
                    "is_input": False,
                    "value": Mslam,
                }
            )
        )

        # Stator winding mass
        if (
            M_dict is not None
            and "Stator-0" in M_dict
            and "Mwind" in M_dict["Stator-0"]
        ):
            Mswind = M_dict["Stator-0"]["Mwind"]
        else:
            Mswind = None
        desc_dict.append(
            dict(
                {
                    "name": "Mswind",
                    "path": "machine.comp_masses()['Stator-0']['Mwind']",
                    "verbose": "Stator winding mass",
                    "type": float,
                    "unit": "kg",
                    "is_input": False,
                    "value": Mswind,
                }
            )
        )

        # Rotor lamination mass
        if M_dict is not None and "Rotor-0" in M_dict and "Mlam" in M_dict["Rotor-0"]:
            Mrlam = M_dict["Rotor-0"]["Mlam"]
        else:
            Mrlam = None
        desc_dict.append(
            dict(
                {
                    "name": "Mrlam",
                    "path": "machine.comp_masses()['Rotor-0']['Mlam']",
                    "verbose": "Rotor lamination mass",
                    "type": float,
                    "unit": "kg",
                    "is_input": False,
                    "value": Mrlam,
                }
            )
        )

        # Rotor winding mass only if necessary
        if M_dict is not None and "Rotor-0" in M_dict and "Mwind" in M_dict["Rotor-0"]:
            Mrwind = M_dict["Rotor-0"]["Mwind"]
            desc_dict.append(
                dict(
                    {
                        "name": "Mrwind",
                        "path": "machine.comp_masses()['Rotor-0']['Mwind']",
                        "verbose": "Rotor winding mass",
                        "type": float,
                        "unit": "kg",
                        "is_input": False,
                        "value": Mrwind,
                    }
                )
            )

        # Magnet mass only if necessary
        if M_dict is not None and "Rotor-0" in M_dict and "Mmag" in M_dict["Rotor-0"]:
            Mmag = M_dict["Rotor-0"]["Mmag"]
            desc_dict.append(
                dict(
                    {
                        "name": "Mmag",
                        "path": "machine.comp_masses()['Rotor-0']['Mmag']",
                        "verbose": "Rotor magnet mass",
                        "type": float,
                        "unit": "kg",
                        "is_input": False,
                        "value": Mmag,
                    }
                )
            )

        # Shaft mass only if necessary
        if M_dict is not None and "Shaft" in M_dict:
            Mshaft = M_dict["Shaft"]
            desc_dict.append(
                dict(
                    {
                        "name": "Mshaft",
                        "path": "machine.comp_masses()['Shaft']",
                        "verbose": "Shaft mass",
                        "type": float,
                        "unit": "kg",
                        "is_input": False,
                        "value": Mshaft,
                    }
                )
            )

        return desc_dict

    # Inlined from Methods.Machine.Machine.comp_length_airgap_active
    def comp_length_airgap_active(self):
        """Compute the airgap active length

        Parameters
        ----------
        self : Machine
            A Machine object

        Returns
        -------
        Lgap: float
            Airgap active length [m]

        """

        return min(self.rotor.L1, self.stator.L1)

    # Inlined from Methods.Machine.Machine.comp_masses
    def comp_masses(self):
        """Compute the masses of the machine
        - Mmach : Mass total [kg]
        - Mfra : Mass of the Frame [kg]
        - Msha : Mass of the Shaft [kg]
        - Mrot : Mass dictionary of the rotor masses
        - Msta : Mass dictionary of the stator masses

        Parameters
        ----------
        self : Machine
            A Machine object

        Returns
        -------
        M_dict: dict
            A dictionary of the Machine's masses (Mmach, Msha,
            Mfra, Mrot, Msta) [kg]

        """

        M_dict = {}
        if self.frame is None:
            M_dict["Frame"] = 0
        else:
            M_dict["Frame"] = self.frame.comp_mass()

        if self.shaft is None:
            M_dict["Shaft"] = 0
        else:
            M_dict["Shaft"] = self.shaft.comp_mass()

        Mlam = 0
        for lam in self.get_lam_list():
            M = lam.comp_masses()
            M_dict[lam.get_label()] = M
            Mlam += M["Mtot"]

        Mtot = M_dict["Frame"] + M_dict["Shaft"] + Mlam
        M_dict["All"] = Mtot
        return M_dict

    # Inlined from Methods.Machine.Machine.comp_output_geo
    def comp_output_geo(self):
        """Compute the main geometry output

        Parameters
        ----------
        self : Machine
            A Machine object

        Returns
        -------
        output: OutGeo
            Main geometry output of the machine

        """

        output = OutGeo()
        output.Wgap_mec = self.comp_width_airgap_mec()
        output.Wgap_mag = self.comp_width_airgap_mag()
        output.Rgap_mec = self.comp_Rgap_mec()
        output.Lgap = self.comp_length_airgap_active()

        output.stator = self.stator.comp_output_geo()
        output.rotor = self.rotor.comp_output_geo()

        return output

    # Inlined from Methods.Machine.Machine.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the (anti)-periodicities of the machine in space domain

        Parameters
        ----------
        self : Machine
            A Machine object

        Returns
        -------
        pera : int
            Number of spatial periodicities of the machine over 2*pi
        is_apera : bool
            True if an anti-periodicity is possible after the periodicities
        """

        p = self.get_pole_pair_number()

        # Get stator (anti)-periodicity in spatial domain
        pera_s, is_antipera_s = self.stator.comp_periodicity_spatial()

        # Get rotor (anti)-periodicities in spatial domain
        pera_r, is_antipera_r = self.rotor.comp_periodicity_spatial()

        # Get machine spatial periodicity
        pera = int(np.gcd(np.gcd(pera_s, pera_r), p))

        # Get machine time and spatial anti-periodicities
        is_apera = bool(is_antipera_s and is_antipera_r)

        return pera, is_apera

    # Inlined from Methods.Machine.Machine.comp_periodicity_time
    def comp_periodicity_time(self, slip=0):
        """Compute the (anti)-periodicities of the machine in time domain

        Parameters
        ----------
        self : Machine
            A Machine object
        slip: float
            Rotor asynchronous slip

        Returns
        -------
        pert_S : int
            Number of periodicities of the machine over time period (p/felec by default if Nrev is None) in static referential
        is_apert_S : bool
            True if an anti-periodicity is possible after the periodicities (in static referential)
        pert_R : int
            Number of periodicities of the machine over time period (p/felec by default if Nrev is None) in rotating referential
        is_apert_R : bool
            True if an anti-periodicity is possible after the periodicities (in rotating referential)
        """

        if slip == 0:
            # Rotor and fundamental field rotate synchronously

            # In static referential (stator), rotor (anti)-periodicity in spatial domain
            # becomes (anti)-periodicity in time domain
            pert_S, is_apert_S = self.rotor.comp_periodicity_spatial()

            # In rotating referential (rotor), fundamental field is static so there is no anti-periodicity
            # and periodicity is given by stator spatial periodicity
            pert_R, _ = self.stator.comp_periodicity_spatial()
            is_apert_R = False

        else:
            # In case of non-zero slip, rotor and fundamental field rotates asynchronously
            # so there is no (anti)-periodicity in time domain
            pert_S, is_apert_S, pert_R, is_apert_R = 1, False, 1, False

        return pert_S, is_apert_S, pert_R, is_apert_R

    # Inlined from Methods.Machine.Machine.comp_Rgap_mec
    def comp_Rgap_mec(self):
        """Returns the radius of the center of the mecanical airgap

        Parameters
        ----------
        self : Machine
            Machine object

        Returns
        -------
        Rgap_mec: float
            Radius of the center of the mecanical airgap [m]

        """
        stator = self.stator
        rotor = self.rotor
        return (stator.comp_radius_mec() + rotor.comp_radius_mec()) / 2

    # Inlined from Methods.Machine.Machine.comp_width_airgap_mag
    def comp_width_airgap_mag(self):
        """Compute the magnetic airgap (distance beetween the two Lamination)

        Parameters
        ----------
        self: Machine
            A Machine object
        Returns
        -------
        mag_gap: float
            The magnetic airgap [m]

        """

        if self.rotor.is_internal:
            return self.stator.Rint - self.rotor.Rext
        else:
            return self.rotor.Rint - self.stator.Rext

    # Inlined from Methods.Machine.Machine.comp_width_airgap_mec
    def comp_width_airgap_mec(self):
        """Compute the mechanical airgap (mag_airgap - magnet or ring)

        Parameters
        ----------
        self: Machine
            Machine object
        Returns
        -------
        mec_gap: float
            The mechanical airgap [m]

        """

        if self.rotor.is_internal:
            return self.stator.comp_radius_mec() - self.rotor.comp_radius_mec()
        else:
            return self.rotor.comp_radius_mec() - self.stator.comp_radius_mec()

    # Inlined from Methods.Machine.Machine.get_lam_by_label
    def get_lam_by_label(self, label):
        """Returns the lamination by its labels. Accepted labels are 'Stator-X' and
        'Rotor-X' with X the number of the lamination starting with 0.
        For convenience also 'Stator' or 'Rotor' are allowed here to get respective first
        stator or rotor lamination.

        Parameters
        ----------
        self : Machine
            Machine object
        label : string
            label of the lamination to return

        Returns
        -------
        lam : Lamination
            Lamination with the given label
        """
        # prepare error message just in case
        err_msg = (
            f"'{label}' is not a valid input argument for label."
            + " Only 'Stator-X' or 'Rotor-X', with X the index, are accepted."
        )

        # Short=>Label conversion
        if STATOR_LAB not in label and ROTOR_LAB not in label:
            label = label.replace(ROTOR_LAB_S, ROTOR_LAB)
            label = label.replace(STATOR_LAB_S, STATOR_LAB)

        # split the label components
        lam_str = label.split("-")

        # if no index is provided append index 0
        if len(lam_str) == 1:
            label += "-0"

        # check that 'Rotor' or 'Stator' is in label
        if lam_str[0] not in [STATOR_LAB, ROTOR_LAB]:
            raise LabelInputError(err_msg)

        # get the requested lamination index
        try:
            index = self.get_lam_list_label().index(label)
        except:
            raise LabelInputError(err_msg)

        # return requested lamination
        return self.get_lam_list(is_int_to_ext=True, key=None)[index]

    # Inlined from Methods.Machine.Machine.get_lam_index
    def get_lam_index(self, label):
        """Returns list index of the lamination with the given label
        corresponding to machine.get_lam_list(is_int_to_ext=True, key=None).
        For convenience label 'Stator' or 'Rotor' are allowed here to get respective first
        stator or rotor lamination.

        Parameters
        ----------
        self : Machine
            Machine object

        label : str
            Label of the lamination

        Returns
        -------
        index : int
            List index of the lamination, if label doesn't exists index is None
        """
        # get list of lamination labels
        labels = self.get_lam_list_label()

        # if no index is provided with label append index 0
        if len(label.split("-")) == 1:
            label += "-0"

        # check if label exists
        if label in labels:
            return labels.index(label)
        else:
            return None

    # Inlined from Methods.Machine.Machine.get_lam_list
    def get_lam_list(self, is_int_to_ext=True, key=None):
        """Returns the ordered list of lamination of the machine

        Parameters
        ----------
        self : Machine
            Machine object
        is_int_to_ext : bool
            true to order the list from the inner lamination to the extrenal one
        key : string
            keyword to return only stator or rotor laminations, accepted values are "Stator" or "Rotor" default None to return all

        Returns
        -------
        lam_list : list
            Ordered lamination list, for abstract Machine objects list will be empty
        """
        # Extract all laminations
        lam_list = []
        if hasattr(self, "lam_list"):
            lam_list = self.lam_list
        else:
            if hasattr(self, "stator"):
                lam_list.append(self.stator)
            if hasattr(self, "rotor"):
                lam_list.append(self.rotor)

        # Sort all laminations according to Rint by assuming the lamination are not colliding
        if is_int_to_ext is not None:
            lam_list = sorted(lam_list, key=lambda x: x.Rint, reverse=not is_int_to_ext)

        # Filter the lamination according to key
        if key is not None:
            if key == STATOR_LAB:
                is_stator = True
            elif key == ROTOR_LAB:
                is_stator = False
            else:
                raise KeyInputError(
                    f"'{key}' is not a valid input argument for key (only 'Stator' or 'Rotor' accepted for now)"
                )

            lam_list = [lam for lam in lam_list if lam.is_stator is is_stator]

        return lam_list

    # Inlined from Methods.Machine.Machine.get_lam_list_label
    def get_lam_list_label(self):
        """Returns the ordered (from internal to external) list of lamination labels
        corresponding to machine.get_lam_list(is_int_to_ext=True, key=None)

        Parameters
        ----------
        self : Machine
            Machine object

        Returns
        -------
        label_list : list
            Ordered lamination list, for abstract Machine objects list will be empty
        """

        lam_list = self.get_lam_list(is_int_to_ext=True, key=None)

        label_list = []
        IDs = 0
        IDr = 0
        for lam in lam_list:
            if lam.is_stator:
                label_list.append(STATOR_LAB + "-" + str(IDs))
                IDs += 1
            else:
                label_list.append(ROTOR_LAB + "-" + str(IDr))
                IDr += 1

        return label_list

    # Inlined from Methods.Machine.Machine.get_material_dict
    def get_material_dict(self, path="self", is_unique=False):
        """
        Get the dict of materials contained in a Machine

        Parameters
        ----------
        self : Machine
            A Machine object
        path : str
            prefix to use for material object path
        is_unique : bool
            True each material will only one in the dict

        Returns
        -------
        materials : dict
            dict of materials contained in the object (key="obj path" like self.mat_type)
        """

        mach_mat_dict = self.get_material(self, path=path)
        if is_unique:
            result = {}
            name_list = []
            for key, mat in mach_mat_dict.items():
                if mat.name is not None and mat.name not in name_list:
                    result[key] = mat
                    name_list.append(mat.name)
            return result
        else:
            return mach_mat_dict

    @staticmethod
    def get_material(obj, path="self"):
        """
        Get the dict of materials contained in a pyleecan object

        Parameters
        ----------
        obj : Pyleecan object

        Returns
        -------
        materials : dict
            dict of materials contained in the object (key=obj path like self.mat_type)
        """
        materials = {}
        path += "."
        for key, value in obj.as_dict().items():
            # Get an object attribute
            sub_obj = getattr(obj, key)

            # Add it if it's a Material
            if isinstance(sub_obj, Material):
                materials[path + key] = sub_obj

            # Check the sub object if it's a Pyleecan object
            elif isinstance(value, dict) and "__class__" in value:
                materials.update(Machine.get_material(sub_obj, path=path + key))
            elif isinstance(value, list):
                for ii, v in enumerate(value):
                    if isinstance(v, dict) and "__class__" in v:
                        materials.update(
                            Machine.get_material(
                                sub_obj[ii], path=path + key + "[" + str(ii) + "]"
                            )
                        )

        return materials

    # Inlined from Methods.Machine.Machine.get_polar_eq
    def get_polar_eq(self):
        """Returns a polar equivalent of the machine

        Parameters
        ----------
        self : Machine
            Machine object

        Returns
        -------
        polar_eq: Machine
            The polar equivalent of the machine
        """

        # Copy the machine
        polar_eq = type(self)(init_dict=self.as_dict())

        polar_eq.rotor = polar_eq.rotor.get_polar_eq()
        polar_eq.stator = polar_eq.stator.get_polar_eq()
        # TODO: polar frame
        return polar_eq

    # Inlined from Methods.Machine.Machine.get_pole_pair_number
    def get_pole_pair_number(self):
        """Returns the number of pole pairs of the machine

        Parameters
        ----------
        self : Machine
            Machine object

        Returns
        -------
        p: int
            Pole pair number of the machine
        """

        # Get list of laminations
        lam_list = self.get_lam_list()
        is_add_id = len(lam_list) > 2

        lam_0 = lam_list.pop()
        p = lam_0.get_pole_pair_number()
        lab_0 = lam_0.get_label(is_add_id=is_add_id)

        # Get pole pair number for all laminations
        for i, lam in enumerate(lam_list):
            # Check that the pole pair number of lam is the same as the previous one
            if lam.get_pole_pair_number() != p:
                raise Exception(
                    "ERROR, "
                    + lam.get_label(is_add_id=is_add_id)
                    + " has a different pole pair number than "
                    + lab_0
                )

        return p

    # Inlined from Methods.Machine.Machine.plot
    def plot(
        self,
        fig=None,
        ax=None,
        sym=1,
        alpha=0,
        delta=0,
        is_edge_only=False,
        edgecolor=None,
        is_add_arrow=False,
        comp_machine=None,
        comp_legend=None,
        is_show_fig=True,
        save_path=None,
        win_title=None,
        fig_title=None,
        is_max_sym=False,
        is_clean_plot=False,
        is_winding_connection=False,
        *,
        COMP_EDGE_COLOR="r--",
    ):
        """Plot the Machine in a matplotlib fig

        Parameters
        ----------
        self : Machine
            A Machine object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_edge_only: bool
            To plot transparent Patches
        edgecolor:
            Color of the edges if is_edge_only=True
        comp_machine : Machine
            A machine to plot in transparency on top of the self machine
        comp_legend : str
            Name of the compare machine to set in the legeng (comp_machine != None)
        is_show_fig : bool
            To call show at the end of the method
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        win_title : str
            Name of the Window (default machine name)
        fig_title : str
            Name of the figure (default machine name)
        is_max_sym : bool
            True: overwrite sym parameter with max periodicity of the machine
        is_clean_plot : bool
            True to remove title, legend, axis (only machine on plot with white background)
        is_winding_connection : bool
            True to display winding connections

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        # Get maximum symetry for plot
        if is_max_sym:
            pera, is_apera = self.comp_periodicity_spatial()
            sym = 2 * pera if is_apera else pera

        if edgecolor is None:
            edgecolor = "k"  # Default is black
        (fig, ax, _, _) = init_fig(fig=fig, ax=ax, shape="square")

        # Call each plot method to properly set the legend
        if self.frame is not None:
            self.frame.plot(
                fig=fig,
                ax=ax,
                sym=sym,
                alpha=alpha,
                delta=delta,
                is_edge_only=is_edge_only,
                edgecolor=edgecolor,
                is_show_fig=False,
            )
            Wfra = self.frame.comp_height_eq()
        else:
            Wfra = 0

        # Determin order of plotting parts
        lam_list = self.get_lam_list(is_int_to_ext=True)

        Rext = lam_list[-1].Rext
        for lam in lam_list[::-1]:
            lam.plot(
                fig=fig,
                ax=ax,
                sym=sym,
                alpha=alpha,
                delta=delta,
                is_edge_only=is_edge_only,
                edgecolor=edgecolor,
                is_add_arrow=is_add_arrow,
                is_show_fig=False,
                is_winding_connection=is_winding_connection,
            )

        if (
            lam_list[0].Rint > 0
            and self.shaft is not None
            and self.shaft.Drsh is not None
        ):
            self.shaft.plot(
                fig=fig,
                ax=ax,
                sym=sym,
                alpha=alpha,
                delta=delta,
                is_edge_only=is_edge_only,
                edgecolor=edgecolor,
                is_show_fig=False,
            )

        if comp_machine is not None:
            comp_machine.rotor.plot(
                fig,
                ax,
                sym=sym,
                alpha=alpha,
                delta=delta,
                is_edge_only=True,
                edgecolor=COMP_EDGE_COLOR,
                is_add_arrow=is_add_arrow,
                is_show_fig=is_show_fig,
            )
            comp_machine.stator.plot(
                fig,
                ax,
                sym=sym,
                alpha=alpha,
                delta=delta,
                is_edge_only=True,
                edgecolor=COMP_EDGE_COLOR,
                is_add_arrow=is_add_arrow,
                is_show_fig=is_show_fig,
            )
            patch_leg = [
                Patch(facecolor=self.PATCH_COLOR_ALPHA, edgecolor="k"),
                Patch(facecolor=self.PATCH_COLOR_ALPHA, edgecolor="r", linestyle="--"),
            ]
            if comp_legend is None:
                comp_legend = "Compared machine"
            label_leg = ["Reference", comp_legend]
            ax.set_axis_off()
            ax.legend(patch_leg, label_leg)

        ax.set_xlabel("Position along x-axis [m]")
        ax.set_ylabel("Position along y-axis [m]")
        if fig_title is None:
            fig_title = self.name
        ax.set_title(fig_title)

        # Axis Setup
        ax.axis("equal")

        # The Lamination is centered in the figure
        Lim = (Rext + Wfra) * 1.5  # Axes limit for plot
        if sym > 2:
            ax.set_xlim(-Lim * 0.1, Lim)
            ax.set_ylim(-Lim * 0.1, Lim)
        elif sym == 2:
            ax.set_xlim(-Lim, Lim)
            ax.set_ylim(-Lim * 0.1, Lim)
        else:
            ax.set_xlim(-Lim, Lim)
            ax.set_ylim(-Lim, Lim)

        # Set Windows title
        if self.name not in ["", None] and win_title is None:
            win_title = self.name + " plot machine"

        # Clean figure
        if is_clean_plot:
            ax.set_axis_off()
            ax.axis("equal")
            if ax.get_legend() is not None:
                ax.get_legend().remove()
            ax.set_title("")

        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)

        if is_show_fig:
            fig.show()

        if win_title:
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(win_title)
        return fig, ax

    # Inlined from Methods.Machine.Machine.plot_anim_rotor
    def plot_anim_rotor(self, Nframe, Tanim, Nrot=1, is_loop=True):
        """Plot the machine with an animation of the rotor
        (Internal Rotor for now ?)

        Parameters
        ----------
        self : Machine
            Machine object
        Nframe: int
            Number of frame for the animation
        Tanim : float
            Duration of the animation [ms]
        Nrot : float
            Number of rotation
        is_loop : bool
            True to activate the loop animation
        """

        # Display
        fig, axes = subplots()
        axes.set_xlabel("(m)")
        axes.set_ylabel("(m)")
        axes.set_title("Machine")

        # Axis Setup
        axes.axis("equal")

        # The Lamination is centered in the figure
        Lim = (self.stator.Rext) * 1.5  # Axes limit for plot
        Rsurf = self.rotor.build_geometry(sym=1, alpha=0, delta=0)

        # Rotation angle between each frame
        Dalpha = 2 * np.pi * Nrot / Nframe

        def init():
            """Create the patches for the first image"""
            Spatches = self.stator.plot(is_display=False)
            Rpatches = self.rotor.plot(is_display=False)
            for patch in Spatches:
                axes.add_patch(patch)
            for patch in Rpatches:
                axes.add_patch(patch)
            return []

        def update_rotor(ii):
            """Rotate and update the rotor patches"""
            for ii in range(len(Rsurf)):
                Rsurf[ii].rotate(Dalpha)
                patches = Rsurf[ii].get_patches()
                for patch in patches:
                    if type(patch) is Polygon:
                        axes.patches[-len(Rsurf) + ii].xy = patch.xy
                # elif type(patch) is Circle:
                #     pass

            axes.set_xlim(-Lim, Lim)
            axes.set_ylim(-Lim, Lim)
            return []

        # Animation definition
        anim = animation.FuncAnimation(
            fig,
            update_rotor,
            init_func=init,
            frames=Nframe,
            interval=Tanim / Nframe,
            blit=True,
            repeat=is_loop,
        )
        plt.show()

    # Inlined from Methods.Machine.Machine.set_pole_pair_number
    def set_pole_pair_number(self, p):
        """Set the number of pole pairs of the machine

        Parameters
        ----------
        self : Machine
            Machine object
        p: int
            Pole pair number of the machine
        """

        # Set pole pair number for all laminations
        for lam in self.get_lam_list(is_int_to_ext=None):
            try:
                lam.set_pole_pair_number(p)
            except Exception as e:
                raise Exception(
                    "Cannot enforce pole pair number to lamination "
                    + lam.get_label()
                    + ":\n"
                    + str(e)
                )

    class MachineCheckError(Exception):
        """ """

    class MC_AbstractError(MachineCheckError):
        """ """

    class MC_BothExternal(MachineCheckError):
        """ """

    class MC_BothInternal(MachineCheckError):
        """ """

    class MC_MecAirgapError(MachineCheckError):
        """ """

    class MC_RotorDontFit(MachineCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        stator


        """

    class MC_RotorIsStator(MachineCheckError):
        """ """

    class MC_ShaftTooBig(MachineCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        rotor


        """

    class MC_ShaftTooSmall(MachineCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        rotor


        """

    class MC_StatorDontFit(MachineCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        rotor


        """

    class MC_StatorNotStator(MachineCheckError):
        """ """

    class LabelInputError(Exception):
        """ """

    class KeyInputError(Exception):
        """ """


MachineCheckError = Machine.MachineCheckError
MC_AbstractError = Machine.MC_AbstractError
MC_BothExternal = Machine.MC_BothExternal
MC_BothInternal = Machine.MC_BothInternal
MC_MecAirgapError = Machine.MC_MecAirgapError
MC_RotorDontFit = Machine.MC_RotorDontFit
MC_RotorIsStator = Machine.MC_RotorIsStator
MC_ShaftTooBig = Machine.MC_ShaftTooBig
MC_ShaftTooSmall = Machine.MC_ShaftTooSmall
MC_StatorDontFit = Machine.MC_StatorDontFit
MC_StatorNotStator = Machine.MC_StatorNotStator
LabelInputError = Machine.LabelInputError
KeyInputError = Machine.KeyInputError
