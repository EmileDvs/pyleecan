from numpy import zeros, mean as np_mean, array, unique
from SciDataTool import Data1D

from ....Classes._FEMMHandler import _FEMMHandler
from ....Classes.OutMagFEMM import OutMagFEMM
from ....Functions.FEMM.draw_FEMM import draw_FEMM
from ....Functions.labels import STATOR_LAB, ROTOR_LAB
from ....Functions.MeshSolution.build_meshsolution import build_meshsolution
from ....Functions.MeshSolution.build_solution_data import build_solution_data
from ....Functions.MeshSolution.build_solution_vector import build_solution_vector


def comp_flux_airgap(self, output, axes_dict, Is_val=None, Ir_val=None):
    """Build and solve FEMM model to calculate and store magnetic quantities

    Parameters
    ----------
    self : MagFEMM
        a MagFEMM object
    output : Output
        an Output object
    axes_dict: {Data}
        Dict of axes used for magnetic calculation

    Returns
    -------
    out_dict: dict
        Dict containing the following quantities:
            Br : ndarray
                Airgap radial flux density (Nt,Na) [T]
            Bt : ndarray
                Airgap tangential flux density (Nt,Na) [T]
            Tem : ndarray
                Electromagnetic torque over time (Nt,) [Nm]
            Phi_wind_stator : ndarray
                Stator winding flux (qs,Nt) [Wb]
            Phi_wind : dict
                Dict of winding fluxlinkage with respect to Machine.get_lam_list_label (qs,Nt) [Wb]
            meshsolution: MeshSolution
                MeshSolution object containing magnetic quantities B, H, mu for each time step
    """

    logger = self.get_logger()

    # Init output
    out_dict = dict()
    if output.mag.internal is None:
        output.mag.internal = OutMagFEMM()

    # Get time and angular axes
    Angle = axes_dict["angle"]
    Time = axes_dict["time"]

    # Set the angular symmetry factor according to the machine and check if it is anti-periodic
    sym, is_antiper_a = Angle.get_periodicity()

    # Import angular vector from Data object
    angle = Angle.get_values(
        is_oneperiod=self.is_periodicity_a,
        is_antiperiod=is_antiper_a and self.is_periodicity_a,
    )
    Na = angle.size

    # Check if the time axis is anti-periodic
    _, is_antiper_t = Time.get_periodicity()

    # Change Time periodicity in case meshsolution is requested
    # and rotor time periodicity is not the same as stator time periodicity
    if (
        self.is_periodicity_t
        and self.is_get_meshsolution
        and self.is_separate_meshsolution
    ):
        # Get time periodicity in stator and rotor frame
        pert_S, is_apert_S, pert_R, _ = output.simu.machine.comp_periodicity_time()

        Time_S = Time.copy()  # Time axis in stator frame
        Time_R = Time.copy()  # Time axis in rotor frame
        if (
            pert_S == pert_R  # same time periodicity for stator and rotor
            and is_apert_S  # anti-periodicity in stator frame
            and is_antiper_t  # anti-periodicity requested in model
            and "antiperiod"
            in Time.symmetries  # anti-periodicity existing in Time axis
        ):
            # Anti-periodicity in stator frame become periodicity in rotor frame (there is no anti-periodicity in rotor frame)
            Time_R.symmetries = {"period": Time.symmetries["antiperiod"]}
        else:
            # Change stator to rotor periodicity
            Time_R = Time_S.get_axis_periodic(Nper=pert_R, is_aper=False)
            Time = Time_R.copy()
            is_antiper_t = False
            # Recalculate currents with updated Time axis
            Is_val, Ir_val = self.comp_I_mag(output, Time)

        # Store time axes for both stator and rotor frame
        axes_dict["time_S"] = Time_S
        axes_dict["time_R"] = Time_R

    # Number of time steps
    time = Time.get_values(
        is_oneperiod=self.is_periodicity_t,
        is_antiperiod=is_antiper_t and self.is_periodicity_t,
    )
    Nt = time.size

    # Get rotor angular position
    angle_rotor = output.get_angle_rotor()[0:Nt]

    # Setup the FEMM simulation
    # Geometry building and assigning property in FEMM
    # Instanciate a new FEMM
    femm = _FEMMHandler()
    output.mag.internal.handler_list.append(femm)
    if self.import_file is None:
        path_femm = self.get_path_save_fem(output)
        logger.debug("Drawing machine in FEMM at " + path_femm)
        FEMM_dict = draw_FEMM(
            femm,
            output,
            is_mmfr=self.is_mmfr,
            is_mmfs=self.is_mmfs,
            sym=sym,
            is_antiper=is_antiper_a,
            type_calc_leakage=self.type_calc_leakage,
            is_remove_ventS=self.is_remove_ventS,
            is_remove_ventR=self.is_remove_ventR,
            is_remove_slotS=self.is_remove_slotS,
            is_remove_slotR=self.is_remove_slotR,
            type_BH_stator=self.type_BH_stator,
            type_BH_rotor=self.type_BH_rotor,
            kgeo_fineness=self.Kgeo_fineness,
            kmesh_fineness=self.Kmesh_fineness,
            user_FEMM_dict=self.FEMM_dict_enforced,
            path_save=path_femm,
            is_sliding_band=self.is_sliding_band,
            transform_list=self.transform_list,
            rotor_dxf=self.rotor_dxf,
            stator_dxf=self.stator_dxf,
            is_fast_draw=self.is_fast_draw,
            T_mag=self.T_mag,
        )
    else:
        logger.debug("Reusing the FEMM file: " + self.import_file)
        if output.mag.internal.FEMM_dict is not None:
            FEMM_dict = output.mag.internal.FEMM_dict
        else:
            FEMM_dict = self.FEMM_dict_enforced

    # Init flux arrays in out_dict
    out_dict["B_{rad}"] = zeros((Nt, Na))
    out_dict["B_{circ}"] = zeros((Nt, Na))
    if self.is_calc_torque_energy:
        # Init torque array in out_dict
        out_dict["Tem"] = zeros((Nt))
    # Init lamination winding flux list of arrays in out_dict
    machine = output.simu.machine
    out_dict["Phi_wind"] = {}
    axes_dict_elec = output.elec.axes_dict
    for label in machine.get_lam_list_label():
        if "phase_" + label in axes_dict_elec:
            qs = axes_dict_elec["phase_" + label].get_length(is_smallestperiod=True)
            out_dict["Phi_wind"][label] = zeros((Nt, qs))
    # delete 'Phi_wind' if empty
    if len(out_dict["Phi_wind"]) == 0:
        out_dict.pop("Phi_wind")

    # Solve for all time step and store all the results in out_dict
    if self.nb_worker > 1:
        # A Femm handler will be created for each worker
        femm.closefemm()
        output.mag.internal.handler_list.remove(femm)
        # With parallelization
        (
            B_elem,
            H_elem,
            mu_elem,
            A_node,
            meshFEMM,
            groups,
            A_elem,
        ) = self.solve_FEMM_parallel(
            femm,
            output,
            out_dict,
            FEMM_dict=FEMM_dict,
            sym=sym,
            Nt=Nt,
            angle=angle,
            Is=Is_val,
            Ir=Ir_val,
            angle_rotor=angle_rotor,
            filename=self.import_file,
        )
    else:
        # Without parallelization
        B_elem, H_elem, mu_elem, A_node, meshFEMM, groups, A_elem = self.solve_FEMM(
            femm,
            output,
            out_dict,
            FEMM_dict=FEMM_dict,
            sym=sym,
            Nt=Nt,
            angle=angle,
            Is=Is_val,
            Ir=Ir_val,
            angle_rotor=angle_rotor,
            is_close_femm=self.is_close_femm,
            filename=self.import_file,
        )

    # Store FEMM_dict in to avoid drawing the machine several times
    output.mag.internal.FEMM_dict = FEMM_dict

    # Store stator winding flux
    if STATOR_LAB + "-0" in out_dict["Phi_wind"].keys():
        out_dict["Phi_wind_stator"] = out_dict["Phi_wind"][STATOR_LAB + "-0"]

    # Store mesh data & solution
    if self.is_get_meshsolution and B_elem is not None:
        if not self.is_periodicity_t or not self.is_separate_meshsolution:
            # Define axis
            Time = Time.copy()
            meshFEMM.sym = sym
            meshFEMM.is_antiper_a = is_antiper_a
            indices_element = meshFEMM.element_dict["triangle"].indice
            Indices_Element = Data1D(
                name="indice",
                values=indices_element,
                is_components=True,
                is_overlay=False,
            )
            # Slice = axes_dict["z"]
            axis_list = [Time, Indices_Element]

            B_sol = build_solution_vector(
                field=B_elem[:, :, None, :],  # quick fix for slice issue
                axis_list=axis_list,
                name="Magnetic Flux Density",
                symbol="B",
                unit="T",
            )
            H_sol = build_solution_vector(
                field=H_elem[:, :, None, :],
                axis_list=axis_list,
                name="Magnetic Field",
                symbol="H",
                unit="A/m",
            )
            mu_sol = build_solution_data(
                field=mu_elem[:, :, None],
                axis_list=axis_list,
                name="Magnetic Permeability",
                symbol="\\mu",
                unit="H/m",
            )
            Ae_sol = build_solution_data(
                field=A_elem[:, :, None],
                axis_list=axis_list,
                name="Magnetic Potential Vector (per element)",
                symbol="A_z^{element}",
                unit="Wb/m",
            )

            indices_nodes = meshFEMM.node.indice
            Indices_Nodes = Data1D(
                name="indice", values=indices_nodes, is_components=True
            )
            axis_list_node = [Time, Indices_Nodes]

            An_sol = build_solution_data(
                field=A_node,
                axis_list=axis_list_node,
                name="Magnetic Potential Vector (nodal)",
                symbol="A_z",
                unit="Wb/m",
            )
            An_sol.type_element = "node"

            solution_dict = {
                solution.label: solution
                for solution in [B_sol, H_sol, mu_sol, An_sol, Ae_sol]
            }

            out_dict["meshsolution"] = build_meshsolution(
                solution_dict=solution_dict,
                label="FEMM 2D Magnetostatic",
                mesh=meshFEMM,
                group=groups,
            )
        else:
            # Reduce output quantities to original number of time steps
            Nt_S = axes_dict["time_S"].get_length(is_smallestperiod=True)
            quantity_list = [
                "B_{rad}",
                "B_{circ}",
                "Phi_wind",
                "Tem",
                "Phi_wind_stator",
            ]
            for quantity in quantity_list:
                if quantity in out_dict:
                    if quantity == "Phi_wind":
                        for key, val in out_dict[quantity].items():
                            out_dict[quantity][key] = val[:Nt_S, ...]
                    else:
                        out_dict[quantity] = out_dict[quantity][:Nt_S, ...]

            # Separate stator and rotor elements
            list_elem_R = list()
            list_elem_S = list()
            groups_R = dict()
            groups_S = dict()
            for name, ind in groups.items():
                if STATOR_LAB.lower() in name:
                    list_elem_S.extend(ind)
                    groups_S[name] = ind
                elif ROTOR_LAB.lower() in name:
                    list_elem_R.extend(ind)
                    groups_R[name] = ind
                elif "airgap" in name:
                    if self.Rag_enforced is not None:
                        # Take enforced value
                        Rag = self.Rag_enforced
                    else:
                        Rag = machine.comp_Rgap_mec()
                    # Separate airgap belonging to rotor and airgap belonging to stator
                    elem_ag_coords = meshFEMM.get_element_coordinate(
                        element_indices=ind
                    )["triangle"]
                    elem_ag_centers = np_mean(elem_ag_coords, axis=1)
                    elem_ag_dist = (
                        elem_ag_centers[:, 0] ** 2 + elem_ag_centers[:, 1] ** 2
                    )
                    if machine.rotor.is_internal:
                        is_elem_ag_R = elem_ag_dist < Rag**2
                    else:
                        is_elem_ag_R = elem_ag_dist > Rag**2
                    list_elem_ag_R = array(ind)[is_elem_ag_R].tolist()
                    list_elem_ag_S = array(ind)[~is_elem_ag_R].tolist()

                    if len(list_elem_ag_R) > 0:
                        list_elem_R.extend(list_elem_ag_R)
                        groups_R[name + "_R"] = list_elem_ag_R
                    if len(list_elem_S) > 0:
                        list_elem_S.extend(list_elem_ag_S)
                        groups_S[name + "_S"] = list_elem_ag_S
            list_elem_R = unique(list_elem_R).tolist()
            list_elem_S = unique(list_elem_S).tolist()

            # Define axis
            meshFEMM.sym = sym
            meshFEMM.is_antiper_a = is_antiper_a

            Indices_Element_R = Data1D(
                name="indice",
                values=list_elem_R,
                is_components=True,
                is_overlay=False,
            )
            axis_list_R = [axes_dict["time_R"].copy(), Indices_Element_R]

            Indices_Element_S = Data1D(
                name="indice",
                values=list_elem_S,
                is_components=True,
                is_overlay=False,
            )
            axis_list = [axes_dict["time_S"].copy(), Indices_Element_S]

            # Store element values in stator frame
            B_sol = build_solution_vector(
                field=B_elem[:Nt_S, list_elem_S, None, :],  # quick fix for slice issue
                axis_list=axis_list,
                name="Magnetic Flux Density",
                symbol="B",
                unit="T",
            )
            H_sol = build_solution_vector(
                field=H_elem[:Nt_S, list_elem_S, None, :],
                axis_list=axis_list,
                name="Magnetic Field",
                symbol="H",
                unit="A/m",
            )
            mu_sol = build_solution_data(
                field=mu_elem[:Nt_S, list_elem_S, None],
                axis_list=axis_list,
                name="Magnetic Permeability",
                symbol="\\mu",
                unit="H/m",
            )
            Ae_sol = build_solution_data(
                field=A_elem[:Nt_S, list_elem_S, None],
                axis_list=axis_list,
                name="Magnetic Potential Vector (per element)",
                symbol="A_z^{element}",
                unit="Wb/m",
            )

            # Store element values in rotor frame
            B_sol_R = build_solution_vector(
                field=B_elem[:, list_elem_R, None, :],  # quick fix for slice issue
                axis_list=axis_list_R,
                name="Magnetic Flux Density",
                symbol="B",
                unit="T",
            )
            H_sol_R = build_solution_vector(
                field=H_elem[:, list_elem_R, None, :],
                axis_list=axis_list_R,
                name="Magnetic Field",
                symbol="H",
                unit="A/m",
            )
            mu_sol_R = build_solution_data(
                field=mu_elem[:, list_elem_R, None],
                axis_list=axis_list_R,
                name="Magnetic Permeability",
                symbol="\\mu",
                unit="H/m",
            )
            Ae_sol_R = build_solution_data(
                field=A_elem[:, list_elem_R, None],
                axis_list=axis_list_R,
                name="Magnetic Potential Vector (per element)",
                symbol="A_z^{element}",
                unit="Wb/m",
            )

            # Store nodal MVP in all motor (separate rotor and stator values)
            indices_nodes = meshFEMM.node.indice
            Indices_Nodes = Data1D(
                name="indice", values=indices_nodes, is_components=True
            )
            axis_list_node = [axes_dict["time_S"].copy(), Indices_Nodes]
            An_sol = build_solution_data(
                field=A_node[:Nt_S, :],
                axis_list=axis_list_node,
                name="Magnetic Potential Vector (nodal)",
                symbol="A_z",
                unit="Wb/m",
            )
            An_sol.type_element = "node"

            # Build solution vector dicts
            solution_dict = {solution.label: solution for solution in [An_sol]}

            solution_dict_S = {
                solution.label: solution for solution in [B_sol, H_sol, mu_sol, Ae_sol]
            }

            solution_dict_R = {
                solution.label: solution
                for solution in [B_sol_R, H_sol_R, mu_sol_R, Ae_sol_R]
            }

            # Build meshsolutions
            out_dict["meshsolution"] = build_meshsolution(
                solution_dict=solution_dict,
                label="FEMM 2D Magnetostatic",
                mesh=meshFEMM,
                group=groups,
            )

            out_dict["meshsolution_dict"] = {
                STATOR_LAB
                + "-0": build_meshsolution(
                    solution_dict=solution_dict_S,
                    label="FEMM 2D Magnetostatic Stator",
                    mesh=meshFEMM,
                    group=groups_S,
                ),
                ROTOR_LAB
                + "-0": build_meshsolution(
                    solution_dict=solution_dict_R,
                    label="FEMM 2D Magnetostatic Rotor",
                    mesh=meshFEMM,
                    group=groups_R,
                ),
            }

    return out_dict
