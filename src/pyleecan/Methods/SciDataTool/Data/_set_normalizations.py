from numpy import float32, float64, int32, int64, ndarray

from ....Classes._check import check_var
from ....Functions.Load.import_class import import_class


def _set_normalizations(self, value):
    """setter of normalizations"""
    if type(value) is dict:
        for key, obj in value.items():
            if type(obj) is dict:
                class_obj = import_class(
                    "pyleecan.Classes", obj.get("__class__"), "normalizations"
                )
                value[key] = class_obj(init_dict=obj)
            elif isinstance(obj, (float, int, int32, int64, float32, float64)):
                Norm_ref = import_class(
                    "pyleecan.Classes", "Norm_ref", "normalizations"
                )
                value[key] = Norm_ref(ref=obj)
            elif isinstance(obj, (ndarray, list)):
                Norm_vector = import_class(
                    "pyleecan.Classes", "Norm_vector", "normalizations"
                )
                value[key] = Norm_vector(vector=obj)
    if type(value) is int and value == -1:
        value = dict()
    check_var("normalizations", value, "{Normalization}")
    self._normalizations = value
