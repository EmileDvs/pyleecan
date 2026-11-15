from ..Slot import SlotCheckError


class SC_WHCheckError(SlotCheckError):
    """Raised when a SlotCirc has self.H0 < self.W0/2"""

    pass
