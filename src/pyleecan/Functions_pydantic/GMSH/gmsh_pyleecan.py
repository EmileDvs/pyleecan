"""Interface of pyleecan with FEMM (gmsh_pyleecan), written by the functions
generator from the modules of Functions/GMSH (PLAN.md Step 8).
"""

import cmath
import os
import sys
from math import ceil, sqrt
from typing import TYPE_CHECKING

import gmsh
import numpy as np

from ...classes_common.errors import GMSHInputError as InputError
from ...Classes_pydantic.geometry.arc import Arc
from ...Classes_pydantic.geometry.arc_1 import Arc1
from ...Classes_pydantic.geometry.arc_2 import Arc2
from ...Classes_pydantic.geometry.circle import Circle
from ...Classes_pydantic.geometry.segment import Segment
from ...Classes_pydantic.geometry.surf_line import SurfLine
from ...Classes_pydantic.geometry.surf_ring import SurfRing
from ...Classes_pydantic.machine.machine_scim import MachineSCIM
from ...Classes_pydantic.machine.machine_sipmsm import MachineSIPMSM
from ...Classes_pydantic.machine.machine_wrsm import MachineWRSM
from ..get_logger import get_logger
from ..labels import (
    AIRBOX_LAB,
    AIRBOX_R_LAB,
    AIRBOX_SL_LAB,
    AIRBOX_SR_LAB,
    AIRGAP_LAB,
    AR_B_LAB,
    AR_T_LAB,
    AS_BL_LAB,
    AS_BR_LAB,
    AS_TL_LAB,
    AS_TR_LAB,
    BAR_LAB,
    BOT_LAB,
    BOUNDARY_PROP_LAB,
    HOLEM_LAB_S,
    LAM_LAB,
    LAM_LAB_S,
    MAG_LAB,
    NO_LAM_LAB,
    SBR_B_LAB,
    SBR_T_LAB,
    SBS_BL_LAB,
    SBS_BR_LAB,
    SBS_TL_LAB,
    SBS_TR_LAB,
    SHAFT_LAB,
    SLID_LAB,
    TOP_LAB,
    WIND_LAB_S,
    YOKE_LAB,
    decode_label,
    short_label,
)

if TYPE_CHECKING:
    from typing import Any

    from ...Classes_pydantic.geometry.line import Line
    from ...Classes_pydantic.geometry.surface import Surface
    from ...Classes_pydantic.machine.lam_slot import LamSlot
    from ...Classes_pydantic.machine.machine import Machine
    from ...Classes_pydantic.output.output import Output


tol = 1e-6


class gmsh_pyleecan:
    """Interface of pyleecan with gmsh: the gmsh functions of pyleecan

    Static methods for now (the gmsh API is a module): the object gathers the
    functions, to be improved later (PLAN.md Step 8).
    """

    @staticmethod
    def comp_gmsh_mesh_dict(
        surface: Surface, element_size: float, user_mesh_dict: dict = {}
    ) -> dict:
        """Returns the number of mesh elements on each line of the surface
        to match the element_size.

        Parameters
        ----------
        self : Surface
            a Surface object

        element_size : float
            The default size of each element on the mesh [m]

        user_mesh_dict: dictionary
            User specified mesh properties


        Returns
        -------
        mesh_dict : dict
            Dictionary containing the number of element of each line of the surface
        """

        mesh_dict = {}
        # TO-DO: Airgap surfaces are special cases due to the boolean operations
        if "Airgap" in short_label(surface.label):
            return mesh_dict
        lines = surface.get_lines()
        if short_label(surface.label) in user_mesh_dict:
            elements_in_surface = user_mesh_dict[short_label(surface.label)]
            area = surface.comp_surface()
            element_size = area / elements_in_surface
            # Assumption: equilateral triangle
            side_size = sqrt(element_size * 4.0 / 1.73)
        else:
            side_size = element_size

        for ii, line in enumerate(lines):
            label = str(ii)
            # Overwrite number of elements given by boundary name in user_mesh_dict
            if (
                line.prop_dict
                and BOUNDARY_PROP_LAB in line.prop_dict
                and line.prop_dict[BOUNDARY_PROP_LAB] in user_mesh_dict
            ):
                mesh_dict[label] = user_mesh_dict[line.prop_dict[BOUNDARY_PROP_LAB]]
            else:
                length = line.comp_length()
                number_of_element = ceil(length / side_size)
                mesh_dict[label] = number_of_element

        return mesh_dict

    @staticmethod
    def draw_GMSH(
        output: Output,
        sym: int,
        boundary_prop: dict,
        is_lam_only_S: bool = False,
        is_lam_only_R: bool = False,
        user_mesh_dict: dict = {},
        path_save: str = "GMSH_model.msh",
        is_sliding_band: bool = False,
        is_airbox: bool = False,
        is_set_labels: bool = False,
        is_run: bool = False,
    ) -> dict:
        """Draws a machine mesh in GMSH format

        Parameters
        ----------
        output : Output
            Output object
        sym : int
            the symmetry applied on the stator and the rotor (take into account antiperiodicity)
        boundary_prop : dict
            dictionary to match FEA boundary conditions (dict values) with line boundary property (dict keys)
        is_lam_only_S: bool
            Draw only stator lamination
        is_lam_only_R: bool
            Draw only rotor lamination
        user_mesh_dict :dict
            Dictionary to enforce the mesh size on some surface/lines (key: surface label, value dict:key=line id, value:nb element)
        path_save : str
            Path to save the result msh file
        is_sliding_band : bool
            True uses sliding band, else airgap
        is_airbox : bool
            True to add the airbox
        is_set_label : bool
            True to set all line labels as physical groups
        is_run : bool
            True to launch Gmsh GUI at the end

        Returns
        -------
        GMSH_dict : dict
            dictionary containing the main parameters of GMSH File
        """
        # check some input parameter
        if is_lam_only_S and is_lam_only_R:
            raise InputError(
                "is_lam_only_S and is_lam_only_R can't be True at the same time"
            )

        # get machine
        machine = output.simu.machine
        mesh_dict = {}
        tol = 1e-6

        # Default stator mesh element size
        mesh_size_S = machine.stator.Rext / 100.0  # Stator
        mesh_size_R = machine.rotor.Rext / 25.0  # Rotor
        mesh_size_SB = 2.0 * np.pi * machine.rotor.Rext / 360.0  # Sliding Band
        mesh_size_AB = machine.stator.Rext / 50.0  # AirBox
        lam_list = machine.get_lam_list()
        lam_int = lam_list[0]
        lam_ext = lam_list[1]
        lab_int = lam_int.get_label()
        lab_ext = lam_ext.get_label()

        # For readibility
        model = gmsh.model
        factory = model.occ

        # Start a new model
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", int(False))
        gmsh.option.setNumber("Geometry.CopyMeshingMethod", 1)
        gmsh.option.setNumber("Geometry.PointNumbers", 0)
        gmsh.option.setNumber("Geometry.LineNumbers", 0)
        gmsh.option.setNumber(
            "Mesh.CharacteristicLengthMin", min(mesh_size_S, mesh_size_R)
        )
        gmsh.option.setNumber(
            "Mesh.CharacteristicLengthMax", max(mesh_size_S, mesh_size_R)
        )
        model.add("Pyleecan")

        # build geometry
        alpha = 0
        rotor_list = []
        if machine.shaft is not None:
            rotor_list.extend(machine.shaft.build_geometry(sym=sym, alpha=alpha))
        rotor_surf = machine.rotor.build_geometry(sym=sym, alpha=alpha)
        if sym == 1 and machine.shaft is not None:
            # Remove Rotor internal radius (use shaft one)
            # first surface is a SurfRing (cf Lamination.build_geometry)
            rotor_surf[0] = rotor_surf[0].out_surf
        rotor_list.extend(rotor_surf)
        stator_list = []
        stator_list.extend(machine.stator.build_geometry(sym=sym, alpha=alpha))

        #####################
        # Adding Rotor
        #####################
        # set origin
        oo = factory.addPoint(0, 0, 0, 0, tag=-1)
        gmsh_dict = {
            0: {
                "tag": 0,
                "label": "origin",
                "with_holes": False,
                1: {
                    "tag": 0,
                    "label": None,
                    "n_elements": 1,
                    "bc_name": None,
                    "begin": {"tag": oo, "coord": complex(0.0, 0.0)},
                    "end": {"tag": None, "coord": None},
                    "cent": {"tag": None, "coord": None},
                    "arc_angle": None,
                    "line_angle": None,
                },
            }
        }

        nsurf = 0  # number of surfaces
        # Drawing Rotor and Shaft surfaces
        if not is_lam_only_S:
            for surf in rotor_list:
                nsurf += 1
                # print(surf.label)
                gmsh_dict.update(
                    {
                        nsurf: {
                            "tag": None,
                            "label": short_label(surf.label),
                        }
                    }
                )
                if LAM_LAB in decode_label(surf.label)["surf_type"]:
                    gmsh_dict[nsurf]["with_holes"] = True
                    lam_rotor_surf_id = nsurf
                else:
                    gmsh_dict[nsurf]["with_holes"] = False

                # comp. number of elements on the lines & override by user values in case
                mesh_dict = gmsh_pyleecan.comp_gmsh_mesh_dict(
                    surface=surf,
                    element_size=mesh_size_R,
                    user_mesh_dict=user_mesh_dict,
                )

                # Draw the surface
                gmsh_pyleecan.draw_surf_line(
                    surf,
                    mesh_dict,
                    boundary_prop,
                    model,
                    gmsh_dict,
                    nsurf,
                    mesh_size_R,
                )

            lam_and_holes = []
            ext_lam_loop = None
            rotor_cloops = []
            # loop though all (surface) entries of the rotor lamination
            for s_data in gmsh_dict.values():
                lloop = []
                # skip this surface dataset if it is the origin
                if s_data["label"] == "origin":
                    continue

                # build a lineloop of the surfaces lines
                for lvalues in s_data.values():
                    if type(lvalues) is not dict:
                        continue
                    lloop.extend([lvalues["tag"]])
                cloop = factory.addCurveLoop(lloop)

                label_dict = decode_label(s_data["label"])
                if (
                    MAG_LAB in label_dict["surf_type"]
                    or HOLEM_LAB_S in label_dict["surf_type"]
                    or BAR_LAB in label_dict["surf_type"]
                ):
                    # Surface of Hole Magnet
                    rotor_cloops.extend([cloop])

                # search for the holes to substract from rotor lam
                if LAM_LAB_S in label_dict["surf_type"]:
                    ext_lam_loop = cloop
                else:
                    # MachineSIPSM does not have holes in rotor lam
                    # only shaft is taken out if symmetry is one
                    if (
                        isinstance(machine, MachineSIPMSM)
                        or isinstance(machine, MachineSCIM)
                        or isinstance(machine, MachineWRSM)
                    ):
                        if sym == 1 and SHAFT_LAB in label_dict["surf_type"]:
                            lam_and_holes.extend([cloop])
                    else:
                        if sym == 1:
                            lam_and_holes.extend([cloop])
                        elif SHAFT_LAB not in label_dict["surf_type"]:
                            lam_and_holes.extend([cloop])
                        else:
                            pass

                    # Shaft, magnets and magnet pocket surfaces are created
                    if not is_lam_only_R:
                        s_data["tag"] = factory.addPlaneSurface([cloop], tag=-1)
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [s_data["tag"]])
                        model.setPhysicalName(2, pg, s_data["label"])

            # Finally rotor lamination is built
            if ext_lam_loop is not None:
                lam_and_holes.insert(0, ext_lam_loop)
            if len(lam_and_holes) > 0:
                gmsh_dict[lam_rotor_surf_id]["tag"] = factory.addPlaneSurface(
                    lam_and_holes, tag=-1
                )
            factory.synchronize()
            pg = model.addPhysicalGroup(2, [gmsh_dict[lam_rotor_surf_id]["tag"]])
            model.setPhysicalName(2, pg, gmsh_dict[lam_rotor_surf_id]["label"])
            # rotor_cloops = lam_and_holes

        # store rotor dict
        rotor_dict = gmsh_dict.copy()

        #####################
        # Adding Stator
        #####################
        # init new dict for stator
        gmsh_dict = {
            0: {
                "tag": 0,
                "label": "origin",
                "with_holes": False,
                1: {
                    "tag": 0,
                    "label": None,
                    "n_elements": 1,
                    "bc_name": None,
                    "begin": {"tag": oo, "coord": complex(0.0, 0.0)},
                    "end": {"tag": None, "coord": None},
                    "cent": {"tag": None, "coord": None},
                },
            }
        }

        # nsurf = 0
        if not is_lam_only_R:
            stator_cloops = []
            for surf in stator_list:
                nsurf += 1
                gmsh_dict.update(
                    {
                        nsurf: {
                            "tag": None,
                            "label": short_label(surf.label),
                        }
                    }
                )
                if LAM_LAB in decode_label(surf.label)["surf_type"]:
                    gmsh_dict[nsurf]["with_holes"] = True
                else:
                    gmsh_dict[nsurf]["with_holes"] = False

                # comp. number of elements on the lines & override by user values in case
                mesh_dict = gmsh_pyleecan.comp_gmsh_mesh_dict(
                    surface=surf,
                    element_size=mesh_size_S,
                    user_mesh_dict=user_mesh_dict,
                )

                # Draw the surface
                gmsh_pyleecan.draw_surf_line(
                    surf,
                    mesh_dict,
                    boundary_prop,
                    model,
                    gmsh_dict,
                    nsurf,
                    mesh_size_S,
                )

            for s_data in gmsh_dict.values():
                lloop = []
                # skip this surface dataset if it is the origin
                if s_data["label"] == "origin":
                    continue

                if sym == 1:
                    inner_loop = []
                    # build a lineloop of the surfaces lines independently for yoke
                    # and bore is considered a hole
                    for lvalues in s_data.values():
                        if type(lvalues) is not dict:
                            continue

                        if WIND_LAB_S in s_data["label"]:
                            lloop.extend([lvalues["tag"]])
                            inner_loop.extend([lvalues["tag"]])
                        elif (
                            lvalues["label"] is not None
                            and LAM_LAB in lvalues["label"]
                            and YOKE_LAB in lvalues["label"]
                        ):
                            lloop.extend([lvalues["tag"]])
                        else:
                            inner_loop.extend([lvalues["tag"]])
                    # print(s_data["label"],lloop,inner_loop)
                    cloop = factory.addCurveLoop(lloop)
                    # stator_cloops.append(cloop)

                    if LAM_LAB_S in decode_label(s_data["label"])["surf_type"] or (
                        not is_lam_only_S
                    ):
                        # Winding surfaces are created
                        if WIND_LAB_S in s_data["label"]:
                            s_data["tag"] = factory.addPlaneSurface([cloop], tag=-1)
                            factory.synchronize()
                            pg = model.addPhysicalGroup(2, [s_data["tag"]])
                            model.setPhysicalName(2, pg, s_data["label"])
                        # Lamination surfaces are created
                        else:
                            inner_cloop = factory.addCurveLoop(inner_loop)
                            s_data["tag"] = factory.addPlaneSurface(
                                [cloop, inner_cloop], tag=-1
                            )
                            factory.synchronize()
                            pg = model.addPhysicalGroup(2, [s_data["tag"]])
                            model.setPhysicalName(2, pg, s_data["label"])
                else:
                    for lvalues in s_data.values():
                        if type(lvalues) is not dict:
                            continue
                        lloop.extend([lvalues["tag"]])
                    cloop = factory.addCurveLoop(lloop)
                    # stator_cloops.append(cloop)

                    # All surfaces are created
                    if LAM_LAB_S in decode_label(s_data["label"])["surf_type"] or (
                        not is_lam_only_S
                    ):
                        s_data["tag"] = factory.addPlaneSurface([cloop], tag=-1)
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [s_data["tag"]])
                        model.setPhysicalName(2, pg, s_data["label"])

        stator_dict = gmsh_dict.copy()
        gmsh_dict.update(rotor_dict)

        #####################
        # Adding Sliding Band
        #####################
        if is_sliding_band and (not is_lam_only_R) and (not is_lam_only_S):
            sb_list = gmsh_pyleecan.get_sliding_band(sym=sym, machine=machine)
        else:
            sb_list = []

        # nsurf = 0
        for surf in sb_list:
            nsurf += 1
            gmsh_dict.update(
                {
                    nsurf: {
                        "tag": None,
                        "label": short_label(surf.label),
                    }
                }
            )
            # comp. number of elements on the lines & override by user values in case
            mesh_dict = gmsh_pyleecan.comp_gmsh_mesh_dict(
                surface=surf, element_size=mesh_size_SB, user_mesh_dict=user_mesh_dict
            )

            # Draw the surface
            gmsh_pyleecan.draw_surf_line(
                surf,
                mesh_dict,
                boundary_prop,
                model,
                gmsh_dict,
                nsurf,
                mesh_size_SB,
            )

        if is_sliding_band and (not is_lam_only_R) and (not is_lam_only_S):
            if sym == 1:
                lloop1 = []
                lloop2 = []
                lloop3 = []
                lloop4 = []
                lloop5 = []
                for s_data in gmsh_dict.values():
                    label_dict = decode_label(s_data["label"])

                    # skip this surface dataset if it is the origin
                    if s_data["label"] == "origin" or not (
                        AIRGAP_LAB in label_dict["surf_type"]
                        or SLID_LAB in label_dict["surf_type"]
                    ):
                        continue

                    # build a lineloop of the surfaces lines
                    for lvalues in s_data.values():
                        if type(lvalues) is not dict:
                            continue

                        if (
                            AIRGAP_LAB in label_dict["surf_type"]
                            and BOT_LAB in label_dict["surf_type"]
                            and AR_B_LAB in lvalues["label"]
                        ):
                            lloop1.extend([lvalues["tag"]])
                        elif (
                            SLID_LAB in label_dict["surf_type"]
                            and BOT_LAB in label_dict["surf_type"]
                            and SBR_B_LAB in lvalues["label"]
                        ):
                            lloop2.extend([lvalues["tag"]])
                        elif (
                            SLID_LAB in label_dict["surf_type"]
                            and TOP_LAB in label_dict["surf_type"]
                            and SBR_T_LAB in lvalues["label"]
                        ):
                            lloop3.extend([lvalues["tag"]])
                        elif (
                            AIRGAP_LAB in label_dict["surf_type"]
                            and TOP_LAB in label_dict["surf_type"]
                            and AR_T_LAB in lvalues["label"]
                        ):
                            lloop4.extend([lvalues["tag"]])
                        elif (
                            AIRGAP_LAB in label_dict["surf_type"]
                            and TOP_LAB in label_dict["surf_type"]
                            and AIRBOX_R_LAB in lvalues["label"]
                        ):
                            lloop5.extend([lvalues["tag"]])
                        else:
                            pass

                cloop1 = factory.addCurveLoop(lloop1)
                cloop2 = factory.addCurveLoop(lloop2)
                cloop3 = factory.addCurveLoop(lloop3)
                cloop4 = factory.addCurveLoop(lloop4)
                cloop5 = factory.addCurveLoop(lloop5)

                for s_data in gmsh_dict.values():
                    label_dict = decode_label(s_data["label"])

                    # skip this surface dataset if it is the origin
                    if s_data["label"] == "origin" or not (
                        AIRGAP_LAB in label_dict["surf_type"]
                        or SLID_LAB in label_dict["surf_type"]
                    ):
                        continue

                    if (
                        AIRGAP_LAB in label_dict["surf_type"]
                        and BOT_LAB in label_dict["surf_type"]
                    ):
                        s_data["tag"] = factory.addPlaneSurface([cloop1], tag=-1)
                        factory.synchronize()
                        rotor_ag_before = (2, s_data["tag"])
                    elif (
                        SLID_LAB in label_dict["surf_type"]
                        and BOT_LAB in label_dict["surf_type"]
                    ):
                        s_data["tag"] = factory.addPlaneSurface(
                            [cloop2, cloop1], tag=-1
                        )
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [s_data["tag"]])
                        model.setPhysicalName(2, pg, s_data["label"])
                    elif (
                        SLID_LAB in label_dict["surf_type"]
                        and TOP_LAB in label_dict["surf_type"]
                    ):
                        s_data["tag"] = factory.addPlaneSurface(
                            [cloop4, cloop3], tag=-1
                        )
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [s_data["tag"]])
                        model.setPhysicalName(2, pg, s_data["label"])
                    elif (
                        AIRGAP_LAB in label_dict["surf_type"]
                        and TOP_LAB in label_dict["surf_type"]
                    ):
                        s_data["tag"] = factory.addPlaneSurface(
                            [cloop5, cloop4], tag=-1
                        )
                        # s_data["tag"] = factory.addPlaneSurface([cloop5], tag=-1)
                        factory.synchronize()
                        stator_ag_before = (2, s_data["tag"])
                    else:
                        continue

                if is_sliding_band and (not is_lam_only_R) and (not is_lam_only_S):
                    rotor_surf_gmsh_list = []
                    for tid in rotor_dict:
                        # Discard Origin
                        if tid == 0:
                            continue
                        rotor_surf_gmsh_list.append((2, tid))

                    stator_surf_gmsh_list = []
                    for tid in stator_dict:
                        # Discard Origin
                        if tid == 0:
                            continue
                        stator_surf_gmsh_list.append((2, tid))

                    cut1 = model.occ.cut(
                        [rotor_ag_before],
                        rotor_surf_gmsh_list,
                        removeObject=True,
                        removeTool=False,
                    )

                    # All These because CUT alone is not working for the stator
                    stat_copy = model.occ.copy(stator_surf_gmsh_list)
                    ints1 = model.occ.intersect(
                        [stator_ag_before],
                        [stat_copy[0]],
                        removeObject=True,
                        removeTool=True,
                        tag=-1,
                    )
                    stat_copy.pop(0)
                    cut2 = model.occ.cut(
                        ints1[0], stat_copy, removeObject=True, removeTool=True, tag=-1
                    )

                    if len(cut1[0]) > 1:
                        # Remove extra surfaces
                        model.occ.remove([cut1[0][1]])
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [cut1[0][0][1]])
                        model.setPhysicalName(
                            2, pg, lab_int + "_" + AIRGAP_LAB + BOT_LAB
                        )
                    else:
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [cut1[0][0][1]])
                        model.setPhysicalName(
                            2, pg, lab_int + "_" + AIRGAP_LAB + BOT_LAB
                        )

                    if len(cut2[0]) > 1:
                        # Remove extra surfaces
                        model.occ.remove([cut2[0][0]])
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [cut2[0][1][1]])
                        model.setPhysicalName(
                            2, pg, lab_ext + "_" + AIRGAP_LAB + TOP_LAB
                        )
                    else:
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [cut2[0][0][1]])
                        model.setPhysicalName(
                            2, pg, lab_ext + "_" + AIRGAP_LAB + TOP_LAB
                        )

            else:
                for s_key, s_data in gmsh_dict.items():
                    lloop = []
                    label_dict = decode_label(s_data["label"])

                    # skip this surface dataset if it is the origin
                    if s_data["label"] == "origin" or not (
                        AIRGAP_LAB in label_dict["surf_type"]
                        or SLID_LAB in label_dict["surf_type"]
                    ):
                        continue

                    # build a lineloop of the surfaces lines
                    for lvalues in s_data.values():
                        if type(lvalues) is not dict:
                            continue
                        lloop.extend([lvalues["tag"]])

                    if lloop:
                        cloop = factory.addCurveLoop(lloop)
                        if (
                            AIRGAP_LAB in label_dict["surf_type"]
                            and BOT_LAB in label_dict["surf_type"]
                            and isinstance(machine, MachineSIPMSM)
                        ):
                            s_data["tag"] = factory.addPlaneSurface(
                                [cloop] + rotor_cloops, tag=-1
                            )
                        else:
                            s_data["tag"] = factory.addPlaneSurface([cloop], tag=-1)
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [s_data["tag"]])
                        model.setPhysicalName(2, pg, s_data["label"])
                        if AIRGAP_LAB in s_data["label"] and BOT_LAB in s_data["label"]:
                            rotor_ag_before = (2, s_data["tag"])
                            rotor_ag_key_before = s_key
                        if AIRGAP_LAB in s_data["label"] and TOP_LAB in s_data["label"]:
                            stator_ag_before = (2, s_data["tag"])
                            stator_ag_key_before = s_key

                if is_sliding_band and (not is_lam_only_R) and (not is_lam_only_S):
                    rotor_surf_gmsh_list = []
                    for tid in rotor_dict:
                        # Discard Origin
                        if tid == 0:
                            continue
                        rotor_surf_gmsh_list.append((2, tid))

                    stator_surf_gmsh_list = []
                    for tid in stator_dict:
                        # Discard Origin
                        if tid == 0:
                            continue
                        stator_surf_gmsh_list.append((2, tid))

                    cut1 = model.occ.cut(
                        [rotor_ag_before],
                        rotor_surf_gmsh_list,
                        removeObject=True,
                        removeTool=False,
                    )
                    cut2 = model.occ.cut(
                        [stator_ag_before],
                        stator_surf_gmsh_list,
                        removeObject=True,
                        removeTool=False,
                    )

                    if len(cut1[0]) > 1:
                        # Remove extra surfaces
                        model.occ.remove([cut1[0][0]])
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [cut1[0][1][1]])
                        model.setPhysicalName(
                            2, pg, lab_int + "_" + AIRGAP_LAB + BOT_LAB
                        )
                    else:
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [cut1[0][0][1]])
                        model.setPhysicalName(
                            2, pg, lab_int + "_" + AIRGAP_LAB + BOT_LAB
                        )

                    # Look at the lines in the resulting surface, then update the dictionary
                    # with MASTER/SLAVE BC when line angles match symmetry angles
                    # MASTER is x-axis and SLAVE is 2Pi/sym
                    rotor_ag_after = model.getEntitiesForPhysicalGroup(2, pg)
                    rotor_ag_new_lines = model.getBoundary(
                        [(2, tag) for tag in rotor_ag_after]
                    )
                    nline = 0
                    for type_entity_l, rotor_ag_line in rotor_ag_new_lines:
                        rotor_ag_new_points = model.getBoundary(
                            [(type_entity_l, abs(rotor_ag_line))]
                        )
                        btag = rotor_ag_new_points[0][1]
                        etag = rotor_ag_new_points[1][1]
                        bxy = model.getValue(0, btag, [])
                        exy = model.getValue(0, etag, [])
                        exy_angle = cmath.phase(complex(exy[0], exy[1]))
                        bxy_angle = cmath.phase(complex(bxy[0], bxy[1]))
                        if exy_angle == bxy_angle and abs(exy_angle) < 1e-6:
                            b_name = boundary_prop[AS_BR_LAB]
                            l_name = AS_BR_LAB
                        elif (exy_angle == bxy_angle) and (
                            abs(abs(exy_angle) - 2.0 * np.pi / sym) < 1e-6
                        ):
                            b_name = boundary_prop[AS_BL_LAB]
                            l_name = AS_BL_LAB
                        else:
                            b_name = None
                            l_name = None
                        gmsh_dict[rotor_ag_before[1]].update(
                            {
                                "tag": rotor_ag_after[0],
                                "label": lab_int + "_" + AIRGAP_LAB + BOT_LAB,
                                nline: {
                                    "tag": abs(rotor_ag_line),
                                    "label": l_name,
                                    "n_elements": None,
                                    "bc_name": b_name,
                                    "begin": {
                                        "tag": btag,
                                        "coord": complex(bxy[0], bxy[1]),
                                    },
                                    "end": {
                                        "tag": etag,
                                        "coord": complex(exy[0], exy[1]),
                                    },
                                    "arc_angle": None,
                                    "line_angle": None,
                                },
                            }
                        )
                        nline = nline + 1

                    if len(cut2[0]) > 1:
                        # Remove extra surfaces
                        model.occ.remove([cut2[0][0]])
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [cut2[0][1][1]])
                        model.setPhysicalName(
                            2, pg, lab_ext + "_" + AIRGAP_LAB + TOP_LAB
                        )
                    else:
                        factory.synchronize()
                        pg = model.addPhysicalGroup(2, [cut2[0][0][1]])
                        model.setPhysicalName(
                            2, pg, lab_ext + "_" + AIRGAP_LAB + TOP_LAB
                        )

                    # Look at the lines in the resulting surface, then update the dictionary
                    # with MASTER/SLAVE BC when line angles match symmetry angles
                    # MASTER is x-axis and SLAVE is 2Pi/sym
                    stator_ag_after = model.getEntitiesForPhysicalGroup(2, pg)
                    stator_ag_new_lines = model.getBoundary(
                        [(2, tag) for tag in stator_ag_after]
                    )
                    nline = 0
                    for type_entity_l, stator_ag_line in stator_ag_new_lines:
                        stator_ag_new_points = model.getBoundary(
                            [(type_entity_l, abs(stator_ag_line))]
                        )
                        btag = stator_ag_new_points[0][1]
                        etag = stator_ag_new_points[1][1]
                        bxy = model.getValue(0, btag, [])
                        exy = model.getValue(0, etag, [])
                        exy_angle = cmath.phase(complex(exy[0], exy[1]))
                        bxy_angle = cmath.phase(complex(bxy[0], bxy[1]))
                        if exy_angle == bxy_angle and abs(exy_angle) < 1e-6:
                            b_name = boundary_prop[AS_TR_LAB]
                            l_name = AS_TR_LAB
                        elif (exy_angle == bxy_angle) and (
                            abs(abs(exy_angle) - 2.0 * np.pi / sym) < 1e-6
                        ):
                            b_name = boundary_prop[AS_TL_LAB]
                            l_name = AS_TL_LAB
                        else:
                            b_name = None
                            l_name = None
                        gmsh_dict[stator_ag_before[1]].update(
                            {
                                "tag": stator_ag_after[0],
                                "label": lab_ext + "_" + AIRGAP_LAB + TOP_LAB,
                                nline: {
                                    "tag": abs(stator_ag_line),
                                    "label": l_name,
                                    "n_elements": None,
                                    "bc_name": b_name,
                                    "begin": {
                                        "tag": btag,
                                        "coord": complex(bxy[0], bxy[1]),
                                    },
                                    "end": {
                                        "tag": etag,
                                        "coord": complex(exy[0], exy[1]),
                                    },
                                    "arc_angle": None,
                                    "line_angle": None,
                                },
                            }
                        )
                        nline = nline + 1

        ###################
        # Adding Airbox
        ###################
        if is_airbox and (not is_lam_only_R) and (not is_lam_only_S):
            ab_list = gmsh_pyleecan.get_air_box(sym=sym, machine=machine)
        else:
            ab_list = []

        # Default airbox mesh element size
        for surf in ab_list:
            nsurf += 1
            gmsh_dict.update(
                {
                    nsurf: {
                        "tag": None,
                        "label": short_label(surf.label),
                    }
                }
            )

            # comp. number of elements on the lines & override by user values in case
            mesh_dict = gmsh_pyleecan.comp_gmsh_mesh_dict(
                surface=surf, element_size=mesh_size_AB, user_mesh_dict=user_mesh_dict
            )

            # Draw the surface
            gmsh_pyleecan.draw_surf_line(
                surf,
                mesh_dict,
                boundary_prop,
                model,
                gmsh_dict,
                nsurf,
                mesh_size_AB,
            )

        for s_id, s_data in gmsh_dict.items():
            lloop = []
            if s_id == 0:
                continue
            for lvalues in s_data.values():
                if AIRBOX_LAB in decode_label(s_data["label"])["surf_type"]:
                    if type(lvalues) is not dict:
                        continue
                    lloop.extend([lvalues["tag"]])
                else:
                    continue
            if lloop:
                cloop = factory.addCurveLoop(lloop)
                s_data["tag"] = factory.addPlaneSurface([cloop], tag=-1)
                factory.synchronize()
                pg = model.addPhysicalGroup(2, [s_data["tag"]])
                model.setPhysicalName(2, pg, s_data["label"])

        # Set boundary conditions in gmsh lines
        boundary_list = list(set(boundary_prop.values()))
        for propname in boundary_list:
            bc_id = []
            for s_data in gmsh_dict.values():
                for lvalues in s_data.values():
                    if type(lvalues) is not dict:
                        continue
                    if lvalues["bc_name"] == propname:
                        bc_id.extend([abs(lvalues["tag"])])
            if bc_id:
                factory.synchronize()
                pg = model.addPhysicalGroup(1, bc_id)
                model.setPhysicalName(1, pg, propname)

        # Set all line labels as physical groups
        if is_set_labels:
            groups = {}
            for s_data in gmsh_dict.values():
                for lvalues in s_data.values():
                    if (
                        type(lvalues) is not dict
                        or "label" not in lvalues
                        or not lvalues["label"]
                    ):
                        continue

                    if lvalues["label"] not in groups.keys():
                        groups[lvalues["label"]] = []
                    groups[lvalues["label"]].append(abs(lvalues["tag"]))

            for label, tags in groups.items():
                factory.synchronize()
                pg = model.addPhysicalGroup(1, tags)
                model.setPhysicalName(1, pg, label)

        # save mesh or geo file depending on file extension
        filename, file_extension = os.path.splitext(path_save)

        if file_extension == ".geo":
            gmsh.write(filename + ".geo_unrolled")
            os.replace(filename + ".geo_unrolled", filename + file_extension)
        else:
            gmsh.model.mesh.generate(2)
            gmsh.write(path_save)

        if is_run:
            gmsh.fltk.run()  # Uncomment to launch Gmsh GUI
        gmsh.finalize()
        return gmsh_dict

    @staticmethod
    def draw_surf_line(
        surf: Surface,
        mesh_dict: dict,
        boundary_prop: dict,
        model: Any,
        gmsh_dict: dict,
        nsurf: int,
        mesh_size: float,
    ) -> None:
        """Draw the lines of a surface and handles the Arc>180deg

        Parameters
        ----------
        surf : Surface
            Surface object to draw
        mesh_dict : dict
            Dictionary to enforce the mesh (key: line id, value:nb element)
        boundary_prop : dict
            Dictionary to set the Boundary conditions
        model : Object
            Gmsh model
        gmsh_dict: dict
            dictionary containing the main parameters of GMSH File
        nsurf : int
            Index of the surface to draw
        mesh_size: float
            Default mesh element size

        Returns
        -------
        None
        """
        for ii, line in enumerate(surf.get_lines()):
            n_elem = None if not mesh_dict else mesh_dict[str(ii)]
            n_elem = n_elem if n_elem is not None else 0
            bc_name = gmsh_pyleecan.get_boundary_condition(line, boundary_prop)
            # Gmsh built-in engine does not allow arcs larger than 180deg
            # so arcs are split into two
            if isinstance(line, Arc) and abs(line.get_angle() * 180.0 / np.pi) >= 180.0:
                rot_dir = 1 if line.is_trigo_direction == True else -1
                arc1 = Arc1(
                    begin=line.get_begin(),
                    end=line.get_middle(),
                    radius=rot_dir * line.comp_radius(),
                    prop_dict=line.prop_dict,
                    is_trigo_direction=line.is_trigo_direction,
                )
                arc2 = Arc1(
                    begin=line.get_middle(),
                    end=line.get_end(),
                    radius=rot_dir * line.comp_radius(),
                    prop_dict=line.prop_dict,
                    is_trigo_direction=line.is_trigo_direction,
                )
                for arc in [arc1, arc2]:
                    gmsh_pyleecan._add_agline_to_dict(
                        gmodel=model,
                        line=arc,
                        d=gmsh_dict,
                        idx=nsurf,
                        mesh_size=mesh_size,
                        n_elements=n_elem,
                        bc=bc_name,
                    )
            elif isinstance(line, Arc) and (
                abs(line.get_angle() * 180.0 / np.pi) <= tol
            ):
                # Don't draw anything, this is a circle and usually is repeated ?
                pass
            else:
                gmsh_pyleecan._add_agline_to_dict(
                    gmodel=model,
                    line=line,
                    d=gmsh_dict,
                    idx=nsurf,
                    mesh_size=mesh_size,
                    n_elements=n_elem,
                    bc=bc_name,
                )

    @staticmethod
    def _add_agline_to_dict(
        gmodel: Any,
        line: Line,
        d: dict = {},
        idx: int = 0,
        mesh_size: float = 0.01,
        n_elements: int = 0,
        bc: str | None = None,
    ) -> None:
        """Draw a new Air Gap line and add it to GMSH dictionary if it does not exist

        Parameters
        ----------
        gmodel : Object
            GMSH Model object
        line : Object
            Line Object
        d : Dictionary
            GMSH dictionary
        idx : int
            Surface index it belongs to
        mesh_size : float
            Points mesh size
        n_elements : int
            Number of elements on the line for meshing control
        bc : String
            Boundary condition name

        Returns
        -------
        None
        """

        # TO-DO: Allow repeated points for the rotor and stator sliding bands
        dlines = []
        ltag = None
        btag, bx, by = gmsh_pyleecan._find_point_tag(d, line.get_begin())
        etag, ex, ey = gmsh_pyleecan._find_point_tag(d, line.get_end())
        if btag is None:
            btag = gmodel.occ.addPoint(bx, by, 0, meshSize=mesh_size, tag=-1)
        else:
            dlines.extend(gmsh_pyleecan._find_lines_from_point(d, btag))
        if etag is None:
            etag = gmodel.occ.addPoint(ex, ey, 0, meshSize=mesh_size, tag=-1)
        else:
            dlines.extend(gmsh_pyleecan._find_lines_from_point(d, etag))

        if line.prop_dict and BOUNDARY_PROP_LAB in line.prop_dict:
            line_label = line.prop_dict[BOUNDARY_PROP_LAB]
        else:
            line_label = None
        if isinstance(line, Arc):
            ctag, cx, cy = gmsh_pyleecan._find_point_tag(d, line.get_center())
            if ctag is None:
                ctag = gmodel.occ.addPoint(cx, cy, 0, meshSize=mesh_size, tag=-1)
            else:
                dlines.extend(gmsh_pyleecan._find_lines_from_point(d, ctag))
            if len(dlines) > 0:
                for iline in dlines:
                    p = gmsh_pyleecan._find_points_from_line(d, iline)
                    if p[0] == btag and p[1] == etag and p[2] == ctag:
                        ltag = iline
                        break
                    elif p[0] == etag and p[1] == btag and p[2] == ctag:
                        ltag = -iline
                        break
                    else:
                        pass
                if ltag is None:
                    ltag = gmodel.occ.addCircleArc(btag, ctag, etag, tag=-1)
                    if n_elements > 0:
                        gmodel.occ.synchronize()
                        gmodel.mesh.setTransfiniteCurve(
                            ltag, n_elements + 1, "Progression"
                        )
            else:
                ltag = gmodel.occ.addCircleArc(btag, ctag, etag, tag=-1)
                if n_elements > 0:
                    gmodel.occ.synchronize()
                    gmodel.mesh.setTransfiniteCurve(ltag, n_elements + 1, "Progression")

            # To avoid fill the dictionary with repeated lines
            repeated = False
            for lvalues in d[idx].values():
                if type(lvalues) is not dict:
                    continue
                else:
                    if lvalues["tag"] == ltag:
                        repeated = True

            if not repeated:
                nline = len(d[idx]) - 2
                arc_angle = cmath.phase(complex(ex, ey)) - cmath.phase(complex(bx, by))
                d[idx].update(
                    {
                        nline: {
                            "tag": ltag,
                            "label": line_label,
                            "n_elements": n_elements,
                            "bc_name": bc,
                            "begin": {"tag": btag, "coord": complex(bx, by)},
                            "end": {"tag": etag, "coord": complex(ex, ey)},
                            "cent": {"tag": ctag, "coord": complex(cx, cy)},
                            "arc_angle": arc_angle,
                            "line_angle": None,
                        }
                    }
                )

        else:
            if len(dlines) > 0:
                for iline in dlines:
                    p = gmsh_pyleecan._find_points_from_line(d, iline)
                    if p[0] == btag and p[1] == etag:
                        ltag = iline
                        break
                    elif p[0] == etag and p[1] == btag:
                        ltag = -iline
                        break
                    else:
                        pass
                if ltag is None:
                    ltag = gmodel.occ.addLine(btag, etag, tag=-1)
                    if n_elements > 0:
                        gmodel.occ.synchronize()
                        gmodel.mesh.setTransfiniteCurve(
                            ltag, n_elements + 1, "Progression"
                        )
            else:
                ltag = gmodel.occ.addLine(btag, etag, tag=-1)
                if n_elements > 0:
                    gmodel.occ.synchronize()
                    gmodel.mesh.setTransfiniteCurve(ltag, n_elements + 1, "Progression")

            # To avoid fill the dictionary with repeated lines
            repeated = False
            for lvalues in d[idx].values():
                if type(lvalues) is not dict:
                    continue
                else:
                    if lvalues["tag"] == ltag:
                        repeated = True

            if not repeated:
                nline = len(d[idx]) - 2
                line_angle = 0.5 * (
                    cmath.phase(complex(ex, ey)) + cmath.phase(complex(bx, by))
                )
                d[idx].update(
                    {
                        nline: {
                            "tag": ltag,
                            "label": line_label,
                            "n_elements": n_elements,
                            "bc_name": bc,
                            "begin": {"tag": btag, "coord": complex(bx, by)},
                            "end": {"tag": etag, "coord": complex(ex, ey)},
                            "arc_angle": None,
                            "line_angle": line_angle,
                        }
                    }
                )

        return None

    @staticmethod
    def _find_lines_from_point(d: dict = {}, ptag: int = -1) -> int:
        """Find lines that have the given point tag

        Parameters
        ----------
        d : Dictionary
            GMSH dictionary
        ptag : int
            point tag

        Returns
        -------
        ltag : int
            List of line tags
        """
        lines = []
        for s_data in d.values():
            for lvalues in s_data.values():
                if type(lvalues) is not dict:
                    continue
                for pvalues in lvalues.values():
                    if type(pvalues) is not dict:
                        continue
                    if pvalues["tag"] == ptag:
                        lines.append(lvalues["tag"])
        return lines

    @staticmethod
    def _find_point_tag(
        d: dict = {}, p: complex = complex(0.0, 0.0)
    ) -> tuple[int, float, float]:
        """Find a point in the GMSH dictionary

        Parameters
        ----------
        d : Dictionary
            GMSH dictionary
        p : Complex
            Point coordinates

        Returns
        -------
        tag : int
            Existing tag number or new one if it does not exist
        real : float
            Real coordinates of point
        imag : float
            Imaginary coordinates of point
        """
        tol = 1e-6
        for s_data in d.values():
            for lvalues in s_data.values():
                if type(lvalues) is not dict:
                    continue
                for pvalues in lvalues.values():
                    if type(pvalues) is not dict:
                        continue
                    if pvalues["tag"] is not None:
                        b = pvalues["coord"]
                        if abs(p.real - b.real) < tol and abs(p.imag - b.imag) < tol:
                            return pvalues["tag"], b.real, b.imag
        return None, p.real, p.imag

    @staticmethod
    def _find_points_from_line(d: dict = {}, ltag: int = -1) -> float:
        """Find points tag from existing lines

        Parameters
        ----------
        d : Dictionary
            GMSH dictionary
        ltag : int
            line tag

        Returns
        -------
        coord : float
            Coordinates of point if found
        """
        btag = None
        etag = None
        ctag = None
        for s_data in d.values():
            for lvalues in s_data.values():
                if type(lvalues) is not dict:
                    continue
                if lvalues["tag"] != ltag:
                    continue
                else:
                    for pid, pvalues in lvalues.items():
                        if type(pvalues) is not dict:
                            continue
                        if pid == "begin":
                            btag = pvalues["tag"]
                        elif pid == "end":
                            etag = pvalues["tag"]
                        elif pid == "cent":
                            ctag = pvalues["tag"]
                    break
        return [btag, etag, ctag]

    @staticmethod
    def gen_3D_mesh(
        lamination: LamSlot,
        save_path: str = "Lamination.msh",
        sym: int = -1,
        mesh_size: float = 0.005,
        user_mesh_dict: dict | None = None,
        is_rect: bool = False,
        Nlayer: int = 20,
        display: bool = True,
    ) -> None:
        """Draw 3D mesh of the lamination
        Parameters
        ----------
        lamination: LamSlot
            Lamintation with slot to draw
        save_path: str
            Path to save the msh result file
        sym : int
            Number of symmetry to apply
        mesh_size : float
            Size of the mesh [m]
        user_mesh_dict : dict
            To enforce the number of elements on the lines
        is_rect : bool
            To use rectangular elements
        Nlayer : int
            Number of mesh layer on Z axis
        display : bool
            To display gmsh logs
        Returns
        -------
        None
        """
        # The defaut symmetry is Zs => We draw only one tooth
        if sym == -1:
            tooth_surf = lamination.slot.get_surface_tooth()
            Zs = lamination.get_Zs()
        else:
            tooth_surf = lamination.build_geometry(sym=sym)[0]
            Zs = sym

        # For readibility
        model = gmsh.model
        factory = model.geo
        L = lamination.L1  # Lamination length

        # Start a new model
        gmsh.initialize()

        gmsh.option.setNumber("General.Terminal", int(display))

        gmsh.option.setNumber("Geometry.CopyMeshingMethod", 1)
        model.add("Pyleecan")

        # Create all the points of the tooth
        NPoint = 0  # Number of point created
        for line in tooth_surf.get_lines():
            Z = line.get_begin()
            NPoint += 1
            factory.addPoint(Z.real, Z.imag, -L / 2, mesh_size, NPoint)

        # Draw all the lines of the tooth
        NLine = 0  # Number of line created
        for line in tooth_surf.get_lines():
            NLine += 1
            if NLine == len(tooth_surf.get_lines()):
                if isinstance(line, Arc):
                    Zc = line.get_center()
                    NPoint += 1
                    factory.addPoint(Zc.real, Zc.imag, -L / 2, mesh_size, NPoint)
                    factory.addCircleArc(NLine, NPoint - 1, 1, NLine)
                else:
                    factory.addLine(NLine, 1, NLine)
            else:
                if isinstance(line, Arc):
                    Zc = line.get_center()
                    NPoint += 1
                    factory.addPoint(Zc.real, Zc.imag, -L / 2, mesh_size, NPoint)
                    factory.addCircleArc(NLine, NPoint, NLine + 1, NLine)
                else:
                    factory.addLine(NLine, NLine + 1, NLine)

        # Create the Tooth surface
        gmsh.model.geo.addCurveLoop(list(range(1, NLine + 1)), 1)
        gmsh.model.geo.addPlaneSurface([1], 1)
        gmsh.model.addPhysicalGroup(2, [1], 1)
        gmsh.model.setPhysicalName(2, 1, "Tooth")

        # convert triangle mesh to rectangle mesh
        if is_rect:
            factory.mesh.setRecombine(2, 1)

        # Change the mesh size for each line
        if user_mesh_dict is not None:
            # Compute basic mesh_dict
            mesh_dict = tooth_surf.comp_mesh_dict(element_size=mesh_size)
            # Overwrite basic mesh dict with user one
            mesh_dict.update(user_mesh_dict)
            # Apply the number of element on each line of the surface
            for ii, line in enumerate(tooth_surf.get_lines()):
                factory.mesh.setTransfiniteCurve(
                    ii + 1, mesh_dict[str(ii)] + 1, "Progression"
                )

        # Copy/Rotate all the tooth to get the 2D lamination
        surf_list = [1]
        for ii in range(Zs):
            ov = factory.copy([(2, 1)])
            factory.rotate(ov, 0, 0, -L / 2, 0, 0, 1, (ii + 1) * 2 * np.pi / Zs)
            surf_list.append(ov[0][1])
        gmsh.model.addPhysicalGroup(2, surf_list, 2)
        gmsh.model.setPhysicalName(2, 2, "Lamination")

        # Extrude the lamination
        for surf in surf_list:
            if is_rect == True:
                ov = factory.extrude(
                    [(2, surf)], 0, 0, L, numElements=[Nlayer], recombine=True
                )
            else:
                ov = factory.extrude(
                    [(2, surf)], 0, 0, L, numElements=[Nlayer], recombine=False
                )
        model.addPhysicalGroup(3, list(range(1, Zs + 1)), 1)
        if lamination.is_stator:
            model.setPhysicalName(3, 1, "stator")
        else:
            model.setPhysicalName(3, 1, "rotor")

        # Generate the 3D mesh
        factory.synchronize()

        filename, file_extension = os.path.splitext(save_path)
        if file_extension == ".geo":
            gmsh.write(filename + ".geo_unrolled")
            os.replace(filename + ".geo_unrolled", filename + file_extension)
        else:
            gmsh.model.mesh.generate(3)
            gmsh.write(save_path)

        # Save and close

        gmsh.finalize()

    @staticmethod
    def get_air_box(sym: int, machine: float) -> list:
        """Returns  an outer surface surrounding the external lamination

        Parameters
        ----------
        sym: int
            Symmetry factor (1= full machine, 2= half of the machine...)
        machine: float
            to extract laminations

        Returns
        -------
        surf_list: list
            Outer surface (Air Box)
        """
        lam_list = machine.get_lam_list()
        lam_int = lam_list[0]
        lam_ext = lam_list[1]

        R_ext = lam_ext.get_Ryoke()
        R_ab = 1.5 * R_ext  # Default at 1.5 times external lam radius

        surf_list = []
        if sym == 1:  # Complete machine
            # TO-DO: Airbox Full Machine no implemented yet.

            surf_list.append(
                Circle(
                    center=0,
                    radius=R_ab,
                    label=NO_LAM_LAB + "_" + AIRBOX_LAB,
                    point_ref=(R_ab / 2) * np.exp(1j * np.pi / 2),
                    prop_dict={BOUNDARY_PROP_LAB: AIRBOX_R_LAB},
                )
            )
        else:  # Symmetry
            # Internal AirGap
            Z1 = R_ext
            Z0 = Z1 * np.exp(1j * 2 * np.pi / sym)
            Z2 = R_ab
            Z3 = Z2 * np.exp(1j * 2 * np.pi / sym)
            airbox_lines: list[Line] = []
            airbox_lines.append(
                Segment(begin=Z1, end=Z2, prop_dict={BOUNDARY_PROP_LAB: AIRBOX_SR_LAB})
            )
            airbox_lines.append(
                Arc1(
                    begin=Z2,
                    end=Z3,
                    radius=R_ab,
                    prop_dict={BOUNDARY_PROP_LAB: AIRBOX_R_LAB},
                    is_trigo_direction=True,
                )
            )
            airbox_lines.append(
                Segment(begin=Z3, end=Z0, prop_dict={BOUNDARY_PROP_LAB: AIRBOX_SL_LAB})
            )
            # airbox_lines.append(Arc2(begin=Z0, center=0.0, angle=-2 * pi / sym))
            airbox_lines.append(
                Arc1(
                    begin=Z0,
                    end=Z1,
                    radius=-R_ext,
                    is_trigo_direction=False,
                )
            )
            surf_list.append(
                SurfLine(
                    line_list=airbox_lines,
                    # point_ref=0.0 * Z2 * exp(1j * pi / sym),
                    label=NO_LAM_LAB + "_" + AIRBOX_LAB,
                )
            )

        return surf_list

    @staticmethod
    def get_boundary_condition(line: Line, boundary_prop: dict) -> str:
        """Returns the boundary name on a line that is used in FEA coupling

        Parameters
        ----------
        line :
            a line with a label

        Returns
        -------
        label : string
            boundary name
        """
        # The id index at the end of lamination label is removed because
        # MagElemer and StructElmer dictionaries don't support it
        if line.prop_dict and BOUNDARY_PROP_LAB in line.prop_dict:
            label_with_id = line.prop_dict[BOUNDARY_PROP_LAB]
            if "-0" in label_with_id[-2:] or "-1" in label_with_id[-2:]:
                label_without_id = label_with_id[:-2]
            else:
                label_without_id = label_with_id
            if label_without_id in boundary_prop:
                return boundary_prop[label_without_id]
        return ""

    @staticmethod
    def get_sliding_band(sym: int, machine: Machine) -> list:
        """Returns  a list of surface in the airgap including the sliding band surface

        Parameters
        ----------
        sym: int
            Symmetry factor (1= full machine, 2= half of the machine...)
        machine: Machine
            Machine to draw

        Returns
        -------
        surf_list: list
            List of surface in the airgap including the sliding band surface
        """
        lam_list = machine.get_lam_list()
        lam_int = lam_list[0]
        lam_ext = lam_list[1]
        lab_int = lam_int.get_label()
        lab_ext = lam_ext.get_label()

        Rgap_mec_int = lam_int.comp_radius_mec()
        Rgap_mec_ext = lam_ext.comp_radius_mec()
        Sor = lam_ext.Rext
        Wgap_mec = Rgap_mec_ext - Rgap_mec_int
        W_sb = Wgap_mec / 4  # Width sliding band
        tol = 0.1e-3  # Tolerance

        surf_list = []
        if sym == 1:  # Complete machine
            # Internal AirGap
            int_airgap_cir = Circle(
                center=0,
                radius=Rgap_mec_int + W_sb,
                label=lab_int + "_" + AIRGAP_LAB + BOT_LAB,
                point_ref=(Rgap_mec_int + W_sb / 2) * np.exp(1j * np.pi / 2),
                prop_dict={BOUNDARY_PROP_LAB: AR_B_LAB},
            )
            surf_list.append(int_airgap_cir)
            # Internal Sliding band
            int_sb_cir = Circle(
                center=0,
                radius=Rgap_mec_int + 2 * W_sb - tol / 10,
                label=NO_LAM_LAB + "_" + SLID_LAB + BOT_LAB,
                point_ref=(Rgap_mec_ext - W_sb / 2) * np.exp(1j * np.pi / 2),
                prop_dict={BOUNDARY_PROP_LAB: SBR_B_LAB},
            )
            surf_list.append(
                SurfRing(
                    out_surf=int_sb_cir,
                    in_surf=int_airgap_cir,
                    label=NO_LAM_LAB + "_" + SLID_LAB + BOT_LAB,
                    point_ref=(Rgap_mec_ext - W_sb / 2) * np.exp(1j * np.pi / 2),
                )
            )
            ext_sb_cir = Circle(
                center=0,
                radius=Rgap_mec_int + 2 * W_sb + tol / 10,
                label=NO_LAM_LAB + "_" + SLID_LAB + TOP_LAB,
                point_ref=(Rgap_mec_ext - W_sb / 2) * np.exp(1j * np.pi / 2),
                prop_dict={BOUNDARY_PROP_LAB: SBR_T_LAB},
            )
            ext_airgap_cir = Circle(
                center=0,
                radius=Rgap_mec_int + 3 * W_sb,
                label=lab_ext + "_" + AIRGAP_LAB + TOP_LAB,
                point_ref=(Rgap_mec_ext - W_sb / 2) * np.exp(1j * np.pi / 2),
                prop_dict={BOUNDARY_PROP_LAB: AR_T_LAB},
            )
            # External Sliding band
            surf_list.append(
                SurfRing(
                    out_surf=ext_airgap_cir,
                    in_surf=ext_sb_cir,
                    label=NO_LAM_LAB + "_" + SLID_LAB + TOP_LAB,
                    point_ref=(Rgap_mec_ext - W_sb / 2) * np.exp(1j * np.pi / 2),
                )
            )
            lam_ext_cir = Circle(
                center=0,
                radius=1.1 * Rgap_mec_ext,  # Hopefully enough to reach the windings
                label=lab_ext + "_" + AIRBOX_LAB + BOT_LAB,
                point_ref=(Rgap_mec_ext - W_sb / 2) * np.exp(1j * np.pi / 2),
                prop_dict={BOUNDARY_PROP_LAB: AIRBOX_R_LAB},
            )
            # External AirGap
            surf_list.append(
                SurfRing(
                    out_surf=lam_ext_cir,
                    in_surf=ext_airgap_cir,
                    label=lab_ext + "_" + AIRGAP_LAB + TOP_LAB,
                    point_ref=(Rgap_mec_ext - W_sb / 2) * np.exp(1j * np.pi / 2),
                )
            )

        else:  # Symmetry
            # Internal AirGap
            Z0 = 0 * np.exp(1j * 2 * np.pi / sym)
            Z2 = Rgap_mec_int + W_sb
            Z3 = Z2 * np.exp(1j * 2 * np.pi / sym)
            airgap_lines: list[Line] = []
            airgap_lines.append(
                Segment(begin=Z0, end=Z2, prop_dict={BOUNDARY_PROP_LAB: AS_BR_LAB})
            )
            int_airgap_arc = Arc1(
                begin=Z2,
                end=Z3,
                radius=Rgap_mec_int + W_sb,
                prop_dict={BOUNDARY_PROP_LAB: AR_B_LAB},
                is_trigo_direction=True,
            )
            airgap_lines.append(int_airgap_arc)
            airgap_lines.append(
                Segment(begin=Z3, end=Z0, prop_dict={BOUNDARY_PROP_LAB: AS_BL_LAB})
            )

            surf_list.append(
                SurfLine(
                    line_list=airgap_lines,
                    point_ref=(Z2 - W_sb / 2) * np.exp(1j * np.pi / sym),
                    label=lab_int + "_" + AIRGAP_LAB + BOT_LAB,
                )
            )

            # Internal Sliding Band
            Z4 = Rgap_mec_int + 2 * W_sb - tol / 10
            Z5 = Z4 * np.exp(1j * 2 * np.pi / sym)
            airgap_lines = []
            airgap_lines.append(
                Segment(begin=Z2, end=Z4, prop_dict={BOUNDARY_PROP_LAB: SBS_BR_LAB})
            )
            int_sb_arc = Arc1(
                begin=Z4,
                end=Z5,
                radius=Rgap_mec_int + 2 * W_sb - tol / 10,
                prop_dict={BOUNDARY_PROP_LAB: SBR_B_LAB},
                is_trigo_direction=True,
            )
            airgap_lines.append(int_sb_arc)
            airgap_lines.append(
                Segment(begin=Z5, end=Z3, prop_dict={BOUNDARY_PROP_LAB: SBS_BL_LAB})
            )
            int_airgap_arc_copy = Arc1(
                begin=Z2,
                end=Z3,
                radius=Rgap_mec_int + W_sb,
                # label="int_airgap_arc_copy",
                prop_dict={BOUNDARY_PROP_LAB: AR_B_LAB},
                is_trigo_direction=True,
            )
            int_airgap_arc_copy.reverse()
            airgap_lines.append(int_airgap_arc_copy)
            surf_list.append(
                SurfLine(
                    line_list=airgap_lines,
                    point_ref=(Z4 - W_sb / 2) * np.exp(1j * np.pi / sym),
                    label=NO_LAM_LAB + "_" + SLID_LAB + BOT_LAB,
                )
            )

            # External Sliding Band
            Z6 = Rgap_mec_int + 2 * W_sb + tol / 10
            Z7 = Z6 * np.exp(1j * 2 * np.pi / sym)
            Z8 = Rgap_mec_int + 3 * W_sb
            Z9 = Z8 * np.exp(1j * 2 * np.pi / sym)
            airgap_lines = []
            airgap_lines.append(  # Right Top SB
                Segment(begin=Z6, end=Z8, prop_dict={BOUNDARY_PROP_LAB: SBS_TR_LAB})
            )
            ext_airgap_arc = Arc1(
                begin=Z8,
                end=Z9,
                radius=Rgap_mec_int + 3 * W_sb,
                prop_dict={BOUNDARY_PROP_LAB: AR_T_LAB},  # Top Radius SB
                is_trigo_direction=True,
            )
            airgap_lines.append(ext_airgap_arc)
            airgap_lines.append(  # Left Top SB
                Segment(begin=Z9, end=Z7, prop_dict={BOUNDARY_PROP_LAB: SBS_TL_LAB})
            )
            ext_sb_arc = Arc1(
                begin=Z6,
                end=Z7,
                radius=Rgap_mec_int + 2 * W_sb + tol / 10,
                # label="ext_sb_arc",
                prop_dict={BOUNDARY_PROP_LAB: SBR_T_LAB},
                is_trigo_direction=True,
            )
            ext_sb_arc.reverse()
            airgap_lines.append(ext_sb_arc)
            surf_list.append(
                SurfLine(
                    line_list=airgap_lines,
                    point_ref=(Z8 - W_sb / 2) * np.exp(1j * np.pi / sym),
                    label=NO_LAM_LAB + "_" + SLID_LAB + TOP_LAB,
                )
            )

            # External AirGap
            Z10 = Sor
            Z11 = Z10 * np.exp(1j * 2 * np.pi / sym)
            airgap_lines = []
            airgap_lines.append(
                Segment(begin=Z8, end=Z10, prop_dict={BOUNDARY_PROP_LAB: AS_TR_LAB})
            )
            lam_ext_arc = Arc1(
                begin=Z10,
                end=Z11,
                radius=Sor,
                # label="int_airgap_arc_copy",
                is_trigo_direction=True,
            )
            airgap_lines.append(lam_ext_arc)
            airgap_lines.append(
                Segment(begin=Z11, end=Z9, prop_dict={BOUNDARY_PROP_LAB: AS_TL_LAB})
            )
            ext_airgap_arc_copy = Arc1(
                begin=Z8,
                end=Z9,
                radius=Rgap_mec_int + 3 * W_sb,
                # label="ext_airgap_arc_copy",
                prop_dict={BOUNDARY_PROP_LAB: AR_T_LAB},
                is_trigo_direction=True,
            )
            ext_airgap_arc_copy.reverse()
            airgap_lines.append(ext_airgap_arc_copy)
            surf_list.append(
                SurfLine(
                    line_list=airgap_lines,
                    point_ref=(Z8 + W_sb / 2) * np.exp(1j * np.pi / sym),
                    label=lab_ext + "_" + AIRGAP_LAB + TOP_LAB,
                )
            )
        return surf_list
