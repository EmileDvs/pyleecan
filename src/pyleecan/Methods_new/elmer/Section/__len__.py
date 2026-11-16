def __len__(self) -> int:
    """Method to behave like a dict and the number of keys"""
    return self._statements.__len__()
