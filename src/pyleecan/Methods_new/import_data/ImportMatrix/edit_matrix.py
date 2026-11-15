# -*- coding: utf-8 -*-

import numpy as np


def edit_matrix(self, matrix):
    """To apply transformation on the matrix

    Parameters
    ----------
    self : ImportMatrix
        An ImportMatrix object
    matrix: ndarray
        The matrix to edit

    Returns
    -------
    matrix: ndarray
        The edited matrix

    """

    if self.is_transpose:
        return np.transpose(matrix)
    return matrix
