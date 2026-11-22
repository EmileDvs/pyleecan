"""File generated according to PCondType22/gen_list.json and the class
information (ClassInfo): limits and help of the widgets.
WARNING! All changes made in this file will be lost!
"""
from .Ui_PCondType22 import Ui_PCondType22


class Gen_PCondType22(Ui_PCondType22):
    def setupUi(self, PCondType22):
        """Set the widget limits and help texts (class information)"""
        Ui_PCondType22.setupUi(self, PCondType22)
        # Setup of w_mat
        txt = self.tr('Material of the conductor')
        self.w_mat.setWhatsThis(txt)
        self.w_mat.setToolTip(txt)
