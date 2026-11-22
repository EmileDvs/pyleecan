

def convert_to_UD(self):
    """Convert the hole to HoleUD"""
    # Local import: avoids circular imports
    from ....Classes_new.slot.hole_ud import HoleUD

    surf_list = self.build_geometry()
    magnet_dict = self.get_magnet_dict()
    magnetization_dict = self.comp_magnetization_dict()

    return HoleUD(
        surf_list=surf_list,
        magnet_dict=magnet_dict,
        Zh=self.Zh,
        mat_void=self.mat_void,
        magnetization_dict_offset=magnetization_dict,
    )
