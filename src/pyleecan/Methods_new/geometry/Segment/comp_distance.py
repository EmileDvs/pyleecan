import numpy as np




def distance_numpy(A, B, P):
    # from: https://gist.github.com/nim65s/5e9902cd67f094ce65b0
    """segment line AB, point P, where each one is an array([x, y])"""
    if all(A == P) or all(B == P):
        return 0
    if np.arccos(np.dot((P - A) / np.linalg.norm(P - A), (B - A) / np.linalg.norm(B - A))) > np.pi / 2:
        return np.linalg.norm(P - A)
    if np.arccos(np.dot((P - B) / np.linalg.norm(P - B), (A - B) / np.linalg.norm(A - B))) > np.pi / 2:
        return np.linalg.norm(P - B)
    return np.linalg.norm(np.cross(A - B, A - P)) / np.linalg.norm(B - A)


def comp_distance(self, Z):
    """Compute the distance of a point to the Segment

    Parameters
    ----------
    self : Segment
        A Segment object
    Z : complex
        Complex coordinate of the point

    Returns
    -------
    D : float
        distance of a point to the Segment
    """

    Z1 = np.array([self.begin.real, self.begin.imag, 0])
    Z2 = np.array([self.end.real, self.end.imag, 0])
    Z3 = np.array([Z.real, Z.imag, 0])
    return distance_numpy(Z1, Z2, Z3)
