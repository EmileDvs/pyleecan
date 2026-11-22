"""Interface of pyleecan with FEMM (femm_pyleecan), written by the functions
generator from the modules of Functions/FEMM (PLAN.md Step 8).
"""

from typing import TYPE_CHECKING

import numpy as np

from ...classes_common.errors import FEMMError, NotImplementedYetError
from ...classes_common.logger_context import get_logger
from ...Classes_pydantic.geometry.arc_1 import Arc1
from ...Classes_pydantic.geometry.circle import Circle
from ...Classes_pydantic.geometry.segment import Segment
from ...Classes_pydantic.geometry.surf_line import SurfLine
from ...Classes_pydantic.import_data.import_matrix import ImportMatrix
from ...Classes_pydantic.machine.lam_h import LamH
from ...Classes_pydantic.machine.lam_hole import LamHole
from ...Classes_pydantic.machine.lam_hole_ns import LamHoleNS
from ...Classes_pydantic.machine.lam_slot_m import LamSlotM
from ...Classes_pydantic.machine.lamination import Lamination
from ...Classes_pydantic.machine.machine_sipmsm import MachineSIPMSM
from ..utils.labels import (
    AIRGAP_LAB,
    AS_BL_LAB,
    AS_BR_LAB,
    BAR_LAB,
    BORE_LAB,
    BOUNDARY_PROP_LAB,
    HOLEM_LAB,
    HOLEV_LAB,
    KEY_LAB,
    LAM_LAB,
    MAG_LAB,
    NO_LAM_LAB,
    NO_MESH_LAB,
    NOTCH_LAB,
    ROTOR_LAB,
    SBR_B_LAB,
    SBR_T_LAB,
    SBS_BL_LAB,
    SBS_BR_LAB,
    SBS_TL_LAB,
    SBS_TR_LAB,
    SLID_LAB,
    SOP_LAB,
    STATOR_LAB,
    VENT_LAB,
    WEDGE_LAB,
    WIND_LAB,
    YOKE_LAB,
    YS_LAB,
    YSL_LAB,
    YSM_LAB,
    YSML_LAB,
    YSMR_LAB,
    YSN_LAB,
    YSNL_LAB,
    YSNR_LAB,
    YSR_LAB,
    decode_label,
    get_obj_from_label,
)
from . import (
    FEMM_GROUPS,
    LAM_MAT_NAME,
    acsolver,
    is_eddies,
    minangle,
    pbtype,
    precision,
)

if TYPE_CHECKING:
    from ...classes_common.femm_handler import _FEMMHandler
    from ...Classes_pydantic.geometry.line import Line
    from ...Classes_pydantic.geometry.surface import Surface
    from ...Classes_pydantic.machine.lam_slot import LamSlot
    from ...Classes_pydantic.machine.lam_slot_wind import LamSlotWind
    from ...Classes_pydantic.machine.machine import Machine
    from ...Classes_pydantic.machine.magnet import Magnet
    from ...Classes_pydantic.output.output import Output
    from ...Classes_pydantic.simulation.dxf_import import DXFImport


class femm_pyleecan:
    """Interface of pyleecan with FEMM: the FEMM handler and the FEMM functions

    One object per FEMM instance (per parallel worker of MagFEMM, see
    OutMagFEMM.handler_list). The FEMM commands are sent with self.handler.
    """

    def __init__(self, handler: _FEMMHandler | None = None) -> None:
        """Create the object, with a new handler if none is given."""
        if handler is None:
            from ...classes_common.femm_handler import _FEMMHandler

            handler = _FEMMHandler()
        self.handler = handler

    def as_dict(self, **kwargs) -> dict:
        """Dictionary of the handler (the FEMM instance is not saved)."""
        return self.handler.as_dict(**kwargs)

    def copy(self) -> "femm_pyleecan":
        """New object with a new handler (the FEMM instance is not copied)."""
        return femm_pyleecan(handler=self.handler.copy())

    def compare(
        self, other, ignore_list=None, name="self", is_add_value: bool = False
    ) -> list:
        """No difference between two FEMM interface objects (as the handler)."""
        return []

    def assign_FEMM_surface(
        self, surf: Surface, prop: str, FEMM_dict: dict, machine: Machine
    ) -> None:
        """Assign the property given in parameter to surface having the label given
        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        surf : Surface
            the surface to assign
        prop : str
            The property to assign in FEMM
        FEMM_dict : dict
            dictionary containing the main parameters of FEMM
        machine : Machine
            Machine to draw

        Returns
        -------
        None

        """

        label = surf.label
        label_dict = decode_label(label)
        mesh_dict = self.get_mesh_param(label_dict, FEMM_dict)

        group = mesh_dict["group"]

        Clabel = 0  # By default no circuit
        Ntcoil = 0  # By default no circuit
        mag = 0  # By default no magnetization

        # point_ref is None => don't assign the surface
        if surf.point_ref is not None:
            # Select the surface
            point_ref = surf.point_ref
            self.handler.mi_addblocklabel(point_ref.real, point_ref.imag)
            self.handler.mi_selectlabel(point_ref.real, point_ref.imag)

            # Get circuit or magnetization properties if needed
            if (
                WIND_LAB in label_dict["surf_type"]
                or BAR_LAB in label_dict["surf_type"]
            ):
                # If the surface is a winding or a bar => Set circuit
                lam_obj = get_obj_from_label(machine, label_dict=label_dict)
                wind_mat = lam_obj.winding.get_connection_mat(lam_obj.get_Zs())
                Nrad_id = label_dict["R_id"]  # zone radial coordinate
                Ntan_id = label_dict["T_id"]  # zone tangential coordinate
                Zs_id = label_dict["S_id"]  # Zone slot number coordinate
                # Get the phase value in the correct slot zone
                q_id = lam_obj.winding.get_phase_id(
                    Nrad_id, Ntan_id, Zs_id, wind_mat=wind_mat
                )
                if ROTOR_LAB in label_dict["lam_type"]:  # Winding on the rotor
                    Clabel = "Circr" + str(q_id)
                else:  # winding on the stator
                    Clabel = "Circs" + str(q_id)
                Ntcoil = wind_mat[Nrad_id, Ntan_id, Zs_id, q_id]
            elif HOLEM_LAB in label_dict["surf_type"]:  # LamHole
                mag_obj = get_obj_from_label(machine, label_dict=label_dict)
                # Parallel (default) or Tangential
                if mag_obj.type_magnetization in [1, 3, None]:
                    # calculate pole angle and angle of pole middle
                    T_id = label_dict["T_id"]
                    hole = mag_obj.parent
                    Zh = hole.Zh
                    lam = hole.parent
                    alpha_p = 360 / Zh
                    mag_0 = (
                        np.floor_divide(np.angle(point_ref, deg=True), alpha_p) + 0.5
                    ) * alpha_p

                    mag_dict = hole.comp_magnetization_dict()
                    mag = mag_0 + mag_dict["magnet_" + str(T_id)] * 180 / np.pi

                    # modifiy magnetisation of south poles
                    if isinstance(lam, LamHole):
                        if (label_dict["S_id"] % 2) == 1:
                            mag = mag + 180
                    elif isinstance(lam, LamHoleNS):
                        if hole in lam.hole_south:
                            mag = mag + 180
                    # Modify magnetisation for Tangential
                    if mag_obj.type_magnetization == 3:
                        mag = mag - 90

                    # Assign magnet group
                    nb_mag = machine.rotor.get_magnet_number(sym=machine.rotor.get_Zs())
                    # Compute the number of magnet present on the inferior set
                    nb_mag_layer_inf = 0
                    for nb_set in range(label_dict["R_id"]):
                        nb_mag_layer_inf += len(
                            machine.rotor.get_hole_list()[nb_set].get_magnet_dict()
                        )

                    grp_id = (
                        label_dict["S_id"] * nb_mag
                        + label_dict["T_id"]
                        + nb_mag_layer_inf
                    )
                    group = group[grp_id]

                else:
                    raise NotImplementedYetError(
                        "Only parallele magnetization are available for HoleMagnet found: "
                        + label
                    )
            elif MAG_LAB in label_dict["surf_type"]:  # LamSlotMag
                mag_obj = get_obj_from_label(machine, label_dict=label_dict)

                # type_magnetization: 0 for radial, 1 for parallel, 2 for Hallbach
                if mag_obj.type_magnetization == 0 and (label_dict["S_id"] % 2) == 0:
                    mag = "theta"  # Radial North pole magnet
                elif mag_obj.type_magnetization == 0:
                    mag = "theta + 180"  # Radial South pole magnet
                elif mag_obj.type_magnetization == 1 and (label_dict["S_id"] % 2) == 0:
                    mag = (
                        np.angle(point_ref) * 180 / np.pi
                    )  # Parallel North pole magnet
                elif mag_obj.type_magnetization == 1:
                    mag = (
                        np.angle(point_ref) * 180 / np.pi + 180
                    )  # Parallel South pole magnet
                elif mag_obj.type_magnetization == 2:
                    lam_obj = mag_obj.parent
                    Zs = lam_obj.get_Zs()
                    mag = str(-(Zs / 2 - 1)) + " * theta + 90 "
                elif mag_obj.type_magnetization == 3 and (label_dict["S_id"] % 2) == 0:
                    mag = (
                        np.angle(point_ref) * 180 / np.pi - 90
                    )  # Tangential North pole magnet
                elif mag_obj.type_magnetization == 3:
                    mag = (
                        np.angle(point_ref) * 180 / np.pi + 180 - 90
                    )  # Tangential South pole magnet

                # Assign magnet group (assuming one magnet per pole)
                group = group[label_dict["S_id"]]

            elif VENT_LAB in label_dict["surf_type"]:
                vent_obj = get_obj_from_label(machine, label_dict=label_dict)
                prop = "Air"
            elif HOLEV_LAB in label_dict["surf_type"]:
                hole_obj = get_obj_from_label(machine, label_dict=label_dict)
                prop = "Air"

            # Set the surface property
            self.handler.mi_setblockprop(
                prop,
                mesh_dict["automesh"],
                mesh_dict["meshsize"],
                Clabel,
                mag,
                group,
                Ntcoil,
            )
            self.handler.mi_clearselected()

    @staticmethod
    def comp_FEMM_dict(
        machine: Machine,
        Kgeo_fineness: float,
        Kmesh_fineness: float,
        T_mag: float,
        type_calc_leakage: int = 0,
        sym: int = 1,
    ) -> dict:
        """Compute the parameters needed for FEMM simulations

        Parameters
        ----------
        machine : Machine
            The machine to draw
        Kgeo_fineness : float
            global coefficient to adjust geometry fineness in FEMM
            (1 : default ; > 1 : finner ; < 1 : less fine)
        Kmesh_fineness : float
            global coefficient to adjust mesh fineness in FEMM
            (1 :default ; > 1 : finner ; < 1 : less fine)
        T_mag: float
            Permanent magnet temperature [deg Celsius]
        type_calc_leakage : int
            0 no leakage calculation
            1 calculation using single slot
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        FEMM_dict : dict
            dictionary containing the main parameters of FEMM

        """

        FEMM_dict = {}
        # Gather the main Simulation/model related parameters
        FEMM_dict["simu"] = {}
        if type_calc_leakage == 1:
            FEMM_dict["simu"]["is_close_model"] = 1
        else:
            FEMM_dict["simu"]["is_close_model"] = 0
        FEMM_dict["simu"]["acsolver"] = acsolver
        FEMM_dict["simu"]["pbtype"] = pbtype
        FEMM_dict["simu"]["precision"] = precision
        FEMM_dict["simu"]["minangle"] = minangle
        FEMM_dict["simu"]["freqpb"] = 0  # setting 2D magnetostatic problem
        # assign unitary length to calculate torque and flux linkage per meter unit
        FEMM_dict["simu"]["Lfemm"] = 1
        FEMM_dict["simu"]["T_mag"] = T_mag

        # Gather all mesh related parameters
        FEMM_dict["mesh"] = {}
        FEMM_dict["mesh"]["smart_mesh"] = 0
        FEMM_dict["mesh"]["automesh"] = 0  # 1 to let the solver define the mesh in all
        # regions(except in the airgap), otherwise meshsize_XXX parameters are used
        FEMM_dict["mesh"]["automesh_airgap"] = (
            0  # 1 to let the solver define the mesh in the
        )
        #  airgap, otherwise meshsize_airgap is used
        FEMM_dict["mesh"]["automesh_segments"] = (
            0  # 1 to let the solver define the mesh
        )
        # points along arcs and segments, otherwise arcspan_XXX and
        # elementsize_XXX are used

        FEMM_dict["mesh"]["maxsegdeg"] = (
            1  # max angular width of elementary segment along
        )
        # arc discretization(default: 1)
        FEMM_dict["mesh"]["maxelementsize"] = (
            1  # max length of elementary segment along
        )
        # segment discretization(1 for automatic meshing) "elementsize" in FEMM doc
        FEMM_dict["mesh"]["arcspan"] = (
            1 / Kgeo_fineness
        )  # max span of arc element in degrees

        # Add all mesh size for all Laminations
        for lam in machine.get_lam_list():
            label = lam.get_label()
            # Recompute because machine may has been modified
            Hsy = lam.comp_height_yoke()
            Hs = lam.Rext - lam.Rint
            Hstot = Hs - Hsy  # Works with holes and slot

            # Store all the elements size for the lamination
            FEMM_dict["mesh"][label] = {}
            if lam.is_stator:
                # stator slot region mesh and segments max element size parameter
                # If Hstot = 0 there is no slot and the region parameter won't be used
                FEMM_dict["mesh"][label]["meshsize_slot"] = (
                    max(Hstot, Hs / 2) / 8 / Kmesh_fineness
                )
                FEMM_dict["mesh"][label]["elementsize_slot"] = (
                    max(Hstot, Hs / 2) / 8 / Kmesh_fineness
                )
                # stator yoke region mesh and segments max element size parameter
                FEMM_dict["mesh"][label]["meshsize_yoke"] = (
                    min(Hsy, Hs / 2) / 4 / Kmesh_fineness
                )
                FEMM_dict["mesh"][label]["elementsize_yoke"] = (
                    min(Hsy, Hs / 2) / 4 / Kmesh_fineness
                )
            else:
                # rotor slot region mesh and segments max element size parameter
                if isinstance(lam, (LamSlotM, LamH)):
                    FEMM_dict["mesh"][label]["meshsize_slot"] = Hsy / 4 / Kmesh_fineness
                    FEMM_dict["mesh"][label]["elementsize_slot"] = (
                        Hsy / 4 / Kmesh_fineness
                    )
                else:
                    FEMM_dict["mesh"][label]["meshsize_slot"] = (
                        Hstot / 8 / Kmesh_fineness
                    )
                    FEMM_dict["mesh"][label]["elementsize_slot"] = (
                        Hstot / 8 / Kmesh_fineness
                    )
                # rotor yoke region mesh and segments max element size parameter
                FEMM_dict["mesh"][label]["meshsize_yoke"] = Hsy / 4 / Kmesh_fineness
                FEMM_dict["mesh"][label]["elementsize_yoke"] = Hsy / 4 / Kmesh_fineness
            # Wedge mesh
            FEMM_dict["mesh"][label]["meshsize_wedge"] = Hstot / 20 / Kmesh_fineness
            # key mesh
            if lam.has_key():
                notch = [notch for notch in lam.notch if notch.has_key()][0]
                Hkey = notch.notch_shape.comp_height_active()
                FEMM_dict["mesh"][label]["meshsize_key"] = Hkey / 4 / Kmesh_fineness
                FEMM_dict["mesh"][label]["elementsize_key"] = Hkey / 4 / Kmesh_fineness

            # mesh parameter for stator and rotor slot region
            if type_calc_leakage == 1:
                FEMM_dict["mesh"][label]["meshsize_slot"] = Hstot / 50

            # magnet region mesh and segments max element size parameter
            if isinstance(lam, LamSlotM):
                Hmag = (
                    lam.slot.comp_height_active()
                )  # For LamSlotMagNS => slot is North slot
                FEMM_dict["mesh"][label]["meshsize_magnet"] = Hmag / 4 / Kmesh_fineness
                FEMM_dict["mesh"][label]["elementsize_magnet"] = (
                    Hmag / 4 / Kmesh_fineness
                )
            elif isinstance(lam, LamH):
                Hmag = lam.get_hole_list()[0].comp_height()
                FEMM_dict["mesh"][label]["meshsize_magnet"] = Hmag / 4 / Kmesh_fineness
                FEMM_dict["mesh"][label]["elementsize_magnet"] = (
                    Hmag / 4 / Kmesh_fineness
                )
            else:
                FEMM_dict["mesh"][label]["meshsize_magnet"] = None

        # airgap region mesh and segments max element size parameter
        Wgap_mec = machine.comp_width_airgap_mec()
        if isinstance(machine, MachineSIPMSM):
            FEMM_dict["mesh"]["meshsize_airgap"] = Wgap_mec / 10 / Kmesh_fineness
            FEMM_dict["mesh"]["elementsize_airgap"] = Wgap_mec / 10 / Kmesh_fineness
        else:
            FEMM_dict["mesh"]["meshsize_airgap"] = Wgap_mec / 3 / Kmesh_fineness
            FEMM_dict["mesh"]["elementsize_airgap"] = Wgap_mec / 3 / Kmesh_fineness

        # mesh parameter for basic air regions (ventilation ducts etc)
        Hry = machine.get_lam_by_label(ROTOR_LAB).comp_height_yoke()
        FEMM_dict["mesh"]["meshsize_air"] = Hry / 4 / Kmesh_fineness

        # Set groups (to select area by type)
        FEMM_dict["groups"] = {}
        for grp in FEMM_GROUPS:
            if grp != "lam_group_list":
                FEMM_dict["groups"][grp] = FEMM_GROUPS[grp]["ID"]
        grp_max = max(FEMM_dict["groups"].values())

        # Adding lam_group_list linking lam name to related ID
        FEMM_dict["groups"]["lam_group_list"] = {}
        for key, val in FEMM_GROUPS["lam_group_list"].items():
            FEMM_dict["groups"]["lam_group_list"][key] = list(val)

        # Adding a group for each magnet on the lamination
        if isinstance(machine.rotor, (LamSlotM, LamH)):
            nb_mag = machine.rotor.get_magnet_number(sym=sym)
            ndigit = max(len(str(nb_mag)), len(str(grp_max)) - 1)
            grp0 = FEMM_dict["groups"]["GROUP_RM"] * 10**ndigit
            list_mag = [grp0 + ii for ii in range(nb_mag)]
            FEMM_dict["groups"]["GROUP_RM"] = list_mag
            FEMM_dict["groups"]["lam_group_list"][machine.rotor.get_label()].extend(
                list_mag
            )

        # Init empty list
        FEMM_dict["materials"] = []
        FEMM_dict["circuits"] = []

        return FEMM_dict

    def comp_FEMM_Phi_wind(
        self,
        qs: int,
        Npcp: int,
        is_stator: bool,
        L1: float,
        L2: float,
        sym: int,
        is_rescale_flux: bool = True,
    ) -> float:
        """Compute the total flux linkage of the winding phases

        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        qs : int
            number of phases
        Npcp : int
            number of parallel circuits per phase (maximum 2p)
        is_stator : bool
            true if windings are stator windings
        L1 : float
            stator length for rescaling flux linkage
        L2 : float
            rotor length for rescaling flux linkage
        sym : int
            symmetry factor (ie. 1 = full machine, 2 = half machine ...)
        is_rescale_flux : bool
            True if rescaling should be applied

        Returns
        -------
        Phi_wind : float
            fluxlinkage of the winding phases [Vs]

        """
        Phi_wind = np.zeros((1, qs))

        if is_stator:
            label = "Circs"
        else:
            label = "Circr"

        # For each phase/circuit
        for q in range(qs):
            try:
                PropCirc = self.handler.mo_getcircuitproperties(label + str(q))
                # rescaling to account for end winding flux
                if is_rescale_flux:
                    Kphi = L1 / L2
                else:
                    Kphi = 1
                # flux linkage of phase q in Wb=Vs=HA
                Phi_wind[0, q] = sym * PropCirc[2] * Kphi / Npcp
            except Exception:
                Phi_wind[0, q] = None
        return Phi_wind

    def comp_FEMM_torque(self, rotor_groups: list, sym: int = 1) -> float:
        """Compute the torque of the current FEMM simulation result
        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        FEMM_dict : dict
            dict containig FEMM parameters
        """

        # Select rotor groups
        self.handler.mo_seteditmode("area")
        for grp in rotor_groups:
            self.handler.mo_groupselectblock(grp)
        Tem = sym * self.handler.mo_blockintegral(22)

        self.handler.mo_clearblock()

        return Tem

    def create_FEMM_boundary_conditions(self, line_label: str, BC_dict: dict) -> None:
        """Create the boundary conditions in FEMM

        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        sym : int
            Symmetry factor of the machine
        is_antiper : bool
            True if an anti-periodicity is considered

        Returns
        -------
        None
        """
        sym = BC_dict["sym"]
        is_antiper = BC_dict["is_antiper"]
        if sym == 1:
            is_antiper = False

        # anti periodic boundary conditions
        if is_antiper:
            BdPr = 5
        # even number of rotor poles /slots -> periodic boundary conditions
        else:
            BdPr = 4

        # Dirichlet (no flux going out) (on ext lamination yoke)
        if LAM_LAB in line_label and YOKE_LAB in line_label:
            if "bc_A0" not in BC_dict.values():
                self.handler.mi_addboundprop("bc_A0", 0, 0, 0, 0, 0, 0, 0, 0, 0)
            BC_dict[line_label] = "bc_A0"
        # Sliding Band radius
        elif line_label in [SBR_B_LAB, SBR_T_LAB]:
            if "bc_ag2" not in BC_dict.values():
                self.handler.mi_addboundprop("bc_ag2", 0, 0, 0, 0, 0, 0, 0, 0, BdPr + 2)
            BC_dict[SBR_B_LAB] = "bc_ag2"
            BC_dict[SBR_T_LAB] = "bc_ag2"
        # Sliding Band Bottom side
        elif line_label in [SBS_BR_LAB, SBS_BL_LAB]:
            if "bc_ag1" not in BC_dict.values():
                self.handler.mi_addboundprop("bc_ag1", 0, 0, 0, 0, 0, 0, 0, 0, BdPr)
            BC_dict[SBS_BR_LAB] = "bc_ag1"
            BC_dict[SBS_BL_LAB] = "bc_ag1"
        # Sliding Band Top side
        elif line_label in [SBS_TR_LAB, SBS_TL_LAB]:
            if "bc_ag3" not in BC_dict.values():
                self.handler.mi_addboundprop("bc_ag3", 0, 0, 0, 0, 0, 0, 0, 0, BdPr)
            BC_dict[SBS_TR_LAB] = "bc_ag3"
            BC_dict[SBS_TL_LAB] = "bc_ag3"
        #  Airgap Side
        elif line_label in [AS_BR_LAB, AS_BL_LAB]:
            if "bc_ag1" not in BC_dict.values():
                self.handler.mi_addboundprop("bc_ag1", 0, 0, 0, 0, 0, 0, 0, 0, BdPr)
            BC_dict[AS_BR_LAB] = "bc_ag1"
            BC_dict[AS_BL_LAB] = "bc_ag1"
        # Lamination YokeSide for Magnets
        elif YSM_LAB in line_label:
            # Create BC name (bc_ys_r0_M0 for instance - yoke side rotor 0 Magnet R0)
            label_dict = decode_label(line_label)
            if sym != 1:
                bc_name = "bc_ys_"
                if STATOR_LAB in label_dict["lam_type"]:
                    bc_name += "s"
                else:
                    bc_name += "r"
                bc_name += str(label_dict["lam_id"])
                R_id = line_label.split("-")[-1]
                bc_name += "_M" + R_id
                # Create BC
                if bc_name not in BC_dict.values():
                    self.handler.mi_addboundprop(bc_name, 0, 0, 0, 0, 0, 0, 0, 0, BdPr)
            else:
                bc_name = "None"
            # Update dict
            BC_dict[label_dict["lam_label"] + "_" + YSML_LAB + "-" + R_id] = bc_name
            BC_dict[label_dict["lam_label"] + "_" + YSMR_LAB + "-" + R_id] = bc_name
        # Lamination YokeSide for Notches
        elif YSN_LAB in line_label:
            # Create BC name (bc_ys_s0_N for instance - yoke side stator 0 Notche)
            label_dict = decode_label(line_label)
            if sym != 1:
                bc_name = "bc_ys_"
                if STATOR_LAB in label_dict["lam_type"]:
                    bc_name += "s"
                else:
                    bc_name += "r"
                bc_name += str(label_dict["lam_id"])
                bc_name += "_N"
                # Create BC
                if bc_name not in BC_dict.values():
                    self.handler.mi_addboundprop(bc_name, 0, 0, 0, 0, 0, 0, 0, 0, BdPr)
            else:
                bc_name = "None"
            # Update dict
            BC_dict[label_dict["lam_label"] + "_" + YSNL_LAB] = bc_name
            BC_dict[label_dict["lam_label"] + "_" + YSNR_LAB] = bc_name
        # Lamination YokeSide
        elif YS_LAB in line_label:
            label_dict = decode_label(line_label)
            line_id = line_label.split("-")[-1]
            # cf Lamination.get_yoke_side_line for label creation
            if sym != 1:
                # Create BC name (bc_ys_s0_1 for instance - yoke side stator 0 line 1)
                bc_name = "bc_ys_"
                if STATOR_LAB in label_dict["lam_type"]:
                    bc_name += "s"
                else:
                    bc_name += "r"
                bc_name += str(label_dict["lam_id"])
                bc_name += "_" + line_id
                # Create BC
                if bc_name not in BC_dict.values():
                    self.handler.mi_addboundprop(bc_name, 0, 0, 0, 0, 0, 0, 0, 0, BdPr)
            else:
                bc_name = "None"
            # Update dict
            BC_dict[label_dict["lam_label"] + "_" + YSL_LAB + "-" + line_id] = bc_name
            BC_dict[label_dict["lam_label"] + "_" + YSR_LAB + "-" + line_id] = bc_name

    def create_FEMM_circuit_material(
        self,
        circuits: list,
        label_dict: dict,
        is_eddies: bool,
        lam: LamSlotWind,
        I: np.ndarray,
        is_mmf: bool,
        j_t0: int,
        materials: list,
    ) -> tuple[str, list, list]:
        """Set in FEMM circuits property

        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        circuits: list
            list the name of all circuits
        label_dict : dict
            Decoded label of the surface
        sym : bool
            integer for symmetry
        is_eddies :
            1 to calculate eddy currents
        lam : LamSlotWind
            Lamination to set the winding
        I : ndarray
            Lamination currents waveforms
        is_mmf :
            1 to compute the lamination magnetomotive
            force / lamination magnetic field
        j_t0 :
            time step for winding current calculation@type integer
        materials :
            list of materials already created in FEMM

        Returns
        -------
        property, materials, circuits: tuple
            the property of the surface having label as surf.label (str),
            materials (list) and the circuits (list)
        """

        # Load parameter for readibility
        rho = (
            lam.winding.conductor.cond_mat.elec.get_resistivity()
        )  # Resistivity at 20°C
        wind_mat = lam.winding.get_connection_mat(lam.get_Zs())
        Swire = lam.winding.conductor.comp_surface_active()

        # Decode the label
        Nrad_id = label_dict["R_id"]  # zone radial coordinate
        Ntan_id = label_dict["T_id"]  # zone tangential coordinate
        Zs_id = label_dict["S_id"]  # Zone slot number coordinate
        # Get the phase value in the correct slot zone
        q_id = lam.winding.get_phase_id(Nrad_id, Ntan_id, Zs_id, wind_mat=wind_mat)
        s = np.sign(wind_mat[Nrad_id, Ntan_id, Zs_id, q_id])

        # circuit definition
        if ROTOR_LAB in label_dict["lam_type"]:
            Clabel = "Circr" + str(q_id)
        else:
            Clabel = "Circs" + str(q_id)

        circuits = self.set_FEMM_circuit_prop(circuits, Clabel, I=None)

        # definition of armature field current sources
        if ROTOR_LAB in label_dict["lam_type"]:
            Jlabel = "Jr"
        else:
            Jlabel = "Js"
        if s == 1:
            cname = Jlabel + str(q_id) + "+"
        else:
            cname = Jlabel + str(q_id) + "-"

        # circuit definition
        circuits = self.set_FEMM_circuit_prop(circuits, Clabel, I=None)

        # adding new current source material if necessary
        materials = self.set_FEMM_wind_material(
            materials,
            cname=cname,
            Cduct=is_eddies * 1e-6 / rho,
            dwire=np.sqrt(4 * Swire / np.pi) * 1e-3,
        )

        return cname, materials, circuits

    def create_FEMM_magnet(
        self,
        is_mmf: bool,
        is_eddies: bool,
        materials: list,
        mag_obj: Magnet,
        T_mag: float,
    ) -> tuple[str, list]:
        """Set the material of the magnet in FEMM

        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        is_mmfr : bool
            1 to compute the lamination magnetomotive force / magnetic field
        is_eddies : bool
            1 to calculate eddy currents
        materials : list
            list of materials already created in FEMM
        mag_obj : Magnet
            Magnet object to set the material
        T_mag: float
            Permanent magnet temperature [deg Celsius]

        Returns
        -------
        (str, list)
            property, materials

        """

        rho = mag_obj.mat_type.elec.rho  # Resistivity
        Hcm = mag_obj.mat_type.mag.get_Hc(T_op=T_mag)  # Magnet coercitivity field
        mur = mag_obj.mat_type.mag.mur_lin

        mat_name = mag_obj.mat_type.name
        if mat_name not in materials:
            self.handler.mi_addmaterial(
                mat_name,
                mur,
                mur,
                is_mmf * Hcm,
                0,
                is_mmf * is_eddies * 1e-6 / rho,
                0,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
            )
            materials.append(mat_name)

        return mat_name, materials

    def create_FEMM_materials(
        self,
        machine: Machine,
        surf_list: list,
        FEMM_dict: dict,
        Is: np.ndarray,
        Ir: np.ndarray,
        is_mmfs: bool,
        is_mmfr: bool,
        type_BH_stator: int,
        type_BH_rotor: int,
        is_eddies: bool,
        j_t0: int,
    ) -> tuple[dict, dict]:
        """Add materials in FEMM

        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        machine : Machine
            the machine to simulate
        surf_list : list
            List of surface of the machine
        FEMM_dict : dict
            dictionary containing the main parameters of FEMM
        Is : ndarray
            Stator current matrix [A]
        Ir : ndarray
            Rotor current matrix [A]
        is_mmfs : bool
            1 to compute the stator magnetomotive force/stator magnetic field
        is_mmfr : bool
            1 to compute the rotor magnetomotive force / rotor magnetic field
        type_BH_stator: int
            2 Infinite permeability, 1 to use linear B(H) curve according to mur_lin, 0 to use the B(H) curve
        type_BH_rotor: int
            2 Infinite permeability, 1 to use linear B(H) curve according to mur_lin, 0 to use the B(H) curve
        is_eddies : bool
            1 to calculate eddy currents
        jt_0 : int
            Current time step for winding calculation

        Returns
        -------
        prop_dict, FEMM_dict : (dict, dict)
            Dictionary of properties and dictionary containing the main parameters of FEMM
        """

        prop_dict = {}  # Initialisation of the dictionary to return

        rotor = machine.rotor
        stator = machine.stator

        materials = FEMM_dict["materials"]
        circuits = FEMM_dict["circuits"]
        # Starting creation of properties for each surface of the machine
        for surf in surf_list:
            label_dict = decode_label(surf.label)
            if (
                LAM_LAB in label_dict["surf_type"]
                and STATOR_LAB in label_dict["lam_type"]
            ):
                lam_obj = get_obj_from_label(machine, label_dict=label_dict)
                mat_name = label_dict["lam_label"] + " " + LAM_MAT_NAME
                if type_BH_stator == 2:
                    mu_is = 100000  # Infinite permeability
                else:
                    mu_is = lam_obj.mat_type.mag.mur_lin  # Relative
                # Check if the property already exist in FEMM
                if mat_name not in materials:
                    # magnetic permeability
                    self.handler.mi_addmaterial(
                        mat_name, mu_is, mu_is, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0
                    )
                    if type_BH_stator == 0:
                        BHs = lam_obj.mat_type.mag.get_BH()
                        self.add_BH_curve(BHs, mat_name)
                    materials.append(mat_name)
                prop_dict[label_dict["full"]] = mat_name
            elif (
                LAM_LAB in label_dict["surf_type"]
                and ROTOR_LAB in label_dict["lam_type"]
            ):
                lam_obj = get_obj_from_label(machine, label_dict=label_dict)
                mat_name = label_dict["lam_label"] + " " + LAM_MAT_NAME
                # Initialisation from the rotor of the machine
                if type_BH_rotor == 2:
                    mu_ir = 100000  # Infinite permeability
                else:
                    mu_ir = rotor.mat_type.mag.mur_lin  # Relative
                # Check if the property already exist in FEMM
                if mat_name not in materials:
                    # magnetic permeability
                    self.handler.mi_addmaterial(
                        mat_name, mu_ir, mu_ir, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0
                    )
                    if type_BH_rotor == 0:
                        BHr = lam_obj.mat_type.mag.get_BH()
                        self.add_BH_curve(BHr, mat_name)
                    materials.append(mat_name)
                prop_dict[label_dict["full"]] = mat_name
            elif (
                AIRGAP_LAB in label_dict["surf_type"]
                or SLID_LAB in label_dict["surf_type"]
            ):
                # Airgap surface
                if "Airgap" not in materials:
                    self.handler.mi_addmaterial(
                        "Airgap", 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0
                    )
                    materials.append("Airgap")
                prop_dict[label_dict["full"]] = "Airgap"
            elif SOP_LAB in label_dict["surf_type"]:  # Slot opening
                # Assigning air to the slot opening
                if "Air" not in materials:
                    self.handler.mi_addmaterial(
                        "Air", 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0
                    )
                    materials.append("Air")
                prop_dict[label_dict["full"]] = "Air"
            elif WEDGE_LAB in label_dict["surf_type"]:  # Wedge
                # Get the material used for the wedge
                if STATOR_LAB in label_dict["lam_type"]:
                    wedge_mat = stator.slot.wedge_mat
                    lam_mat = stator.mat_type
                elif ROTOR_LAB in label_dict["lam_type"]:
                    wedge_mat = rotor.slot.wedge_mat
                    lam_mat = rotor.mat_type
                mat_name = wedge_mat.name
                # Check if the wedge has the same material as the lamination
                if mat_name == lam_mat.name:
                    mat_name = label_dict["lam_label"] + " " + LAM_MAT_NAME
                elif mat_name not in materials:
                    # Create material if it doesn't already exist
                    self.handler.mi_addmaterial(
                        mat_name,
                        wedge_mat.mag.mur_lin,
                        wedge_mat.mag.mur_lin,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                    )
                    if wedge_mat.mag.BH_curve is not None and not isinstance(
                        wedge_mat.mag.BH_curve,
                        ImportMatrix,  # abstract class
                    ):
                        BH = wedge_mat.mag.BH_curve.get_data()
                        self.add_BH_curve(BH, wedge_mat.name)
                    materials.append(mat_name)
                prop_dict[label_dict["full"]] = mat_name
            elif NOTCH_LAB in label_dict["surf_type"]:  # Notches
                # Same material as Airgap but different mesh
                if "Air" not in materials:
                    self.handler.mi_addmaterial(
                        "Air", 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0
                    )
                    materials.append("Air")
                prop_dict[label_dict["full"]] = "Air"
            elif KEY_LAB in label_dict["surf_type"]:  # Key in notches
                # Get the material used for the wedge
                key_mat = get_obj_from_label(machine, label_dict=label_dict)
                mat_name = key_mat.name
                # Check if the key has the same material as the lamination
                if STATOR_LAB in label_dict["lam_type"]:
                    lam_mat = stator.mat_type
                elif ROTOR_LAB in label_dict["lam_type"]:
                    lam_mat = rotor.mat_type
                if mat_name == lam_mat.name:
                    mat_name = label_dict["lam_label"] + " " + LAM_MAT_NAME
                elif mat_name not in materials:
                    # Create material if it doesn't already exist
                    self.handler.mi_addmaterial(
                        mat_name,
                        key_mat.mag.mur_lin,
                        key_mat.mag.mur_lin,
                        0,
                        0,
                        0,
                        0,
                        0,
                        1,
                        0,
                        0,
                        0,
                        0,
                        0,
                    )
                    if (
                        key_mat.mag.BH_curve is not None
                        and not type(key_mat.mag.BH_curve)
                        is ImportMatrix  # abstract class
                    ):
                        BH = key_mat.mag.BH_curve.get_data()
                        self.add_BH_curve(BH, key_mat.name)
                    materials.append(mat_name)
                prop_dict[label_dict["full"]] = mat_name
            elif VENT_LAB in label_dict["surf_type"]:  # Ventilation
                vent = get_obj_from_label(machine, label_dict=label_dict)
                material = vent.mat_void
                # Check if the property already exist in FEMM
                if "Air" not in materials:
                    self.handler.mi_addmaterial(
                        "Air", 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0
                    )
                    materials.append("Air")
                prop_dict[label_dict["full"]] = "Air"
            elif HOLEV_LAB in label_dict["surf_type"]:  # Hole Void
                hole = get_obj_from_label(machine, label_dict=label_dict)
                material = hole.mat_void
                # Check if the property already exist in FEMM
                if "Air" not in materials:
                    self.handler.mi_addmaterial(
                        "Air", 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0
                    )
                    materials.append("Air")
                prop_dict[label_dict["full"]] = "Air"
            elif (
                WIND_LAB in label_dict["surf_type"]
                or BAR_LAB in label_dict["surf_type"]
            ):
                is_stator = STATOR_LAB in label_dict["lam_type"]
                I = Is if is_stator else Ir
                is_mmf = is_mmfs if is_stator else is_mmfr
                lam_obj = get_obj_from_label(machine, label_dict=label_dict)
                prop, materials, circuits = self.create_FEMM_circuit_material(
                    circuits,
                    label_dict,
                    is_eddies,
                    lam_obj,
                    I,
                    is_mmf,
                    j_t0,
                    materials,
                )
                prop_dict[label_dict["full"]] = prop
            elif (
                MAG_LAB in label_dict["surf_type"]
                or HOLEM_LAB in label_dict["surf_type"]
            ):
                T_mag = FEMM_dict["simu"]["T_mag"]
                is_stator = STATOR_LAB in label_dict["lam_type"]
                is_mmf = is_mmfs if is_stator else is_mmfr
                mag_obj = get_obj_from_label(machine, label_dict=label_dict)
                prop, materials = self.create_FEMM_magnet(
                    is_mmf, is_eddies, materials, mag_obj, T_mag
                )
                prop_dict[label_dict["full"]] = prop
            elif NO_MESH_LAB in label_dict["surf_type"]:
                prop_dict[label_dict["full"]] = "<No Mesh>"
            else:
                raise Exception("Unknown label " + label_dict["full"])

        FEMM_dict["materials"] = materials
        FEMM_dict["circuits"] = circuits
        return prop_dict, FEMM_dict

    def add_BH_curve(self, BH: np.ndarray, mat_name: str) -> None:
        """Add the BH curve of a lamination on femm

        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        BH : ndarray
            BH curve of the material
        mat_name : string
            material name
        """
        if BH is not None and BH.shape[0] > 1:
            for B, H in BH:
                self.handler.mi_addbhpoint(mat_name, H, B)

    def draw_FEMM(
        self,
        output: Output,
        is_mmfr: bool,
        is_mmfs: bool,
        sym: int,
        is_antiper: bool,
        type_calc_leakage: int,
        is_remove_ventS: bool = False,
        is_remove_ventR: bool = False,
        is_remove_slotS: bool = False,
        is_remove_slotR: bool = False,
        type_BH_stator: int = 0,
        type_BH_rotor: int = 0,
        kgeo_fineness: float = 1,
        kmesh_fineness: float = 1,
        user_FEMM_dict: dict = {},
        path_save: str = "FEMM_model.fem",
        is_sliding_band: bool = True,
        transform_list: list = [],
        rotor_dxf: DXFImport | None = None,
        stator_dxf: DXFImport | None = None,
        is_fast_draw: bool = False,
        T_mag: float = 20,
    ) -> dict:
        """Draws and assigns the property of the machine in FEMM

        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        output : Output
            Output object
        is_mmfr : bool
            1 to compute the rotor magnetomotive force / rotor magnetic field
        is_mmfs : bool
            1 to compute the stator magnetomotive force/stator magnetic field
        sym : int
            the symmetry applied on the stator and the rotor (take into account antiperiodicity)
        is_antiper: bool
            To apply antiperiodicity boundary conditions
        type_calc_leakage : int
            0 no leakage calculation, 1 calculation using single slot
        is_remove_ventS : bool
            True to remove the ventilation ducts on stator in FEMM (Default value = False)
        is_remove_ventR : bool
            True to remove the ventilation ducts on rotor in FEMM (Default value = False)
        is_remove_slotS : bool
            True to solve without slot effect on the Stator (Default value = False)
        is_remove_slotR : bool
            True to solve without slot effect on the Rotor (Default value = False)
        type_BH_stator: int
            2 Infinite permeability, 1 to use linear B(H) curve according to mur_lin, 0 to use the B(H) curve
        type_BH_rotor: bool
            2 Infinite permeability, 1 to use linear B(H) curve according to mur_lin, 0 to use the B(H) curve
        kgeo_fineness : float
            global coefficient to adjust geometry fineness
            in FEMM (1: default ; > 1: finner ; < 1: less fine)
        kmesh_fineness : float
            global coefficient to adjust mesh fineness
            in FEMM (1: default ; > 1: finner ; < 1: less fine)
        user_FEMM_dict : dict
            To enforce parameters in the FEMM_dict
        path_save : str
            Path to save resulting fem file
        is_sliding_band : bool
            True to use sliding band else use airgap surface
        transform_list : list
            List of transfromation to apply on the surfaces
        rotor_dxf : DXFImport
            To use a dxf version of the rotor instead of build_geometry
        stator_dxf : DXFImport
            To use a dxf version of the stator instead of build_geometry
        is_fast_draw : bool
            True to use lamination symetry to accelerate the drawing of the machine
        T_mag: float
            Permanent magnet temperature [deg Celsius]

        Returns
        -------
        FEMM_dict : dict
            dictionary containing the main parameters of FEMM (including circuits and materials)
        """

        if transform_list not in [None, []] and is_fast_draw:
            is_fast_draw = False
            get_logger(output).debug("Removing fast_draw for transform_list in FEMM")

        # Initialization from output for readibility
        Is = output.elec.Is  # Stator currents waveforms
        Ir = output.elec.Ir  # Rotor currents waveforms
        machine = output.simu.machine

        # Computing parameter (element size, arcspan...) needed to define the simulation
        FEMM_dict = self.comp_FEMM_dict(
            machine,
            kgeo_fineness,
            kmesh_fineness,
            T_mag,
            type_calc_leakage,
            sym,
        )
        # Overwrite some values if needed
        for key, val in user_FEMM_dict.items():
            for key1, val1 in val.items():
                if isinstance(val1, dict):
                    FEMM_dict[key][key1].update(val1)
                else:
                    FEMM_dict[key][key1] = val1

        # The package must be initialized with the openfemm command.
        try:
            self.handler.openfemm(1)  # 1 == open in background, 0 == open normally
        except Exception as e:
            raise FEMMError(
                "Unable to open FEMM, please check that FEMM is correctly installed\n"
                + str(e)
            )

        # We need to create a new Magnetostatics document to work on.
        self.handler.newdocument(0)

        # Minimize the main window for faster geometry creation.
        # femm.main_minimize()

        # defining the problem
        self.handler.mi_probdef(
            0, "meters", FEMM_dict["simu"]["pbtype"], FEMM_dict["simu"]["precision"]
        )

        # Modifiy the machine to match the conditions
        machine_edit = machine.copy()
        if is_remove_slotR:  # Remove all slots on the rotor
            lam_dict = machine_edit.rotor.as_dict()
            machine_edit.rotor = Lamination(init_dict=lam_dict)
        if is_remove_slotS:  # Remove all slots on the stator
            lam_dict = machine_edit.stator.as_dict()
            machine_edit.stator = Lamination(init_dict=lam_dict)
        # Remove ventilations
        if is_remove_ventR:
            for lam in machine_edit.get_lam_list(is_int_to_ext=True):
                if not lam.is_stator:
                    lam.axial_vent = []
        if is_remove_ventS:
            for lam in machine_edit.get_lam_list(is_int_to_ext=True):
                if lam.is_stator:
                    lam.axial_vent = []

        # Lamination list organized from interior to exterior
        lam_list = machine_edit.get_lam_list(is_int_to_ext=True)

        # Init Boundary condition dict (will be filled while drawing Surface/Lines)
        BC_dict = {"sym": sym, "is_antiper": is_antiper}

        # Draw all the laminations
        for lam in lam_list:
            if lam.is_stator:
                lam_dxf = stator_dxf
            else:
                lam_dxf = rotor_dxf
            FEMM_dict = self.draw_FEMM_lamination(
                machine,
                lam,
                sym,
                FEMM_dict,
                transform_list,
                lam_dxf,
                BC_dict,
                Is,
                Ir,
                is_mmfs,
                is_mmfr,
                type_BH_stator,
                type_BH_rotor,
                is_fast_draw,
            )

        # List of the Non lamination related surfaces
        other_surf_list = []

        # Adding no_mesh for shaft if needed
        if lam_list[0].Rint > 0 and sym == 1:
            label_int = lam_list[0].get_label()
            other_surf_list.append(
                Circle(
                    point_ref=0,
                    radius=lam_list[0].Rint,
                    label=label_int + "_" + NO_MESH_LAB,
                )
            )

        # Adding the Airgap surface
        for ii in range(len(lam_list) - 1):
            if is_sliding_band:
                other_surf_list.extend(
                    self.get_sliding_band(
                        sym=sym, lam_int=lam_list[ii], lam_ext=lam_list[ii + 1]
                    )
                )
            else:
                surf_list_ag, point_ref_ag = self.get_airgap_surface(
                    lam_int=lam_list[ii],
                    lam_ext=lam_list[ii + 1],
                    sym=sym,
                )
                other_surf_list.extend(surf_list_ag)
                # FEMM_dict["point_ref_ag"] = point_ref_ag Unused

        # Draw the surfaces not related to lamination
        self.draw_FEMM_surfaces(
            machine,
            other_surf_list,
            FEMM_dict,
            BC_dict,
            Is,
            Ir,
            is_mmfs,
            is_mmfr,
            type_BH_stator,
            type_BH_rotor,
        )

        # Define simulation parameters
        # femm.mi_zoomnatural()  # Zoom out
        self.handler.mi_probdef(
            FEMM_dict["simu"]["freqpb"],
            "meters",
            FEMM_dict["simu"]["pbtype"],
            FEMM_dict["simu"]["precision"],
            FEMM_dict["simu"]["Lfemm"],
            FEMM_dict["simu"]["minangle"],
            FEMM_dict["simu"]["acsolver"],
        )
        self.handler.mi_smartmesh(FEMM_dict["mesh"]["smart_mesh"])
        if path_save is not None:
            get_logger(output).debug("Saving FEMM file at: " + path_save)
            self.handler.mi_saveas(path_save)  # Save
            FEMM_dict["path_save"] = path_save
            # femm.mi_close()

        return FEMM_dict

    def draw_FEMM_lamination(
        self,
        machine: Machine,
        lam: Lamination,
        sym: int,
        FEMM_dict: dict,
        transform_list: list,
        lam_dxf: DXFImport,
        BC_dict: dict,
        Is: np.ndarray,
        Ir: np.ndarray,
        is_mmfs: bool = True,
        is_mmfr: bool = True,
        type_BH_stator: int = 0,
        type_BH_rotor: int = 0,
        is_fast_draw: bool = False,
    ) -> dict:
        """Draw a Lamination in FEMM

        Parameters
        ----------
        machine : Machine
            Machine object to draw
        lam : Lamination
            Lamination object to draw
        sym : int
            the symmetry applied on the stator and the rotor (take into account antiperiodicity)
        self : femm_pyleecan
            client to send command to a FEMM instance
        FEMM_dict : dict
            dictionary containing the main parameters of FEMM
        transform_list : list
            List of transfromation to apply on the surfaces
        lam_dxf : DXFImport
            To use a dxf version of the Lamination instead of build_geometry
        BC_dict : dict
            Boundary condition dict ([line label] = BC name)
        Is : ndarray
            Stator current matrix [A]
        Ir : ndarray
            Rotor current matrix [A]
        is_mmfs : bool
            1 to compute the stator magnetomotive force/stator magnetic field
        is_mmfr : bool
            1 to compute the rotor magnetomotive force / rotor magnetic field
        type_BH_stator: int
            2 Infinite permeability, 1 to use linear B(H) curve according to mur_lin, 0 to use the B(H) curve
        type_BH_rotor: int
            2 Infinite permeability, 1 to use linear B(H) curve according to mur_lin, 0 to use the B(H) curve
        is_fast_draw: bool
            True to draw the lamination using the highest periodicity
        Returns
        -------
        FEMM_dict : dict
            dictionary containing the main parameters of FEMM
        """

        # Adding lamination surfaces (or import from DXF)
        if lam_dxf is not None:
            self.handler.mi_readdxf(lam_dxf.file_path)
            surf_list = lam_dxf.get_surfaces()

            sym_draw = sym
            is_draw = True
            type_set_BC = 0
            type_assign = 0
        else:
            # Drawing with smallest periodicities of the lamination depending on is_fast_draw
            if is_fast_draw:
                # Getting the periodicity of the lamination
                sym_draw, is_antiper_a = lam.comp_periodicity_geo()

                if is_antiper_a:
                    sym_draw *= 2

                surf_list = lam.build_geometry(sym=sym_draw, is_circular_radius=True)
                is_draw = False
                type_set_BC = 1
                # Disabling the assign on the build_geometry with sym_draw (done later on build_geometry with sym)
                type_assign = 2
            else:
                sym_draw = sym
                surf_list = lam.build_geometry(sym=sym, is_circular_radius=True)
                is_draw = True
                type_set_BC = 0
                type_assign = 0

        # Applying user defined modifications
        for transform in transform_list:
            for surf in surf_list:
                if transform["label"] in surf.label and transform["type"] == "rotate":
                    surf.rotate(transform["value"])
                elif (
                    transform["label"] in surf.label
                    and transform["type"] == "translate"
                ):
                    surf.translate(transform["value"])

        # Draw all the lamination related surfaces with/without assigning the surfaces
        FEMM_dict = self.draw_FEMM_surfaces(
            machine,
            surf_list,
            FEMM_dict,
            BC_dict,
            Is,
            Ir,
            is_mmfs,
            is_mmfr,
            type_BH_stator,
            type_BH_rotor,
            type_assign=type_assign,
            type_set_BC=type_set_BC,
        )

        # Duplicate periodic parts if sym_draw > sym
        if sym != sym_draw:
            self.handler.mi_seteditmode("group")
            lam_label = lam.get_label()
            for val in FEMM_dict["groups"]["lam_group_list"][lam_label]:
                self.handler.mi_selectgroup(val)
            Ncopy = int(round(sym_draw / sym))
            self.handler.mi_copyrotate(0, 0, 360 / sym / Ncopy, Ncopy - 1)

        # BC + Assigning surface with the machine symetry instead of the lam symetry
        if is_fast_draw:
            surf_list_2 = lam.build_geometry(sym=sym, is_circular_radius=True)

            FEMM_dict = self.draw_FEMM_surfaces(
                machine,
                surf_list_2,
                FEMM_dict,
                BC_dict,
                Is,
                Ir,
                is_mmfs,
                is_mmfr,
                type_BH_stator,
                type_BH_rotor,
                type_assign=1,
                type_set_BC=0,
                is_draw=is_draw,
            )

        # Apply BC for DXF import
        if lam_dxf is not None:
            for BC in lam_dxf.BC_list:
                if BC[1] is True:  # Select Arc
                    self.handler.mi_selectarcsegment(BC[0].real, BC[0].imag)
                    self.handler.mi_setarcsegmentprop(
                        FEMM_dict["mesh"]["arcspan"], BC[2], False, None
                    )
                else:  # Select Line
                    self.handler.mi_selectsegment(BC[0].real, BC[0].imag)
                    self.handler.mi_setsegmentprop(BC[2], None, None, False, None)
                self.handler.mi_clearselected()

        return FEMM_dict

    def draw_FEMM_surfaces(
        self,
        machine: Machine,
        surf_list: list,
        FEMM_dict: dict,
        BC_dict: dict,
        Is: np.ndarray,
        Ir: np.ndarray,
        is_mmfs: bool,
        is_mmfr: bool,
        type_BH_stator: int,
        type_BH_rotor: int,
        type_assign: int = 0,
        type_set_BC: int = 0,
        is_draw: bool = True,
    ) -> dict:
        """Draw a list of surfaces in FEMM

        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        machine : Machine
            Machine object to draw
        surf_list : list
            List of surfaces to draw
        FEMM_dict : dict
            dictionary containing the main parameters of FEMM
        BC_dict : dict
            Boundary condition dict ([line label] = BC name)
        Is : ndarray
            Stator current matrix [A]
        Ir : ndarray
            Rotor current matrix [A]
        is_mmfs : bool
            1 to compute the stator magnetomotive force/stator magnetic field
        is_mmfr : bool
            1 to compute the rotor magnetomotive force / rotor magnetic field
        type_BH_stator: int
            2 Infinite permeability, 1 to use linear B(H) curve according to mur_lin, 0 to use the B(H) curve
        type_BH_rotor: int
            2 Infinite permeability, 1 to use linear B(H) curve according to mur_lin, 0 to use the B(H) curve
        type_assign : int
            2 to assign all but WIND and MAG, 1 to assign WIND and MAG and 0 to assign all
        type_set_BC : bool
            1 to set BC of the yoke only, 0 to set all
        is_draw : bool
            1 to draw the list of surfaces given
        Returns
        -------
        FEMM_dict : dict
            dictionary containing the main parameters of FEMM
        """
        # Creation of all the materials and circuit in FEMM
        prop_dict, FEMM_dict = self.create_FEMM_materials(
            machine,
            surf_list,
            FEMM_dict,
            Is,
            Ir,
            is_mmfs,
            is_mmfr,
            type_BH_stator,
            type_BH_rotor,
            is_eddies,
            j_t0=0,
        )

        # Draw and assign all the surfaces of the machine
        for surf in surf_list:
            label = surf.label

            # Get the correct element size and group according to the label
            surf.draw_FEMM(
                femm=self,
                nodeprop="None",
                maxseg=FEMM_dict["mesh"][
                    "arcspan"
                ],  # max span of arc element in degrees
                FEMM_dict=FEMM_dict,
                hide=False,
                BC_dict=BC_dict,
                is_draw=is_draw,
                type_set_BC=type_set_BC,
            )

            # Detecting if the property assigned is related to the magnet or the winding
            label_dict = decode_label(label)

            is_mag_wind_lab = (
                WIND_LAB in label_dict["surf_type"]
                or BAR_LAB in label_dict["surf_type"]
                or HOLEM_LAB in label_dict["surf_type"]
                or MAG_LAB in label_dict["surf_type"]
            )

            if (
                type_assign == 0
                or (type_assign == 1 and is_mag_wind_lab)
                or (type_assign == 2 and not is_mag_wind_lab)
            ):
                self.assign_FEMM_surface(surf, prop_dict[label], FEMM_dict, machine)

        return FEMM_dict

    @staticmethod
    def get_airgap_surface(
        lam_int: Lamination, lam_ext: Lamination, sym: int = 1
    ) -> tuple[list, complex]:
        """Returns a list of surface in the airgap without sliding band surface

        Parameters
        ----------
        lam_int:
            Internal lamination
        lam_ext:
            External lamination

        Returns
        -------
        surf_list: list
            List of surface in the airgap without sliding band surface
        point_ref: complex
            Airgap point ref
        """

        surf_list = []

        Rgap_mec_int = lam_int.comp_radius_mec()
        Rgap_mec_ext = lam_ext.comp_radius_mec()
        Wgap_mec = Rgap_mec_ext - Rgap_mec_int

        point_ref = (Rgap_mec_int + Wgap_mec / 2) * np.exp(1j * np.pi / sym / 2)

        if sym == 1:
            line_list: list[Line] = []
        else:
            Z1 = lam_int.get_Rbo()
            Z2 = lam_ext.get_Rbo()

            Z1_bis = Z1 * np.exp(1j * 2 * np.pi / sym)
            Z2_bis = Z2 * np.exp(1j * 2 * np.pi / sym)

            line_list: list[Line] = [
                Segment(begin=Z1, end=Z2, prop_dict={BOUNDARY_PROP_LAB: AS_BR_LAB}),
                Segment(
                    begin=Z1_bis, end=Z2_bis, prop_dict={BOUNDARY_PROP_LAB: AS_BL_LAB}
                ),
            ]

        # Middle
        surf_list.append(
            SurfLine(
                line_list=line_list,
                point_ref=point_ref,
                label=NO_LAM_LAB + "_" + AIRGAP_LAB,
            )
        )

        return surf_list, point_ref

    def get_FEMM_BC_propname(self, line_label: str, BC_dict: dict) -> str:
        """Get/create the Boundary coundition corresponding the line

        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        line_label : str
            BOUNDARY_PROP_LAB of the line
        BC_dict : dict
            Boundary condition dict ([line label] = BC name)

        Returns
        -------
        propname : str
            Name of the property to set
        """

        if line_label not in BC_dict:
            self.create_FEMM_boundary_conditions(line_label, BC_dict)
        return BC_dict[line_label]

    @staticmethod
    def get_mesh_param(label_dict: str, FEMM_dict: dict) -> dict:
        """Returns main mesh parameters corresponding to a surface label
        Parameters
        ----------
        label_dict : str
            Decoded label of the surface to assign
        FEMM_dict : dict
            dictionary containing the main parameters of FEMM
        Returns
        -------
        mesh_dict : dict
            dictionary containing the main mesh parameters of the surface
        """

        mesh_dict = {}

        # Default automesh except airgap
        mesh_dict["automesh"] = FEMM_dict["mesh"]["automesh"]
        # Get the mesh sizes related to the lamination label
        if label_dict["lam_label"] != "None":
            lam_mesh_dict = FEMM_dict["mesh"][label_dict["lam_label"]]
        else:
            lam_mesh_dict = None
        maxelementsize = FEMM_dict["mesh"]["maxelementsize"]
        meshsize_air = FEMM_dict["mesh"]["meshsize_air"]

        # Lamination
        if LAM_LAB in label_dict["surf_type"]:
            if BORE_LAB in label_dict["surf_type"]:
                mesh_dict["element_size"] = FEMM_dict["mesh"]["elementsize_airgap"]
                mesh_dict["meshsize"] = FEMM_dict["mesh"]["meshsize_airgap"]
            else:  # Yoke or other lines
                mesh_dict["element_size"] = lam_mesh_dict["elementsize_yoke"]
                mesh_dict["meshsize"] = lam_mesh_dict["meshsize_yoke"]
            if STATOR_LAB in label_dict["lam_type"]:
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_SC"]
            elif ROTOR_LAB in label_dict["lam_type"]:
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_RC"]
        # Ventilation
        elif VENT_LAB in label_dict["surf_type"]:
            mesh_dict["element_size"] = maxelementsize
            mesh_dict["meshsize"] = meshsize_air
            if STATOR_LAB in label_dict["lam_type"]:
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_SV"]
            else:  # if the Ventilation is on the Rotor
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_RV"]
        # Hole Air zone
        elif HOLEV_LAB in label_dict["surf_type"]:
            mesh_dict["element_size"] = maxelementsize
            mesh_dict["meshsize"] = meshsize_air
            if STATOR_LAB in label_dict["lam_type"]:  # if the Hole is on the Stator
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_SH"]
            else:  # if the Hole is on the Rotor
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_RH"]
        # Magnet or HoleMagnet
        elif HOLEM_LAB in label_dict["surf_type"] or MAG_LAB in label_dict["surf_type"]:
            mesh_dict["element_size"] = lam_mesh_dict["elementsize_magnet"]
            mesh_dict["meshsize"] = lam_mesh_dict["meshsize_magnet"]
            if STATOR_LAB in label_dict["lam_type"]:  # if the Magnet is on the Stator
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_SM"]
            else:  # if the Magnet is on the Rotor
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_RM"]
        # Winding or Bar
        elif WIND_LAB in label_dict["surf_type"] or BAR_LAB in label_dict["surf_type"]:
            mesh_dict["element_size"] = lam_mesh_dict["elementsize_slot"]
            mesh_dict["meshsize"] = lam_mesh_dict["meshsize_slot"]
            if STATOR_LAB in label_dict["lam_type"]:  # if the winding is on the Stator
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_SW"]
            else:  # if the winding is on the Rotor
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_RW"]
        # Slot opening
        elif SOP_LAB in label_dict["surf_type"]:
            mesh_dict["element_size"] = lam_mesh_dict["elementsize_slot"]
            mesh_dict["meshsize"] = lam_mesh_dict["meshsize_slot"]
            if STATOR_LAB in label_dict["lam_type"]:  # if the opening is on the Stator
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_SSI"]
            else:
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_RSI"]
        # Slot Notches
        elif NOTCH_LAB in label_dict["surf_type"]:
            mesh_dict["element_size"] = lam_mesh_dict["elementsize_slot"]
            mesh_dict["meshsize"] = lam_mesh_dict["meshsize_slot"]
            if STATOR_LAB in label_dict["lam_type"]:  # if the notch is on the Stator
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_SN"]
            else:  # if the notch is on the Rotor
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_RN"]
        # Slot Wedges
        elif WEDGE_LAB in label_dict["surf_type"]:
            mesh_dict["element_size"] = lam_mesh_dict["elementsize_slot"]
            mesh_dict["meshsize"] = lam_mesh_dict["meshsize_slot"]
            if STATOR_LAB in label_dict["lam_type"]:
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_SWE"]
            else:
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_RWE"]
        # Notches Keys
        elif KEY_LAB in label_dict["surf_type"]:
            mesh_dict["element_size"] = lam_mesh_dict["elementsize_key"]
            mesh_dict["meshsize"] = lam_mesh_dict["meshsize_key"]
            if STATOR_LAB in label_dict["lam_type"]:
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_SK"]
            else:
                mesh_dict["group"] = FEMM_dict["groups"]["GROUP_RK"]
        # Sliding Band / Airgap
        elif (
            SLID_LAB in label_dict["surf_type"] or AIRGAP_LAB in label_dict["surf_type"]
        ):
            mesh_dict["automesh"] = FEMM_dict["mesh"]["automesh_airgap"]
            mesh_dict["element_size"] = FEMM_dict["mesh"]["elementsize_airgap"]
            mesh_dict["meshsize"] = FEMM_dict["mesh"]["meshsize_airgap"]
            mesh_dict["group"] = FEMM_dict["groups"]["GROUP_AG"]
        elif NO_MESH_LAB in label_dict["surf_type"]:
            mesh_dict["automesh"] = 0
            mesh_dict["element_size"] = 0
            mesh_dict["meshsize"] = 0
            mesh_dict["group"] = FEMM_dict["groups"]["GROUP_AG"]
        elif STATOR_LAB in label_dict["lam_type"]:
            # if label don't belong to any of the other groups
            mesh_dict["element_size"] = maxelementsize
            mesh_dict["group"] = FEMM_dict["groups"]["GROUP_SC"]
        elif ROTOR_LAB in label_dict["lam_type"]:
            # if label don't belong to any of the other groups
            mesh_dict["element_size"] = maxelementsize
            mesh_dict["group"] = FEMM_dict["groups"]["GROUP_RC"]
        else:
            raise Exception(
                "Error while assigning surfaces in FEMM: Unknown label "
                + label_dict["full"]
            )
        return mesh_dict

    @staticmethod
    def get_sliding_band(sym: int, lam_int: Lamination, lam_ext: Lamination) -> list:
        """Returns  a list of surface in the airgap including the sliding band surface

        Parameters
        ----------
        sym: int
            Symmetry factor (1= full machine, 2= half of the machine...)
        Rgap_mec_int: float
            Internal lamination mechanic radius
        Rgap_mec_ext: float
            External lamination mechanic radius

        Returns
        -------
        surf_list: list
            List of surface in the airgap including the sliding band surface
        """

        Rgap_mec_int, Rgap_mec_ext = (
            lam_int.comp_radius_mec(),
            lam_ext.comp_radius_mec(),
        )
        Rgap_0_int, Rgap_0_ext = femm_pyleecan._get_radius_boundary(
            sym, lam_int, lam_ext
        )
        Wgap_mec = Rgap_mec_ext - Rgap_mec_int
        W_sb = Wgap_mec / 3  # Width sliding band
        surf_list = []
        label_int = lam_int.get_label()
        label_ext = lam_ext.get_label()

        if sym == 1:  # Complete machine
            # Bottom sliding band
            surf_list.append(
                Circle(
                    center=0,
                    radius=Rgap_mec_int + W_sb,
                    label=label_int + "_" + SLID_LAB,
                    point_ref=(Rgap_mec_int + W_sb / 2) * np.exp(1j * np.pi / 2),
                    prop_dict={BOUNDARY_PROP_LAB: SBR_B_LAB},  # Bottom Radius
                )
            )
            # Top sliding band
            surf_list.append(
                Circle(
                    center=0,
                    radius=Rgap_mec_int + 2 * W_sb,
                    label=label_ext + "_" + SLID_LAB,
                    point_ref=(Rgap_mec_ext - W_sb / 2) * np.exp(1j * np.pi / 2),
                    prop_dict={BOUNDARY_PROP_LAB: SBR_T_LAB},  # Top Radius
                )
            )
            # Middle
            surf_list.append(
                SurfLine(
                    line_list=[],
                    point_ref=(Rgap_mec_int + W_sb * 3 / 2) * np.exp(1j * np.pi / 2),
                    label=NO_LAM_LAB + "_" + NO_MESH_LAB,
                )
            )
        else:  # Symmetry
            # Bottom line
            if hasattr(lam_int, "slot") and lam_int.slot.is_full_pitch_active():
                # Cylinder magnet/winding => limit is mec airgap
                Z1 = Rgap_mec_int
            else:
                Z1 = Rgap_0_int
            Z2 = Rgap_mec_int + W_sb
            Z3 = Z2 * np.exp(1j * 2 * np.pi / sym)
            Z4 = Z1 * np.exp(1j * 2 * np.pi / sym)
            airgap_lines: list[Line] = []
            airgap_lines.append(  # Bottom Right side
                Segment(begin=Z1, end=Z2, prop_dict={BOUNDARY_PROP_LAB: SBS_BR_LAB})
            )
            airgap_lines.append(
                Arc1(
                    begin=Z2,
                    end=Z3,
                    radius=Rgap_mec_int + W_sb,  # Bottom Radius
                    prop_dict={BOUNDARY_PROP_LAB: SBR_B_LAB},
                )
            )
            airgap_lines.append(  # Bottom Left side
                Segment(begin=Z3, end=Z4, prop_dict={BOUNDARY_PROP_LAB: SBS_BL_LAB})
            )
            surf_list.append(
                SurfLine(
                    line_list=airgap_lines,
                    point_ref=(Z2 - W_sb / 2) * np.exp(1j * np.pi / sym),
                    label=label_int + "_" + SLID_LAB,
                )
            )
            # Top line
            if hasattr(lam_ext, "slot") and lam_ext.slot.is_full_pitch_active():
                # Cylinder magnet/winding => limit is mec airgap
                Z5 = Rgap_mec_ext
            else:
                Z5 = Rgap_0_ext
            Z6 = Rgap_mec_ext - W_sb
            Z7 = Z6 * np.exp(1j * 2 * np.pi / sym)
            Z8 = Z5 * np.exp(1j * 2 * np.pi / sym)
            airgap_lines = []
            airgap_lines.append(  # Top Right Side
                Segment(begin=Z5, end=Z6, prop_dict={BOUNDARY_PROP_LAB: SBS_TR_LAB})
            )
            airgap_lines.append(
                Arc1(  # Top Radius
                    begin=Z6,
                    end=Z7,
                    radius=Rgap_mec_ext - W_sb,
                    prop_dict={BOUNDARY_PROP_LAB: SBR_T_LAB},
                )
            )
            airgap_lines.append(  # Top Left Side
                Segment(begin=Z7, end=Z8, prop_dict={BOUNDARY_PROP_LAB: SBS_TL_LAB})
            )
            surf_list.append(
                SurfLine(
                    line_list=airgap_lines,
                    point_ref=(Z6 + W_sb / 2) * np.exp(1j * np.pi / sym),
                    label=label_ext + "_" + SLID_LAB,
                )
            )

        return surf_list

    @staticmethod
    def _get_radius_boundary(
        sym: int, lam_int: LamSlot, lam_ext: LamSlot
    ) -> tuple[float, float]:
        """Returns the radii of the laminations on the x axis

        Parameters
        ----------
        lam_int: LamSlot
            Lamination on the internal side
        lam_ext: LamSlot
            Lamination on the external side

        Returns
        -------
        Rint, Rext: float
            Radii of the laminantions on the x axis
        """
        # No bore => is_circular_radius make sure Rbo is Ok even
        # with notch on Ox
        if lam_int.bore is None and not lam_int.has_key():
            Rint = lam_int.get_Rbo()
        elif lam_int.has_key():
            Rint = None
            for notch in lam_int.notch:
                # get_key_Ox_radius return None if no intersection
                # Only one set can intersect with Ox
                if notch.has_key() and Rint is None:
                    Rint = notch.get_key_Ox_radius()
            # No key on Ox => Rbo (if notches, closing surface is added)
            if Rint is None:
                Rint = lam_int.get_Rbo()
        else:
            # With bore shape even with notches, we compute the first point coordinate
            bore_list = lam_int.build_radius_lines(sym=sym, is_bore=True)
            Rint = abs(bore_list[0].get_begin())

        # Same for external lamination
        if lam_ext.bore is None and not lam_ext.has_key():
            Rext = lam_ext.get_Rbo()
        elif lam_ext.has_key():
            Rext = None
            for notch in lam_ext.notch:
                # get_key_Ox_radius return None if no intersection
                # Only one set can intersect with Ox
                if notch.has_key() and Rext is None:
                    Rext = notch.get_key_Ox_radius()
            # No key on Ox => Rbo (if notches, closing surface is added)
            if Rext is None:
                Rext = lam_ext.get_Rbo()
        else:
            bore_list = lam_ext.build_radius_lines(sym=sym, is_bore=True)
            Rext = abs(bore_list[0].get_begin())

        return Rint, Rext

    def set_FEMM_circuit_prop(
        self, circuits: list, Clabel: str, I: np.ndarray | None = None
    ) -> list:
        """Create or update the property of a circuit

        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        circuits: list
            list the name of all circuits
        Clabel: str
            the label of the circuit surface
        q_id : int
            Index of the phase
        I : ndarray
            Lamination currents for given time step and for all phases [qs,1]

        Returns
        -------
        circuits : list
            list the name of the circuits in FEMM

        """

        # Find phase index of current surface label
        q_id = int(Clabel[5:])

        if Clabel not in circuits:
            # Create new circuit
            self.handler.mi_addcircprop(Clabel, 0, 1)
            circuits.append(Clabel)

        # Update circuit
        if I is not None:
            self.handler.mi_modifycircprop(Clabel, 1, I[q_id])
        else:
            self.handler.mi_modifycircprop(Clabel, 1, 0)

        return circuits

    def set_FEMM_wind_material(
        self,
        materials: list,
        cname: str,
        Jcus: float = 0,
        Cduct: float | None = None,
        dwire: float | None = None,
    ) -> list:
        """Create or update the property of a winding material

        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        materials: list
            list the name of all materials
        cname: str
            name of the material to create/update
        Jcus : float
            Applied source current density [A/mm^2]
        Cduct : float
            Electrical conductivity of the material [MS/m]
        dwire : float
            Diameter of each of the wire’s constituent strand [mm]

        Returns
        -------
        circuits : list
            list the name of the circuits in FEMM

        """
        if cname not in materials:
            # Create a new material
            self.handler.mi_addmaterial(
                cname,
                1,  # Relative permeability in the x- or r-direction
                1,  # Relative permeability in the y- or z-direction
                0,  # Permanent magnet coercivity [A/m]
                Jcus,
                Cduct,
                0,  # Lamination thickness [mm]
                0,  # Hysteresis lag angle [deg], (used for nonlinear BH curves)
                1,  # Fraction of the volume occupied per lamination that is actually filled withiron
                0,  # LamType (Not laminated)
                0,  # Hysteresis lag [deg] in the x-direction for linear problems
                0,  # Hysteresis lag [deg] in the y-direction for linear problems
                1,  # Number of strands in the wire build
                dwire,
            )
            materials.append(cname)

        return materials

    def update_FEMM_simulation(
        self,
        FEMM_dict: dict,
        is_internal_rotor: bool,
        is_sliding_band: bool,
        angle_rotor: np.ndarray,
        Is: np.ndarray,
        Ir: np.ndarray,
        ii: int,
    ) -> None:
        """Update the simulation by changing the rotor position and
        updating the currents
        Parameters
        ----------
        self : femm_pyleecan
            client to send command to a FEMM instance
        FEMM_dict : dict
            Dictionary containing main FEMM definition / properties
        is_internal_rotor: bool
            True if it is an Internal Rotor topology
        is_sliding_band: bool
            True if it is an Internal Rotor topology
        angle_rotor: ndarray
            Vector of rotor angular position over time [Nt,]
        Is : ndarray
            Stator currents function of phase and time [qs,Nt]
        Ir : ndarray
            Rotor currents function of phase and time [qr,Nt]
        ii : int
            Time step index
        """

        if is_sliding_band:  # No rotation without sliding band.
            # Rotor rotation using sliding band
            if is_internal_rotor:
                self.handler.mi_modifyboundprop(
                    "bc_ag2", 10, 180 * angle_rotor[ii] / np.pi
                )
            else:
                self.handler.mi_modifyboundprop(
                    "bc_ag2", 11, 180 * angle_rotor[ii] / np.pi
                )

        else:
            # Select and rotate rotor groups
            self.handler.mi_seteditmode("group")
            for key, val in FEMM_dict["groups"]["lam_group_list"].items():
                if "Rotor" in key:
                    for ind in val:
                        self.handler.mi_selectgroup(ind)
            self.handler.mi_moverotate(0, 0, 180 * angle_rotor[ii] / np.pi)

        # Update currents
        if Is is not None or Ir is not None:
            circuits = FEMM_dict["circuits"]
            for label in circuits:
                if "Circs" in label and Is is not None:  # Stator
                    self.set_FEMM_circuit_prop(
                        circuits,
                        label,
                        Is[:, ii],
                    )
                if "Circr" in label and Ir is not None:  # Rotor
                    self.set_FEMM_circuit_prop(
                        circuits,
                        label,
                        Ir[:, ii],
                    )
