"""File generated according to DBore/gen_list.json and the class
information (ClassInfo): limits and help of the widgets.
WARNING! All changes made in this file will be lost!
"""
from .Ui_DBore import Ui_DBore


class Gen_DBore(Ui_DBore):
    def setupUi(self, DBore):
        """Set the widget limits and help texts (class information)"""
        Ui_DBore.setupUi(self, DBore)
        # Setup of in_alpha
        txt = self.tr('Angular offset for the bore shape')
        self.in_alpha.setWhatsThis(txt)
        self.in_alpha.setToolTip(txt)

        # Setup of lf_alpha
        txt = self.tr('Angular offset for the bore shape')
        self.lf_alpha.setWhatsThis(txt)
        self.lf_alpha.setToolTip(txt)
