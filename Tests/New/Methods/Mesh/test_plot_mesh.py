# -*- coding: utf-8 -*-
from os.path import join

import numpy as np
import pytest

from backend_classes.mesh.element_mat import ElementMat
from backend_classes.mesh.mesh_mat import MeshMat
from backend_classes.mesh.mesh_solution import MeshSolution
from backend_classes.mesh.node_mat import NodeMat
from Tests.New._test_paths import save_plot_path as save_path


@pytest.mark.MeshSol
def test_plot_mesh():
    mesh = MeshMat(dimension=3)
    mesh.node = NodeMat()
    mesh.node.add_node([0, 0, 0])
    mesh.node.add_node([0, 1, 0])
    mesh.node.add_node([1, 0, 0])
    mesh.node.add_node([1, 1, 0])
    mesh.node.add_node([2, 1, 0])

    mesh.element_dict["triangle"] = ElementMat(nb_node_per_element=3)
    mesh.add_element([0, 1, 2], "triangle")
    mesh.add_element([1, 2, 3], "triangle")
    mesh.add_element([2, 3, 4], "triangle")

    MSol = MeshSolution(mesh=mesh)

    MSol.plot_mesh(is_show_fig=False, save_path=save_path + "/plot_mesh.png")


if __name__ == "__main__":
    test_plot_mesh()
