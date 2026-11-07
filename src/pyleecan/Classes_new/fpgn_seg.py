# Experimental dataclass generated from Generator/ClassesRef/Mesh/Interpolation/FPGNSeg.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .gauss_point import GaussPoint


@dataclass(eq=False)
class FPGNSeg(GaussPoint):
    """Compute N gauss point for segment elements

    Attributes
    ----------
    nb_gauss_point : int
        Nb of gauss point to be used
        Default: 4
    """

    nb_gauss_point: int = 4
    """Nb of gauss point to be used"""

    # Inlined from Methods.Mesh.FPGNSeg.get_gauss_points
    def get_gauss_points(self):
        """Return the gauss points and weights for Segments"""

        nb_gauss_points = self.nb_gauss_point
        gauss_pts = np.zeros([nb_gauss_points, 2], dtype=float)

        gauss_pts[:, 0] = np.polynomial.legendre.leggauss(nb_gauss_points)[0]

        weights = np.polynomial.legendre.leggauss(nb_gauss_points)[1]

        return gauss_pts, weights, nb_gauss_points
