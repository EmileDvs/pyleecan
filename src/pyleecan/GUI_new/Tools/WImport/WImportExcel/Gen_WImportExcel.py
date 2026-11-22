"""File generated according to WImportExcel/gen_list.json and the class
information (ClassInfo): limits and help of the widgets.
WARNING! All changes made in this file will be lost!
"""
from .Ui_WImportExcel import Ui_WImportExcel


class Gen_WImportExcel(Ui_WImportExcel):
    def setupUi(self, WImportExcel):
        """Set the widget limits and help texts (class information)"""
        Ui_WImportExcel.setupUi(self, WImportExcel)
        # Setup of in_range
        txt = self.tr('list of Excel column letters and column ranges (e.g. "A:E" or "A,C,E:F")')
        self.in_range.setWhatsThis(txt)
        self.in_range.setToolTip(txt)

        # Setup of le_range
        txt = self.tr('list of Excel column letters and column ranges (e.g. "A:E" or "A,C,E:F")')
        self.le_range.setWhatsThis(txt)
        self.le_range.setToolTip(txt)
