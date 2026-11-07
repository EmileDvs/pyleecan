# Experimental dataclass generated from Generator/ClassesRef/Mesh/Interpolation/ScalarProductL2.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .scalar_product import ScalarProduct


@dataclass(eq=False)
class ScalarProductL2(ScalarProduct):
    """Store shape functions definition in the reference element

    Attributes
    ----------
    """

    # Inlined from Methods.Mesh.ScalarProductL2.scalar_product
    def scalar_product(self, funca, funcb, detJ, weights, nb_gauss_points):
        """Scalar product of shape functions with L2 gauss integration

        Parameters
        ----------
        self : ScalarProductL2
            a ScalarProductL2 object
        funca : ndarray
            coordinates of the element
        nba : ndarray
            coordinates of a point
        funcb : ndarray
            coordinates of the element
        nbb : ndarray
            coordinates of a point
        detJ : ndarray
            jacobian determinant evaluated for each gauss point
        weights : ndarray
            gauss weights
        nb_gauss_points : int
            number of gauss points

        Returns
        -------
        l2_scal : ndarray
            a L2 scalar product
        """

        func_a_w_dJ = np.zeros(funca.shape)
        for i in range(nb_gauss_points):
            func_a_w_dJ[i, :] = funca[i, :] * weights[i] * detJ[i]

        l2_scal_mat = np.squeeze(np.tensordot(func_a_w_dJ, funcb, axes=([0], [0])))

        return l2_scal_mat
