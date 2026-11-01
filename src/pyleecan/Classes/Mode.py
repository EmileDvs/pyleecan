# File generated according to Generator/ClassesRef/Simulation/Mode.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/Mode"""

from os import linesep
from sys import getsizeof

import numpy as np
from pyleecan.Classes.SolutionMat import SolutionMat
from pyleecan.Classes._check import check_var

from pyleecan.Functions.Structural.conversions import cart2pol, pol2cart
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class Mode(SolutionMat):
    """Structural module: Mode object"""

    VERSION = 1

    # cf Methods.Simulation.Mode.get_shape_pol
    def get_shape_pol(self):
        """Return the mode shape in cartesian coordinates.

        Parameters
        ----------
        self : Mode
            a Mode object

        Returns
        -------
        shape : ndarray
            ndarray of the shape (Nnodes*Ndof)
        """

        if self.shape_pol is not None and self.shape_pol.size != 0:
            return self.shape_pol
        else:
            shape_xyz = self.shape_xyz
            points = self.parent.mesh.get_points()
            return cart2pol(shape_xyz, points)

    # cf Methods.Simulation.Mode.get_shape_xyz
    def get_shape_xyz(self):
        """Return the mode shape in cartesian coordinates.

        Parameters
        ----------
        self : Mode
            a Mode object

        Returns
        -------
        shape : ndarray
            ndarray of the shape (Nnodes*Ndof)
        """

        if self.shape_xyz is not None and self.shape_xyz.size != 0:
            return self.shape_xyz
        else:
            shape_pol = self.shape_pol
            points = self.parent.mesh.get_points()
            return pol2cart(shape_pol, points)

    # cf Methods.Simulation.Mode.plot
    def plot(self, i):
        """Return the pyvista mesh object.

        Parameters
        ----------
        self : Mode
            a Mode object
        i : int
            index of the mode to plot

        Returns
        -------
        mesh : pyvista.core.pointset.StructuredGrid
            a pyvista StructuredGrid object
        """

        radial_shape = self.get_shape_pol()[:, 0]
        clim = [np.min(radial_shape), np.max(radial_shape)]
        self.parent.mesh.plot_contour(
            radial_shape, field_name="Radial displacement", clim=clim
        )

    # cf Methods.Simulation.Mode.plot_animated
    def plot_animated(self, i):
        """Return the pyvista mesh object.

        Parameters
        ----------
        self : Mode
            a Mode object
        i : int
            index of the mode to plot

        Returns
        -------
        mesh : pyvista.core.pointset.StructuredGrid
            a pyvista StructuredGrid object
        """

        radial_shape = self.get_shape_pol()[:, 0]
        shape_xyz = self.get_shape_xyz()
        clim = [np.min(radial_shape), np.max(radial_shape)]
        self.parent.mesh.plot_deformation_animated(
            shape_xyz,
            radial_shape,
            factor=0.05,
            field_name="Radial displacement",
            clim=clim,
        )

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        nat_freq=None,
        order_circ=None,
        order_long=None,
        field=None,
        indice=None,
        axis_name=None,
        axis_size=None,
        type_element="triangle",
        label=None,
        dimension=2,
        unit="",
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "nat_freq" in list(init_dict.keys()):
                nat_freq = init_dict["nat_freq"]
            if "order_circ" in list(init_dict.keys()):
                order_circ = init_dict["order_circ"]
            if "order_long" in list(init_dict.keys()):
                order_long = init_dict["order_long"]
            if "field" in list(init_dict.keys()):
                field = init_dict["field"]
            if "indice" in list(init_dict.keys()):
                indice = init_dict["indice"]
            if "axis_name" in list(init_dict.keys()):
                axis_name = init_dict["axis_name"]
            if "axis_size" in list(init_dict.keys()):
                axis_size = init_dict["axis_size"]
            if "type_element" in list(init_dict.keys()):
                type_element = init_dict["type_element"]
            if "label" in list(init_dict.keys()):
                label = init_dict["label"]
            if "dimension" in list(init_dict.keys()):
                dimension = init_dict["dimension"]
            if "unit" in list(init_dict.keys()):
                unit = init_dict["unit"]
        # Set the properties (value check and convertion are done in setter)
        self.nat_freq = nat_freq
        self.order_circ = order_circ
        self.order_long = order_long
        # Call SolutionMat init
        super(Mode, self).__init__(
            field=field,
            indice=indice,
            axis_name=axis_name,
            axis_size=axis_size,
            type_element=type_element,
            label=label,
            dimension=dimension,
            unit=unit,
        )
        # The class is frozen (in SolutionMat init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Mode_str = ""
        # Get the properties inherited from SolutionMat
        Mode_str += super(Mode, self).__str__()
        Mode_str += "nat_freq = " + str(self.nat_freq) + linesep
        Mode_str += "order_circ = " + str(self.order_circ) + linesep
        Mode_str += "order_long = " + str(self.order_long) + linesep
        return Mode_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from SolutionMat
        if not super(Mode, self).__eq__(other):
            return False
        if other.nat_freq != self.nat_freq:
            return False
        if other.order_circ != self.order_circ:
            return False
        if other.order_long != self.order_long:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from SolutionMat
        diff_list.extend(
            super(Mode, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._nat_freq is not None
            and self._nat_freq is not None
            and np.isnan(other._nat_freq)
            and np.isnan(self._nat_freq)
        ):
            pass
        elif other._nat_freq != self._nat_freq:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._nat_freq)
                    + ", other="
                    + str(other._nat_freq)
                    + ")"
                )
                diff_list.append(name + ".nat_freq" + val_str)
            else:
                diff_list.append(name + ".nat_freq")
        if other._order_circ != self._order_circ:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._order_circ)
                    + ", other="
                    + str(other._order_circ)
                    + ")"
                )
                diff_list.append(name + ".order_circ" + val_str)
            else:
                diff_list.append(name + ".order_circ")
        if other._order_long != self._order_long:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._order_long)
                    + ", other="
                    + str(other._order_long)
                    + ")"
                )
                diff_list.append(name + ".order_long" + val_str)
            else:
                diff_list.append(name + ".order_long")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from SolutionMat
        S += super(Mode, self).__sizeof__()
        S += getsizeof(self.nat_freq)
        S += getsizeof(self.order_circ)
        S += getsizeof(self.order_long)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from SolutionMat
        Mode_dict = super(Mode, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        Mode_dict["nat_freq"] = self.nat_freq
        Mode_dict["order_circ"] = self.order_circ
        Mode_dict["order_long"] = self.order_long
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        Mode_dict["__class__"] = "Mode"
        return Mode_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        nat_freq_val = self.nat_freq
        order_circ_val = self.order_circ
        order_long_val = self.order_long
        if self.field is None:
            field_val = None
        else:
            field_val = self.field.copy()
        if self.indice is None:
            indice_val = None
        else:
            indice_val = self.indice.copy()
        if self.axis_name is None:
            axis_name_val = None
        else:
            axis_name_val = self.axis_name.copy()
        if self.axis_size is None:
            axis_size_val = None
        else:
            axis_size_val = self.axis_size.copy()
        type_element_val = self.type_element
        label_val = self.label
        dimension_val = self.dimension
        unit_val = self.unit
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            nat_freq=nat_freq_val,
            order_circ=order_circ_val,
            order_long=order_long_val,
            field=field_val,
            indice=indice_val,
            axis_name=axis_name_val,
            axis_size=axis_size_val,
            type_element=type_element_val,
            label=label_val,
            dimension=dimension_val,
            unit=unit_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.nat_freq = None
        self.order_circ = None
        self.order_long = None
        # Set to None the properties inherited from SolutionMat
        super(Mode, self)._set_None()

    def _get_nat_freq(self):
        """getter of nat_freq"""
        return self._nat_freq

    def _set_nat_freq(self, value):
        """setter of nat_freq"""
        check_var("nat_freq", value, "float")
        self._nat_freq = value

    nat_freq = property(
        fget=_get_nat_freq,
        fset=_set_nat_freq,
        doc="""Natural frequency of the mode

        :Type: float
        """,
    )

    def _get_order_circ(self):
        """getter of order_circ"""
        return self._order_circ

    def _set_order_circ(self, value):
        """setter of order_circ"""
        check_var("order_circ", value, "int", Vmin=0)
        self._order_circ = value

    order_circ = property(
        fget=_get_order_circ,
        fset=_set_order_circ,
        doc="""Circumferential order

        :Type: int
        :min: 0
        """,
    )

    def _get_order_long(self):
        """getter of order_long"""
        return self._order_long

    def _set_order_long(self, value):
        """setter of order_long"""
        check_var("order_long", value, "int", Vmin=0)
        self._order_long = value

    order_long = property(
        fget=_get_order_long,
        fset=_set_order_long,
        doc="""Longitudinal order

        :Type: int
        :min: 0
        """,
    )
