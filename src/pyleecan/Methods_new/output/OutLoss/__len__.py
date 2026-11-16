def __len__(self) -> int:
    """Method to behave like a dict and iterate in the object"""
    return len(self.loss_dict)
