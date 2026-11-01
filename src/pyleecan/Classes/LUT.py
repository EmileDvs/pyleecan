# File generated according to Generator/ClassesRef/Output/LUT.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Output/LUT"""

from pyleecan.Classes.XOutput import XOutput
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class LUT(XOutput):
    """Abstract class for Look Up Table (LUT)"""

    VERSION = 1

    # cf Methods.Output.LUT.get_eec
    def get_eec(self):
        """Get the Electrical Equivalent Circuit

        Parameters
        ----------
        self : LUT
            a LUT object

        Returns
        ----------
        eec : EEC
            Electrical Equivalent Circuit
        """

        if self.simu is None:
            return None
        if self.simu.elec is None:
            return None
        return self.simu.elec.eec

    # cf Methods.Output.LUT.get_OP_array
    def get_OP_array(self, *arg_list):
        """Get the Operating Point array

        Parameters
        ----------
        self : LUT
            a LUT object

        Returns
        ----------
        OP_array : ndarray
            Operating Point Matrix object
        """

        OPM = self.get_OP_matrix_obj()
        return OPM.get_OP_array(*arg_list)

    # cf Methods.Output.LUT.get_OP_matrix_obj
    def get_OP_matrix_obj(self):
        """Get the Operating Point Matrix

        Parameters
        ----------
        self : LUT
            a LUT object

        Returns
        ----------
        OP_matrix : OPMatrix
            Operating Point Matrix object
        """

        if self.simu is None:
            return None
        var_load = self.simu.get_var_load()
        if var_load is None:
            return None
        return var_load.OP_matrix

    # cf Methods.Output.LUT.get_phase_dir
    def get_phase_dir(self):
        """Return the Rotation direction of the stator phases

        Parameters
        ----------
        self : LUT
            A LUT object

        Returns
        -------
        phase_dir : int
            Rotation direction of the stator phase
        """

        return self.output_list[0].elec.phase_dir

    # cf Methods.Output.LUT.set_default_simulation
    def set_default_simulation(self, machine, OP_matrix=None, name=None):
        """Set the default simulation to compute the LUT

        Parameters
        ----------
        self : LUT
            A LUT object
        machine : Machine
            The machine to use in the simulation
        OP_matrix : OP_matrix/ndarray
            OP_matrix to use for VarLoadCurrent
        name : str
            Name of the simulation
        """

        # Dynamic import to avoid loop
        Simu1 = import_class("pyleecan.Classes", "Simu1")
        InputCurrent = import_class("pyleecan.Classes", "InputCurrent")
        VarLoadCurrent = import_class("pyleecan.Classes", "VarLoadCurrent")
        OPdq = import_class("pyleecan.Classes", "OPdq")
        MagFEMM = import_class("pyleecan.Classes", "MagFEMM")
        PostLUT = import_class("pyleecan.Classes", "PostLUT")

        if name is None:
            name = "comp_LUT_" + machine.name
        simu = Simu1(name=name, machine=machine)

        # Definition of the input
        simu.input = InputCurrent(
            Nt_tot=8 * 12,
            Na_tot=8 * 200,
            OP=OPdq(N0=1000, Id_ref=0, Iq_ref=0),  # Will be overwritten
        )

        # Set varspeed simulation
        simu.var_simu = VarLoadCurrent(
            is_keep_all_output=True,
            stop_if_error=True,
        )
        if OP_matrix is not None:
            simu.var_simu.set_OP_matrix_obj(OP_matrix)

        # Define second simu for FEMM comparison
        simu.mag = MagFEMM(is_periodicity_a=True, is_periodicity_t=True, nb_worker=4)

        # Postprocessing
        simu.var_simu.postproc_list = [PostLUT(is_save_LUT=True)]

        # Set simu in LUT
        self.simu = simu

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        paramexplorer_list=-1,
        output_list=-1,
        xoutput_dict=-1,
        nb_simu=0,
        xoutput_ref=None,
        xoutput_ref_index=None,
        simu=-1,
        path_result="",
        geo=-1,
        elec=-1,
        mag=-1,
        struct=-1,
        post=-1,
        logger_name="Pyleecan.Output",
        force=-1,
        loss=-1,
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
            if "paramexplorer_list" in list(init_dict.keys()):
                paramexplorer_list = init_dict["paramexplorer_list"]
            if "output_list" in list(init_dict.keys()):
                output_list = init_dict["output_list"]
            if "xoutput_dict" in list(init_dict.keys()):
                xoutput_dict = init_dict["xoutput_dict"]
            if "nb_simu" in list(init_dict.keys()):
                nb_simu = init_dict["nb_simu"]
            if "xoutput_ref" in list(init_dict.keys()):
                xoutput_ref = init_dict["xoutput_ref"]
            if "xoutput_ref_index" in list(init_dict.keys()):
                xoutput_ref_index = init_dict["xoutput_ref_index"]
            if "simu" in list(init_dict.keys()):
                simu = init_dict["simu"]
            if "path_result" in list(init_dict.keys()):
                path_result = init_dict["path_result"]
            if "geo" in list(init_dict.keys()):
                geo = init_dict["geo"]
            if "elec" in list(init_dict.keys()):
                elec = init_dict["elec"]
            if "mag" in list(init_dict.keys()):
                mag = init_dict["mag"]
            if "struct" in list(init_dict.keys()):
                struct = init_dict["struct"]
            if "post" in list(init_dict.keys()):
                post = init_dict["post"]
            if "logger_name" in list(init_dict.keys()):
                logger_name = init_dict["logger_name"]
            if "force" in list(init_dict.keys()):
                force = init_dict["force"]
            if "loss" in list(init_dict.keys()):
                loss = init_dict["loss"]
        # Set the properties (value check and convertion are done in setter)
        # Call XOutput init
        super(LUT, self).__init__(
            paramexplorer_list=paramexplorer_list,
            output_list=output_list,
            xoutput_dict=xoutput_dict,
            nb_simu=nb_simu,
            xoutput_ref=xoutput_ref,
            xoutput_ref_index=xoutput_ref_index,
            simu=simu,
            path_result=path_result,
            geo=geo,
            elec=elec,
            mag=mag,
            struct=struct,
            post=post,
            logger_name=logger_name,
            force=force,
            loss=loss,
        )
        # The class is frozen (in XOutput init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LUT_str = ""
        # Get the properties inherited from XOutput
        LUT_str += super(LUT, self).__str__()
        return LUT_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from XOutput
        if not super(LUT, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from XOutput
        diff_list.extend(
            super(LUT, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from XOutput
        S += super(LUT, self).__sizeof__()
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

        # Get the properties inherited from XOutput
        LUT_dict = super(LUT, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LUT_dict["__class__"] = "LUT"
        return LUT_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.paramexplorer_list is None:
            paramexplorer_list_val = None
        else:
            paramexplorer_list_val = list()
            for obj in self.paramexplorer_list:
                paramexplorer_list_val.append(obj.copy())
        if self.output_list is None:
            output_list_val = None
        else:
            output_list_val = list()
            for obj in self.output_list:
                output_list_val.append(obj.copy())
        if self.xoutput_dict is None:
            xoutput_dict_val = None
        else:
            xoutput_dict_val = dict()
            for key, obj in self.xoutput_dict.items():
                xoutput_dict_val[key] = obj.copy()
        nb_simu_val = self.nb_simu
        if self.xoutput_ref is None:
            xoutput_ref_val = None
        else:
            xoutput_ref_val = self.xoutput_ref.copy()
        xoutput_ref_index_val = self.xoutput_ref_index
        if self.simu is None:
            simu_val = None
        else:
            simu_val = self.simu.copy()
        path_result_val = self.path_result
        if self.geo is None:
            geo_val = None
        else:
            geo_val = self.geo.copy()
        if self.elec is None:
            elec_val = None
        else:
            elec_val = self.elec.copy()
        if self.mag is None:
            mag_val = None
        else:
            mag_val = self.mag.copy()
        if self.struct is None:
            struct_val = None
        else:
            struct_val = self.struct.copy()
        if self.post is None:
            post_val = None
        else:
            post_val = self.post.copy()
        logger_name_val = self.logger_name
        if self.force is None:
            force_val = None
        else:
            force_val = self.force.copy()
        if self.loss is None:
            loss_val = None
        else:
            loss_val = self.loss.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            paramexplorer_list=paramexplorer_list_val,
            output_list=output_list_val,
            xoutput_dict=xoutput_dict_val,
            nb_simu=nb_simu_val,
            xoutput_ref=xoutput_ref_val,
            xoutput_ref_index=xoutput_ref_index_val,
            simu=simu_val,
            path_result=path_result_val,
            geo=geo_val,
            elec=elec_val,
            mag=mag_val,
            struct=struct_val,
            post=post_val,
            logger_name=logger_name_val,
            force=force_val,
            loss=loss_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        # Set to None the properties inherited from XOutput
        super(LUT, self)._set_None()
