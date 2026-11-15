import numpy as np


def get_data(self):
    """Generate the sinus vector

    Parameters
    ----------
    self : ImportGenVectSin
        An ImportGenVectSin object

    Returns
    -------
    vect: ndarray
        The generated sinus vector

    """

    time = np.linspace(start=0, stop=self.Tf, num=self.N, endpoint=False)

    vect = self.A * np.sin(2 * np.pi * self.f * time + self.Phi)
    return self.edit_matrix(vect)
