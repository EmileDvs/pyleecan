# Experimental pydantic model generated from Generator/ClassesRef/Elmer/ElmerResultsVTU.csv
"""Generated experimental pydantic model; do not edit by hand."""

import os
from typing import TYPE_CHECKING, Any, ClassVar

import numpy as np
from meshio import read
from pydantic import Field

from ...classes_common.errors import ElmerResultsVTUError
from ...classes_common.logger_context import get_logger
from ..mesh.mesh_solution import MeshSolution
from ..mesh.mesh_vtk import MeshVTK
from ..mesh.solution_data import SolutionData
from ..mesh.solution_vector import SolutionVector
from ..scidatatool.data_1d import Data1D
from ..scidatatool.data_time import DataTime
from ..scidatatool.norm_ref import NormRef
from ..scidatatool.vector_field import VectorField
from .elmer import Elmer

if TYPE_CHECKING:
    from ..scidatatool.data_nd import DataND


class ElmerResultsVTU(Elmer):
    """Class to get Elmer simulation results from a VTU file

    Attributes
    ----------
    label : str
        Label of the resulting meshsolution
        Default: "ElmerResults"
    file_path : str
        Filename of the results VTU data file
        Default: ""
    store_dict : dict or None
        Dict containing the data names to store
        Default: {}
    """

    label: str = "ElmerResults"
    """Label of the resulting meshsolution"""
    file_path: str = ""
    """Filename of the results VTU data file"""
    store_dict: dict[str, Any] = Field(default_factory=dict)
    """Dict containing the data names to store"""

    _package: ClassVar[str] = "Elmer"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Elmer.ElmerResultsVTU.build_meshsolution
    def build_meshsolution(self) -> MeshSolution:
        """Get the mesh and solution data from an Elmer VTU results file

        Parameters
        ----------
        self : ElmerResultsVTU
            a ElmerResultsVTU object

        Returns
        -------
        meshsol: MeshSolution
            Mesh solution built from the results

        """
        # create meshsolution
        meshsol = MeshSolution(label=self.label)

        # get the mesh
        save_path, fn = os.path.split(self.file_path)
        file_name, file_ext = os.path.splitext(fn)
        if file_ext != ".vtu":
            raise ElmerResultsVTUError(
                "ElmerResultsVTU: Results file must be of type VTU."
            )

        meshvtk = MeshVTK(path=save_path, name=file_name, format="vtu")
        # TODO maybe convert to MeshMat before
        meshsol.mesh = meshvtk

        # get the solution data on the mesh
        meshsolvtu = read(self.file_path)
        pt_data = meshsolvtu.point_data  # point_data is of type dict

        # setup axes
        indices = np.arange(meshsolvtu.points.shape[0])
        Indices = Data1D(name="indice", values=indices, is_components=True)

        # store only data from store dict if available
        comp_ext = ["x", "y", "z"]

        for key, value in pt_data.items():
            # check if value should be stored
            if key in self.store_dict.keys():
                siz = value.shape[1]
                # only regard max. 3 components
                if siz > 3:
                    get_logger(self).warning(
                        f'ElmerResultsVTU.build_meshsolution(): size of data "{key}" > 3'
                        + " - "
                        + "Data will be truncated."
                    )
                    siz = 3

                components = []
                comp_name = []

                # loop though components
                for i in range(siz):
                    # setup name, symbol and component name extension
                    if siz == 1:
                        ext = ""
                    else:
                        ext = comp_ext[i]

                    # setup data object
                    data = DataTime(
                        name=self.store_dict[key]["name"] + " " + ext,
                        unit=self.store_dict[key]["unit"],
                        symbol=self.store_dict[key]["symbol"] + ext,
                        axes=[Indices],
                        values=value[:, i],
                        normalizations={
                            "ref": NormRef(ref=self.store_dict[key]["norm"])
                        },
                    )
                    components.append(data)
                    comp_name.append("comp_" + ext)

                # setup solution depending on number of field components
                if siz == 1:
                    field = components[0]
                    solution = SolutionData(
                        field=field,
                        type_element="point",
                        label=self.store_dict[key]["symbol"],
                    )

                    label = self.store_dict[key]["symbol"]
                    meshsol.add_solution(solution=solution, label=label)

                else:
                    comps: dict[str, DataND] = {}
                    for i in range(siz):
                        comps[comp_name[i]] = components[i]
                    field = VectorField(
                        name=self.store_dict[key]["name"],
                        symbol=self.store_dict[key]["symbol"],
                        components=comps,
                    )
                    solution = SolutionVector(
                        field=field,
                        type_element="point",
                        label=self.store_dict[key]["symbol"],
                    )
                    label = self.store_dict[key]["symbol"]

                    meshsol.add_solution(solution=solution, label=label)

        return meshsol
