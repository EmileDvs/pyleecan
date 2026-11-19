import numpy as np

from ....Classes.MeshSolution import MeshSolution
from ....Classes.SolutionData import SolutionData
from ....Classes.SolutionVector import SolutionVector
from ....Functions.MeshSolution.build_solution_data import build_solution_data
from ....Functions.MeshSolution.build_solution_vector import build_solution_vector


def get_meshsolution(self, Time=None):
    """Get magnetic meshsolution with solutions of stator and rotor frames merged on the same Time axis.

    OutMag.meshsolution stores solutions in stator frame (e.g. "B_S") and in rotor frame (e.g. "B_R"),
    each one defined on the elements of its frame with its own time axis.
    The returned meshsolution contains one solution per quantity (e.g. "B") defined on all elements.
    It is not stored in OutMag.

    Parameters
    ----------
    self : OutMag
        a OutMag object
    Time : Data1D
        Time axis on which to merge stator and rotor solutions (default: full time axis without periodicity)

    Returns
    -------
    meshsol : MeshSolution
        MeshSolution containing magnetic quantities for both stator and rotor elements
    """

    if self.meshsolution is None:
        return None

    # Pairs of stator / rotor frame solutions
    label_list = [
        key[:-2]
        for key in self.meshsolution
        if key.endswith("_S") and key[:-2] + "_R" in self.meshsolution
    ]

    if len(label_list) == 0:
        # Meshsolution is not split in stator and rotor frames
        return self.meshsolution

    if Time is None:
        Time = self.axes_dict["time"].get_axis_periodic(Nper=1, is_aper=False)

    time_val = Time.get_values(is_smallestperiod=True)

    Indice_Element = self.axes_dict["indice_element"]
    indice_element_S = self.axes_dict["indice_element_S"].values
    indice_element_R = self.axes_dict["indice_element_R"].values
    Nelem = Indice_Element.get_length()

    if "indice_node" in self.axes_dict:
        Indice_Node = self.axes_dict["indice_node"]
        indice_node_S = self.axes_dict["indice_node_S"].values
        indice_node_R = self.axes_dict["indice_node_R"].values
        Nnode = Indice_Node.get_length()

    Nt = time_val.size
    Nz = self.axes_dict["z"].get_length(is_pattern=True)

    # Rebuild solution dict containing both stator and rotor values
    solution_dict = {}
    for label in label_list:
        sol_S = self.meshsolution[label + "_S"]
        sol_R = self.meshsolution[label + "_R"]

        if sol_S.type_element == "node":
            Nval = Nnode
            ind_S = indice_node_S
            ind_R = indice_node_R
            Indice = Indice_Node
        else:
            Nval = Nelem
            ind_S = indice_element_S
            ind_R = indice_element_R
            Indice = Indice_Element

        axis_list = [Time.copy(), Indice.copy(), self.axes_dict["z"].copy()]

        if isinstance(sol_S, SolutionVector):
            # Case for B, H

            # Calculate stator and rotor VectorField on time values
            vf_S = sol_S.field.get_vectorfield_along(
                "time=axis_data",
                "indice",
                "z[smallestpattern]",
                axis_data={"time": time_val},
            )
            vf_R = sol_R.field.get_vectorfield_along(
                "time=axis_data",
                "indice",
                "z[smallestpattern]",
                axis_data={"time": time_val},
            )

            # Rebuild values array in initial mesh format for each component
            sol_val = np.zeros((Nt, Nval, Nz, 2), dtype=float)
            for ii, (comp_S, comp_R) in enumerate(
                zip(vf_S.components.values(), vf_R.components.values())
            ):
                if comp_S.values.ndim == 2:  # No slices
                    sol_val[:, ind_S, :, ii] = comp_S.values.T[:, :, None]
                    sol_val[:, ind_R, :, ii] = comp_R.values.T[:, :, None]
                else:
                    sol_val[:, ind_S, :, ii] = comp_S.values.swapaxes(0, 1)
                    sol_val[:, ind_R, :, ii] = comp_R.values.swapaxes(0, 1)

            solution_dict[label] = build_solution_vector(
                field=sol_val,
                axis_list=axis_list,
                name=vf_S.name,
                symbol=sol_S.label,
                unit=comp_S.unit,
                type_element=sol_S.type_element,
            )

        elif isinstance(sol_S, SolutionData):
            # Case for Az_elem, Az_node, mu

            # Calculate stator and rotor DataTime on time values
            dt_S = sol_S.field.get_data_along(
                "time=axis_data",
                "indice",
                "z[smallestpattern]",
                axis_data={"time": time_val},
            )
            dt_R = sol_R.field.get_data_along(
                "time=axis_data",
                "indice",
                "z[smallestpattern]",
                axis_data={"time": time_val},
            )

            # Rebuild values array in initial mesh format
            sol_val = np.zeros((Nt, Nval, Nz), dtype=float)
            if dt_S.values.ndim == 2:  # No slices
                sol_val[:, ind_S, :] = dt_S.values[:, :, None]
                sol_val[:, ind_R, :] = dt_R.values[:, :, None]
            else:
                sol_val[:, ind_S, :] = dt_S.values
                sol_val[:, ind_R, :] = dt_R.values

            solution_dict[label] = build_solution_data(
                field=sol_val,
                axis_list=axis_list,
                name=dt_S.name,
                symbol=sol_S.label,
                unit=dt_S.unit,
                type_element=sol_S.type_element,
            )

        else:
            raise TypeError("Expecting SolutionVector or SolutionData as field")

    return MeshSolution(
        label=self.meshsolution.label,
        mesh=self.meshsolution.mesh,
        solution_dict=solution_dict,
        dimension=self.meshsolution.dimension,
        group=self.meshsolution.group,
    )
