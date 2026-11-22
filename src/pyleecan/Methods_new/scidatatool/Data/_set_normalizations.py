import numpy as np

from ....classes_common.check import check_var
from ....Classes_new._import import import_class


def _set_normalizations(self, value) -> None:
    """setter of normalizations"""
    if type(value) is dict:
        for key, obj in value.items():
            if type(obj) is dict:
                class_obj = import_class(obj.get('__class__'), 'normalizations')
                value[key] = class_obj(init_dict=obj)
            elif isinstance(obj, (float, int, np.int32, np.int64, np.float32, np.float64)):
                # Local import: avoids circular imports
                from ....Classes_new.scidatatool.norm_ref import NormRef as Norm_ref
                value[key] = Norm_ref(ref=obj)
            elif isinstance(obj, (np.ndarray, list)):
                # Local import: avoids circular imports
                from ....Classes_new.scidatatool.norm_vector import NormVector as Norm_vector
                value[key] = Norm_vector(vector=obj)
    if type(value) is int and value == -1:
        value = dict()
    check_var("normalizations", value, "{Normalization}")
    self.normalizations = value
