# Experimental dataclass generated from Generator/ClassesRef/Simulation/ForceTensor.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .data_1d import Data1D
from .data_time import DataTime
from .force import Force
from .mesh_solution import MeshSolution
from .solution_vector import SolutionVector
from .vector_field import VectorField


@dataclass(eq=False)
class ForceTensor(Force):
    """Force various tensors (Maxwell, magnetostrictive) model for radial flux machines

    Attributes
    ----------
    group : str
        Name of the group selected for magnetic force computation. If None, all the domain is selected.
        Default: "stator core"
    tensor : dict or None
        Force model(s) to be used
        Default: {}
    """

    group: str = "stator core"
    """Name of the group selected for magnetic force computation. If None, all the domain is selected."""
    tensor: dict[str, Any] | None = field(default_factory=dict)
    """Force model(s) to be used"""

    # Inlined from Methods.Simulation.ForceTensor.comp_force
    def comp_force(self, output, axes_dict):
        """Compute the air-gap surface force based on Maxwell Tensor (MT).

        Parameters
        ----------
        self : ForceMT
            A ForceMT object
        output : Output
            an Output object (to update)
        axes_dict: {Data}
            Dict of axes used for force calculation

        Returns
        -------
        out_dict: dict
            Dict containing the following quantities:
                AGSF_r : ndarray
                    Airgap radial Maxwell stress (Nt,Na,Nz) [N/m²]
                AGSF_t : ndarray
                    Airgap tangential Maxwell stress (Nt,Na,Nz) [N/m²]
                AGSF_z : ndarray
                    Airgap axial Maxwell stress (Nt,Na,Nz) [N/m²]

        """

        # Test comp_force_nodal #

        out_dict = self.comp_force_nodal(output, axes_dict)

        return out_dict

    # Inlined from Methods.Simulation.ForceTensor.comp_force_nodal
    def comp_force_nodal(self, output, axes_dict):
        """Run the nodal forces calculation based on a tensor.

        from publications:


        Parameters
        ----------
        self : ForceTensor
            A ForceTensor object

        output : Output
            an Output object (to update)

        """

        dim = 2
        Time = axes_dict["time"]
        Nt_tot = Time.get_length()  # Number of time step

        meshsolution_mag = output.mag.meshsolution  # Comes from FEMM simulation

        # Select the target group (stator, rotor ...) or all the domain
        if self.group is None:
            meshsolution_group = meshsolution_mag
        else:
            meshsolution_group = meshsolution_mag.get_group(self.group)

        mesh = meshsolution_group.mesh

        # New meshsolution object for output, that could be different from the one inputed
        meshsolution = MeshSolution(mesh=mesh.copy(), dimension=dim)

        # Load magnetic flux B and H and mu objects
        B_sol = meshsolution_group.get_solution(label="B")
        H_sol = meshsolution_group.get_solution(label="H")
        mu_sol = meshsolution_group.get_solution(label=r"\mu")

        # Import time vector from Time Data object
        if self.is_periodicity_t is not None:
            is_periodicity_t = self.is_periodicity_t

        is_periodicity_t, is_antiper_t = Time.get_periodicity()
        time = Time.get_values(
            is_oneperiod=is_periodicity_t,
            is_antiperiod=is_antiper_t and is_periodicity_t,
        )

        # Load magnetic flux B and H of size (Nt_tot, nb_elem, dim) and mu (Nt_tot, nb_elem)
        resultB = B_sol.field.get_xyz_along(
            "indice",
            "time=axis_data",
            axis_data={"time": time},
            is_squeeze=False,
        )
        indice = resultB["indice"]  # Store elements indices

        Bx = resultB["comp_x"]
        By = resultB["comp_y"]
        B = np.stack((Bx, By), axis=2)

        resultH = H_sol.field.get_xyz_along(
            "indice",
            "time=axis_data",
            axis_data={"time": time},
            is_squeeze=False,
        )
        Hx = resultH["comp_x"]
        Hy = resultH["comp_y"]
        H = np.stack((Hx, Hy), axis=2)

        resultmu = mu_sol.field.get_along(
            "indice",
            "time=axis_data",
            axis_data={"time": time},
            is_squeeze=False,
        )
        mu = resultmu["\\mu"]

        # Move time axis at the end for clarity purpose
        B = np.moveaxis(B, 0, -1)
        H = np.moveaxis(H, 0, -1)
        mu = np.moveaxis(mu, 0, -1)

        # Loop on elements and nodes for nodal forces
        f, connect = self.element_loop(mesh, B, H, mu, indice, dim, Nt_tot)

        indices_nodes = mesh.node.indice.copy()
        Indices_Point = Data1D(name="indice", values=indices_nodes, is_components=True)

        # Time axis goes back to first axis
        f = np.moveaxis(f, -1, 0)

        components = {}

        fx_data = DataTime(
            name="Nodal force (x)",
            unit="N",
            symbol="Fx",
            axes=[Time, Indices_Point],
            values=f[..., 0],
        )
        components["comp_x"] = fx_data

        fy_data = DataTime(
            name="Nodal force (y)",
            unit="N",
            symbol="Fy",
            axes=[Time, Indices_Point],
            values=f[..., 1],
        )
        components["comp_y"] = fy_data

        vec_force = VectorField(name="Nodal forces", symbol="F", components=components)
        solforce = SolutionVector(field=vec_force, type_element="node", label="F")
        meshsolution.solution.append(solforce)

        out_dict = {}
        out_dict["meshsolution"] = meshsolution

        return out_dict

    # Inlined from Methods.Simulation.ForceTensor.comp_magnetostrictive_tensor
    def comp_magnetostrictive_tensor(
        self,
        M,
        Nt_tot,
        polynomial_coeffs=[[0.719, -0.078, -0.042], [-0.391, 0.114, 0.004]],
    ):
        """Compute magnetostrictive tensor.

        From publications: L. Vandevelde, J. Gyselinck, M. A. C. De Wulf and J. A. A. Melkebeek, "Finite-element computation of the deformation of ferromagnetic material taking into account magnetic forces and magnetostriction," in IEEE Transactions on Magnetics, vol. 40, no. 2, pp. 565-568, March 2004, doi: 10.1109/TMAG.2004.824540.

        Parameters
        ----------

        M : array
            Magnetization vector in the elements, field, material, ...

        Nt_tot: scalar
            Number of time steps

        polynomial_coeffs : 2x3 List, optional
            alpha(i,j) coeffs for polynomal expression of alpha1 and alpha2


        Return
        ----------
        magnetostric_tensor : dim * dim * Nt_tot array
            magnetrostictive tensor in the current element for differents time steps


        """
        # Coeffs from a reference material in IEEETranMagn2004
        a10 = polynomial_coeffs[0][0]
        a12 = polynomial_coeffs[0][1]
        a14 = polynomial_coeffs[0][2]
        a20 = polynomial_coeffs[1][0]
        a22 = polynomial_coeffs[1][1]
        a24 = polynomial_coeffs[1][2]

        mu_0 = 4 * np.pi * 1e-7

        M_norm = np.linalg.norm(M, axis=(0, 1))  # M matrices are in the first two axes
        mu_times_Mnorm_squared = np.multiply(mu_0, M_norm) ** 2

        alpha1 = a10 + a12 * mu_times_Mnorm_squared + a14 * mu_times_Mnorm_squared**2
        alpha2 = a20 + a22 * mu_times_Mnorm_squared + a24 * mu_times_Mnorm_squared**2

        magnetostric_tensor = np.zeros((2, 2, Nt_tot))

        # Iteration over time step
        for ti in range(Nt_tot):
            M_times_M = np.dot(M[:, :, ti], np.transpose(M[:, :, ti]))

            M_norm_squared = np.linalg.norm(M[:, :, ti]) ** 2
            I = np.eye(2, 2)

            first_member = -alpha1[ti] * mu_0 * M_times_M
            second_member = -alpha2[ti] * mu_0 * M_norm_squared * I

            magnetostric_tensor[:, :, ti] = first_member + second_member

        return magnetostric_tensor

    # Inlined from Methods.Simulation.ForceTensor.element_loop
    def element_loop(
        self,
        mesh,
        B,
        H,
        mu,
        indice,
        dim,
        Nt_tot,
        polynomial_coeffs=[[0.719, -0.078, -0.042], [-0.391, 0.114, 0.004]],
    ):
        """compute nodal forces with a loop on elements and nodes

        from publications:

        Parameters
        ----------
        self : ForceTensor
            A ForceTensor object
        mesh : MeshMat
            A Mesh object
        polynomial_coeffs : List
            alpha(i,j) coeffs for polynomal expression of alpha1 and alpha2. Shape of (s2*3)

        Return
        ----------
        f : ndarray
            nodal forces of shape (nb_nodes*dim*Nt_tot)
        connect :  ndarray
            table of mesh connectivity of shape (nb_element*nb_node_per_element)

        """

        # For every type of element (now only Triangle3, TO BE extended)
        for key in mesh.element_dict:
            # Number of nodes per element
            nb_node_per_element = mesh.element_dict[key].nb_node_per_element

            mesh_element_key = mesh.element_dict[key]

            # Each row of connect is an element
            connect = mesh.element_dict[key].get_connectivity()

            # Total nodes number
            nb_node = mesh.node.nb_node

            # Nodal forces init
            f = np.zeros((nb_node, dim, Nt_tot), dtype=np.float)

            # ref_element = mesh.element_dict[key].ref_element // pas besoin d'interpoler car tout est cst

            # Gauss nodes
            # pts_gauss, poidsGauss, nb_gauss = mesh.element_dict[
            #     key
            # ].gauss_point.get_gauss_points()

            # indice_elem = mesh.element_dict[key].indice

            # Loop on element (elt)
            for elt_indice, elt_number in enumerate(indice):
                # elt nodes numbers, can differ from indices
                node_number = mesh_element_key.get_connectivity(elt_number)

                # elt nodes coordonates
                element_coordinate = mesh.get_element_coordinate(elt_number)[key]

                # elt physical fields values
                Be = B[elt_indice, :, :]
                He = H[elt_indice, :, :]
                mue = mu[elt_indice, :]
                mu_0 = 4 * np.pi * 1e-7

                # reshaped for matrix product purpose
                Me = np.reshape(Be / mu_0 - He, (dim, 1, Nt_tot))

                # Total tensor initalization
                total_tensor = np.zeros((dim, dim, Nt_tot))

                # elt magnetostrictive tensor
                if self.tensor["magnetostriction"]:
                    tme = self.comp_magnetostrictive_tensor(
                        M=Me, Nt_tot=Nt_tot, polynomial_coeffs=polynomial_coeffs
                    )
                    total_tensor += tme

                # Triangle orientation, needed for normal orientation. 1 if trigo oriented, -1 otherwise
                orientation_sign = np.sign(
                    np.cross(
                        element_coordinate[1] - element_coordinate[0],
                        element_coordinate[2] - element_coordinate[0],
                    )
                )

                # Loop on edges
                for n in range(nb_node_per_element):
                    # Get current node + next node indices (both needed since pression will be computed on edges because of Green Ostrogradski)
                    node_indice = np.where(mesh.node.indice == node_number[n])[0][0]

                    next_node_indice = np.where(
                        mesh.node.indice == node_number[(n + 1) % nb_node_per_element]
                    )[0][0]

                    # Edge cooordinates
                    edge_vector = (
                        element_coordinate[(n + 1) % nb_node_per_element]
                        - element_coordinate[n % nb_node_per_element]
                    )  # coordonées du vecteur nn+1

                    # Volume ratio (Green Ostrogradski)
                    Ve0 = np.linalg.norm(edge_vector)

                    # Normalized normal vector n, that has to be directed outside the element (i.e. normal ^ edge same sign as the orientation)
                    normal_to_edge_unoriented = (
                        np.array((edge_vector[1], -edge_vector[0])) / Ve0
                    )
                    normal_to_edge = (
                        normal_to_edge_unoriented
                        * np.sign(np.cross(normal_to_edge_unoriented, edge_vector))
                        * orientation_sign
                    )
                    normal_to_edge.reshape(dim, 1)

                    # Green Ostrogradski <tensor, normal> scalar product
                    edge_force = np.tensordot(
                        total_tensor, normal_to_edge, [[1], [0]]
                    )  # [[1],[0]] means sum product over rows for normal (which is vertical) and over rows for tme

                    # Total edge force contribution, to be added to the 2 nodes that made the edge
                    fe = -Ve0 * edge_force
                    f[node_indice, :, :] = f[node_indice, :, :] + fe / 2
                    f[next_node_indice, :, :] = f[next_node_indice, :, :] + fe / 2

        return f, connect
