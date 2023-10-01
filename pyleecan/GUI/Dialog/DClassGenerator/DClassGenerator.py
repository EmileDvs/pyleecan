from os.path import basename, join, dirname, isfile, isdir
import os
from logging import getLogger
from ....Functions.GUI.log_error import log_error
from ....loggers import GUI_LOG_NAME
from PySide2.QtCore import Qt, Signal, QDir

from functools import partial

from PySide2.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QWidget,
    QFileSystemModel,
    QLabel,
    QLineEdit,
    QDesktopWidget,
    QAbstractScrollArea,
    QHeaderView,
    QPushButton,
)

import subprocess

from PySide2.QtGui import QColor

from ....Functions.load import load, load_machine_materials
from ..DMachineSetup import mach_index, mach_list
from ..DClassGenerator.Ui_DClassGenerator import Ui_DClassGenerator

# from ..DMachineSetup.SPreview.SPreview import SPreview
# from ..DMachineSetup.SSimu.SSimu import SSimu
from ....definitions import config_dict, DOC_DIR, PACKAGE_NAME, MAIN_DIR

from ....Classes.Machine import Machine
from ...Tools.WPathSelector.WPathSelector import WPathSelector
from ...Tools.FloatEdit import FloatEdit
from ....Generator.read_fct import read_file

# Flag for set the enable property of w_nav (List_Widget)
DISABLE_ITEM = Qt.NoItemFlags
ENABLE_ITEM = Qt.ItemIsSelectable | Qt.ItemIsEnabled

MAX_WIDTH_TREEVIEW = 300

EDITOR_PATH = "C:\\Users\\emile\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
# EDITOR_PATH = "notepad.exe" ;


class DClassGenerator(Ui_DClassGenerator, QWidget):
    """Main windows of the Machine Setup Tools"""

    # Signal to update the simulation
    path_Changed = Signal()
    rejected = Signal()

    def __init__(self, class_gen_path=""):
        """Initialize the class generator GUI

        Parameters
        ----------
        self : DClassGenerator
            a DClassGenerator object
        class_gen_path : str
            Default path for csv class files
        """

        # Build the interface according to the .ui file
        QWidget.__init__(self)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.setupUi(self)

        self.is_save_needed = False
        # self.material_dict = material_dict
        self.last_index = 0  # Index of the last step available

        # Init class dict of current class
        self.current_class_dict = None

        # Saving arguments
        self.class_gen_path = class_gen_path
        if class_gen_path == "":
            self.class_gen_path = DOC_DIR.replace("\\", "/")
        else:
            self.class_gen_path = class_gen_path.replace("\\", "/")

        # Init path selector and disable it for the moment
        self.path_selector = WPathSelector(parent=self)
        self.path_selector.set_path_txt(path=DOC_DIR)
        self.path_selector.setDisabled(True)
        self.path_selector.setHidden(False)
        self.path_selector.in_path.setText("Class generator path")

        # Init treeview
        self.treeView.setMinimumWidth(200)
        self.treeView.setMaximumWidth(MAX_WIDTH_TREEVIEW)
        self.dirModel = QFileSystemModel()
        self.dirModel.setRootPath(self.class_gen_path)
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        self.treeView.setModel(self.dirModel)
        self.treeView.setRootIndex(self.dirModel.index(self.class_gen_path))
        self.treeView.setHeaderHidden(True)
        self.treeView.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        # Get screen size
        sizeObject = QDesktopWidget().screenGeometry(-1)
        max_height = sizeObject.height()
        max_width = sizeObject.width()
        self.setMinimumWidth(max_width)

        # Load csv file to init tables of properties, methods, and metadata
        folder_list = os.listdir(DOC_DIR)
        csv_path = None
        for folder in folder_list:
            file_list = os.listdir(join(DOC_DIR, folder))
            for filename in file_list:
                if len(filename) > 4 and filename[-4:] == ".csv":
                    csv_path = join(DOC_DIR, folder, filename)
                    break
            if csv_path is not None:
                break
        class_dict_init = read_file(csv_path, soft_name=PACKAGE_NAME)

        # Store list of properties for further use
        self.list_prop = list(class_dict_init["properties"][0].keys())

        # Store list of properties for further use
        self.list_meta = [
            val
            for val in list(class_dict_init.keys())
            if val not in ["name", "path", "properties", "methods"]
        ]

        # Init table of properties
        self.table_prop.setMinimumWidth(max_width - MAX_WIDTH_TREEVIEW)
        self.table_prop.setColumnCount(len(self.list_prop))
        self.table_prop.setRowCount(1)
        for col in range(self.table_prop.columnCount()):
            qlabel = QLabel(self.list_prop[col])
            qlabel.setAlignment(Qt.AlignCenter)
            self.table_prop.setCellWidget(0, col, qlabel)
            self.table_prop.cellWidget(0, col).setStyleSheet("background-color: grey")
        self.table_prop.horizontalHeader().hide()
        self.table_prop.verticalHeader().hide()

        # Init table of methods
        self.table_meth.setMinimumWidth(max_width - MAX_WIDTH_TREEVIEW)
        self.table_meth.setColumnCount(3)
        self.table_meth.setRowCount(1)
        qlabel = QLabel("Methods")
        qlabel.setAlignment(Qt.AlignCenter)
        self.table_meth.setCellWidget(0, 0, qlabel)
        self.table_meth.cellWidget(0, 0).setStyleSheet("background-color: grey")
        self.table_meth.horizontalHeader().hide()
        self.table_meth.verticalHeader().hide()

        # Init tables of metadata
        self.table_meta.setMinimumWidth(max_width - MAX_WIDTH_TREEVIEW)
        self.table_meta.setRowCount(1)
        # Loop on rows to write methods each method name and create buttons
        col = 0
        for meta in self.list_meta:
            if (
                isinstance(class_dict_init[meta], list)
                and len(class_dict_init[meta]) > 0
                and isinstance(class_dict_init[meta][0], dict)
            ):
                # dict for constants name / value
                for key in class_dict_init[meta][0].keys():
                    self.table_meta.setColumnCount(col + 1)
                    # Create FloatEdit or QLineEdit depending on parameter type
                    qlabel = QLabel(str(meta + "_" + key))
                    qlabel.setAlignment(Qt.AlignCenter)
                    self.table_meta.setCellWidget(0, col, qlabel)
                    self.table_meta.cellWidget(0, col).setStyleSheet(
                        "background-color: grey"
                    )
                    col += 1
            else:
                # Create QLineEdit
                self.table_meta.setColumnCount(col + 1)
                qlabel = QLabel(str(meta))
                qlabel.setAlignment(Qt.AlignCenter)
                self.table_meta.setCellWidget(0, col, qlabel)
                self.table_meta.cellWidget(0, col).setStyleSheet(
                    "background-color: grey"
                )
                col += 1
        self.table_meta.horizontalHeader().hide()
        self.table_meta.verticalHeader().hide()

        # Connect treeview to methods
        self.treeView.collapsed.connect(self.onItemCollapse)
        self.treeView.expanded.connect(self.onItemExpand)
        self.treeView.clicked.connect(self.update_class)
        self.treeView.customContextMenuRequested.connect(self.openContextMenu)

    def update_class(self, point):
        """Update tables when clicking on a csv files

        Parameters
        ----------
        self : DClassGenerator
            a DClassGenerator object
        point : QModelIndex
            Model index of current selected item in treeview

        """

        # Get parent folder in which the csv file is
        parent = point.parent()

        if self.dirModel.data(parent) == "ClassesRef":
            # Don't do anything if click on module (folder)
            pass
        else:
            if point.column() == 0:
                # User clicked directly on name, extract name
                class_name = self.dirModel.data(point)
            else:
                # User clicked on other properties than name, extract name by using parent
                class_name = self.dirModel.data(parent.child(point.row(), 0))
            # Get module name
            module = self.dirModel.data(parent)

            # Load csv file
            csv_path = DOC_DIR + "/" + module + "/" + class_name
            current_class_dict = read_file(csv_path, soft_name=PACKAGE_NAME)

            # Store current class dict for further use
            self.current_class_dict = current_class_dict

            # Update table of properties
            # Set the number of rows to the number of properties (first row are labels)
            self.table_prop.setRowCount(len(current_class_dict["properties"]) + 1)

            # Loop on rows to write properties
            for row, prop_dict in enumerate(current_class_dict["properties"]):
                # Loop on columns to write parameters associated to each property
                for prop, val in prop_dict.items():
                    # Get property name index
                    col = self.list_prop.index(prop)
                    # Create FloatEdit or QLineEdit depending on parameter type
                    if isinstance(val, (int, float)):
                        self.table_prop.setCellWidget(row + 1, col, FloatEdit(val))
                    else:
                        line_edit = QLineEdit(str(val))
                        line_edit.setAlignment(Qt.AlignLeft)
                        self.table_prop.setCellWidget(row + 1, col, line_edit)
            self.table_prop.resizeColumnsToContents()

            # Update table of methods
            # Set the number of rows to the number of methods (first row are labels)
            self.table_meth.setRowCount(len(current_class_dict["methods"]) + 1)

            # Loop on rows to write methods each method name and create buttons
            folder_path = join(MAIN_DIR, "Methods", module, class_name[:-4])

            # Create Browse button
            b_browse = QPushButton(text="Browse", parent=self.table_meth)
            b_browse.clicked.connect(lambda: self.browseMethod(folder_path))
            b_browse.setEnabled(isdir(folder_path))
            self.table_meth.setCellWidget(0, 1, b_browse)

            for row, meth in enumerate(current_class_dict["methods"]):
                # Write method name
                line_edit = QLineEdit(str(meth))
                line_edit.setAlignment(Qt.AlignLeft)
                self.table_meth.setCellWidget(row + 1, 0, line_edit)
                # Create Open button
                method_path = join(folder_path, meth + ".py")
                b_open = QPushButton(text="Open", parent=self.table_meth)
                # button.clicked.connect(lambda state, x=name: calluser(x))
                b_open.clicked.connect(partial(self.openMethod, method_path))
                b_open.setEnabled(isfile(method_path))
                self.table_meth.setCellWidget(row + 1, 1, b_open)

            self.table_meth.resizeColumnsToContents()

            # Update table of metadata
            # Set the number of rows to the number of metadata (first row are labels)
            self.table_meta.setRowCount(2)

            # Loop metadata and fill tables
            col = 0
            for meta in self.list_meta:
                if (
                    isinstance(current_class_dict[meta], list)
                    and len(current_class_dict[meta]) > 0
                    and isinstance(current_class_dict[meta][0], dict)
                ):
                    # dict for constants name / value
                    for val in current_class_dict[meta][0].values():
                        # Create FloatEdit or QLineEdit depending on parameter type
                        if isinstance(val, (int, float)):
                            self.table_meta.setCellWidget(1, col, FloatEdit(val))
                        else:
                            line_edit = QLineEdit(str(val))
                            line_edit.setAlignment(Qt.AlignLeft)
                            self.table_meta.setCellWidget(1, col, line_edit)
                        col += 1
                else:
                    # Create QLineEdit
                    line_edit = QLineEdit(str(current_class_dict[meta]))
                    line_edit.setAlignment(Qt.AlignLeft)
                    self.table_meta.setCellWidget(1, col, line_edit)
                    col += 1

    def onItemCollapse(self, index):
        """Slot for item collapsed"""
        # dynamic resize
        for ii in range(3):
            self.treeView.resizeColumnToContents(ii)

    def onItemExpand(self, index):
        """Slot for item expand"""
        # dynamic resize
        for ii in range(3):
            self.treeView.resizeColumnToContents(ii)

    def browseMethod(self, folder_path):
        path = os.path.realpath(folder_path)
        if isdir(path):
            os.startfile(path)

    def openMethod(self, method_path):
        if isfile(method_path):
            p = subprocess.Popen([EDITOR_PATH, method_path])

    def openContextMenu(self, point):
        """Generate and open context the menu at the given point position."""

        index = self.treeView.indexAt(point)
        # pos = QtGui.QCursor.pos()

        # if not index.isValid():
        #     return

        # # get the data
        # item = self.model.item(index)
        # obj_info = self.model.get_obj_info(item)

        # # init the menu
        # menu = TreeEditContextMenu(obj_dict=obj_info, parent=self)
        # menu.exec_(pos)

        # self.onSelectionChanged(self.selectionModel.selection())

        print("toto5")

        pass

        # """Generate and open context the menu at the given point position."""
        # index = self.treeView.indexAt(point)
        # pos = QtGui.QCursor.pos()

        # if not index.isValid():
        #     return

        # # get the data
        # item = self.model.item(index)
        # obj_info = self.model.get_obj_info(item)

        # # init the menu
        # menu = TreeEditContextMenu(obj_dict=obj_info, parent=self)
        # menu.exec_(pos)

        # self.onSelectionChanged(self.selectionModel.selection())

        # # Initialize the machine if needed
        # if machine is None:
        #     self.machine = type(mach_list[0]["init_machine"])(
        #         init_dict=mach_list[0]["init_machine"].as_dict()
        #     )

        # self.update_nav()
        # self.set_nav(self.last_index)

        # # Connect save/load button
        # self.nav_step.currentRowChanged.connect(self.set_nav)
        # self.b_save.clicked.connect(self.s_save)
        # self.b_load.clicked.connect(self.s_load)

        # self.qmessagebox_question = None

    # def save_needed(self):
    #     """Set is_save_needed to True"""
    #     self.is_save_needed = True

    # def closeEvent(self, event):
    #     """Display a message before leaving

    #     Parameters
    #     ----------
    #     self : DMachineSetup
    #         A DMachineSetup object
    #     event :
    #         The closing event
    #     """

    #     if self.is_save_needed:
    #         quit_msg = self.tr(
    #             "Unsaved changes will be lost.\nDo you want to save the machine?"
    #         )
    #         reply = QMessageBox.question(
    #             self,
    #             self.tr("Please save before closing"),
    #             quit_msg,
    #             QMessageBox.Yes,
    #             QMessageBox.No,
    #         )
    #         self.qmessagebox_question = reply
    #         if reply == QMessageBox.Yes:
    #             self.s_save()

    # def reject(self):
    #     """ """
    #     self.rejected.emit()
    #     self.close()

    # def s_save(self):
    #     """Slot for saving the current machine to a json file

    #     Parameters
    #     ----------
    #     self : DMachineSetup
    #         A DMachineSetup object
    #     """
    #     # Ask the user to select a .m file to save
    #     if self.machine.name in ["", None]:
    #         save_file_path = QFileDialog.getSaveFileName(
    #             self, self.tr("Save file"), self.machine_path, "Json (*.json)"
    #         )[0]
    #     else:
    #         def_path = join(self.machine_path, self.machine.name + ".json")
    #         save_file_path = QFileDialog.getSaveFileName(
    #             self, self.tr("Save file"), def_path, "Json (*.json)"
    #         )[0]
    #     save_file_path = save_file_path.replace("\\", "/")

    #     # Avoid bug due to user closing the popup witout selecting a file
    #     if save_file_path != "":
    #         # Set the machine name to match the file name
    #         self.machine.name = str(basename(str(save_file_path)))[:-5]
    #         # Save the machine file
    #         getLogger(GUI_LOG_NAME).info(
    #             "Saving " + self.machine.name + " in folder " + dirname(save_file_path)
    #         )
    #         try:
    #             self.machine.save(save_file_path)
    #         except Exception as e:
    #             err_msg = (
    #                 "Error while saving machine " + self.machine.name + ":\n" + str(e)
    #             )
    #             log_error(self, err_msg)
    #             return False
    #         # To update the machine name field (if first page)
    #         self.set_nav(self.nav_step.currentRow())
    #         # Update the machine path to remember the last used folder
    #         self.machine_path = dirname(save_file_path)
    #         # Notify the project GUI that the machine has changed
    #         self.machineChanged.emit()
    #         self.is_save_needed = False
    #         return True
    #     return False

    # def s_save_close(self):
    #     """Signal to save and close

    #     Parameters
    #     ----------
    #     self : DMachineSetup
    #         A DMachineSetup object
    #     """
    #     to_close = self.s_save()
    #     if to_close:
    #         self.close()

    # def s_load(self):
    #     """Slot to load a machine from a .json file (triggered by b_load)

    #     Parameters
    #     ----------
    #     self : DMachineSetup
    #         A DMachineSetup object
    #     """
    #     ### TODO: handle material data, i.e. "connect", set new material, etc.

    #     # Ask the user to select a .json file to load
    #     load_path = str(
    #         QFileDialog.getOpenFileName(
    #             self, self.tr("Load file"), self.machine_path, "Json (*.json)"
    #         )[0]
    #     )
    #     if load_path != "":
    #         try:
    #             # Update the machine path to remember the last used folder
    #             self.machine_path = dirname(load_path)
    #             # Load and check type of instance
    #             machine = load(load_path)
    #             if isinstance(machine, Machine):
    #                 self.machine = machine
    #                 load_machine_materials(self.material_dict, self.machine)
    #             else:
    #                 QMessageBox().critical(
    #                     self,
    #                     self.tr("Error"),
    #                     self.tr("The choosen file is not a machine file."),
    #                 )
    #                 return
    #             self.machineChanged.emit()
    #             self.is_save_needed = False
    #         except Exception as e:
    #             QMessageBox().critical(
    #                 self,
    #                 self.tr("Error"),
    #                 self.tr(
    #                     "The machine file is incorrect:\n",
    #                     "Please keep the \n, another " "message is following this one",
    #                 )
    #                 + type(e).__name__
    #                 + ": "
    #                 + str(e),
    #             )
    #             return
    #         self.update_nav()

    # def update_nav(self, next_step=None):
    #     """Update the nav list to match the step of the current machine"""
    #     mach_dict = mach_list[self.get_machine_index()]
    #     self.nav_step.blockSignals(True)
    #     self.nav_step.clear()
    #     index = 1
    #     for step in mach_dict["start_step"]:
    #         self.nav_step.addItem(" " + str(index) + ": " + step.step_name)
    #         index += 1
    #     for step in mach_dict["stator_step"]:
    #         self.nav_step.addItem(" " + str(index) + ": Stator " + step.step_name)
    #         index += 1
    #     for step in mach_dict["rotor_step"]:
    #         if index < 10:
    #             self.nav_step.addItem(" " + str(index) + ": Rotor " + step.step_name)
    #         else:
    #             self.nav_step.addItem(str(index) + ": Rotor " + step.step_name)
    #         index += 1
    #     # Adding step Machine Summary
    #     if index < 10:
    #         self.nav_step.addItem(" " + str(index) + ": " + SPreview.step_name)
    #     else:
    #         self.nav_step.addItem(str(index) + ": " + SPreview.step_name)
    #     index += 1
    #     # Adding Simulation Step
    #     if index < 10:
    #         self.nav_step.addItem(" " + str(index) + ": " + SSimu.step_name)
    #     else:
    #         self.nav_step.addItem(str(index) + ": " + SSimu.step_name)
    #     # Update GUI and select correct step
    #     self.update_enable_nav()
    #     self.nav_step.blockSignals(False)
    #     if next_step is None:
    #         self.nav_step.setCurrentRow(self.last_index)
    #     else:
    #         self.nav_step.setCurrentRow(next_step)

    # def update_enable_nav(self):
    #     # Load for readibility
    #     nav = self.nav_step
    #     machine = self.machine
    #     mach_dict = mach_list[self.get_machine_index()]
    #     # First we disable all the item in the navigation widget
    #     for ii in range(0, nav.count()):
    #         nav.item(ii).setFlags(DISABLE_ITEM)
    #     # First step is always available
    #     nav.item(0).setFlags(ENABLE_ITEM)
    #     index = 1
    #     # Check the start steps
    #     for step in mach_dict["start_step"]:
    #         if step.check(machine) is not None:
    #             self.last_index = index - 1
    #             return None  # Exit at the first fail
    #         nav.item(index).setFlags(ENABLE_ITEM)
    #         index += 1
    #     # Check the stator steps
    #     for step in mach_dict["stator_step"]:
    #         if step.check(machine.stator) is not None:
    #             self.last_index = index - 1
    #             return None  # Exit at the first fail
    #         nav.item(index).setFlags(ENABLE_ITEM)
    #         index += 1
    #     # Check the rotor steps
    #     for step in mach_dict["rotor_step"]:
    #         if step.check(machine.rotor) is not None:
    #             self.last_index = index - 1
    #             return None  # Exit at the first fail
    #         nav.item(index).setFlags(ENABLE_ITEM)
    #         index += 1
    #     # Enable and select FEMM Simulation
    #     nav.item(index).setFlags(ENABLE_ITEM)
    #     self.last_index = index

    # def get_machine_index(self):
    #     """Get the index corresponding to the current machine in the mach_list"""
    #     # Get the correct machine dictionary
    #     index = mach_index.index(type(self.machine))
    #     if index == -1:
    #         QMessageBox().critical(
    #             self, self.tr("Error"), self.tr("Unknown machine type")
    #         )
    #         self.machine = type(mach_list[0]["init_machine"])(
    #             init_dict=mach_list[0]["init_machine"].as_dict()
    #         )
    #         return self.get_machine_index()
    #     return index

    # def set_nav(self, index):
    #     """Select the current widget according to the current machine type
    #     and the current nav index

    #     Parameters
    #     ----------
    #     self : DMachineSetup
    #         A DMachineSetup object
    #     index : int
    #         Current index of nav_step
    #     """
    #     # Get the step list of the current machine
    #     mach_dict = mach_list[self.get_machine_index()]
    #     step_list = list()
    #     step_list.extend(mach_dict["start_step"])
    #     step_list.extend(mach_dict["stator_step"])
    #     step_list.extend(mach_dict["rotor_step"])
    #     step_list.append(SPreview)
    #     step_list.append(SSimu)
    #     is_stator = "Stator" in self.nav_step.currentItem().text()

    #     # Regenerate the step with the current values
    #     self.w_step.setParent(None)
    #     self.w_step = step_list[index](
    #         machine=self.machine, material_dict=self.material_dict, is_stator=is_stator
    #     )
    #     self.w_step.b_previous.clicked.connect(self.s_previous)
    #     if index != len(step_list) - 1:
    #         self.w_step.b_next.setText(self.tr("Next"))
    #         self.w_step.b_next.clicked.connect(self.s_next)
    #     # else:
    #     #     self.w_step.b_next.setText(self.tr("Save and Close"))
    #     #     self.w_step.b_next.clicked.connect(self.s_save_close)

    #     self.w_step.saveNeeded.connect(self.save_needed)
    #     # Refresh the GUI
    #     self.main_layout.insertWidget(1, self.w_step)

    # def s_next(self):
    #     """Signal to set the next step as accessible (and selected)

    #     Parameters
    #     ----------
    #     self : DMachineSetup
    #         A DMachineSetup object
    #     """
    #     next_index = self.nav_step.currentRow() + 1
    #     mach_dict = mach_list[self.get_machine_index()]

    #     if next_index - 1 < len(mach_dict["start_step"]):
    #         error = self.w_step.check(self.machine)
    #     elif next_index - 1 < len(mach_dict["start_step"]) + len(
    #         mach_dict["stator_step"]
    #     ):
    #         error = self.w_step.check(self.machine.stator)
    #     else:
    #         error = self.w_step.check(self.machine.rotor)

    #     if error is not None:  # An error: display it in a popup
    #         QMessageBox().critical(self, self.tr("Error"), error)
    #     else:  # No error => Go to the next page
    #         self.nav_step.item(next_index).setFlags(ENABLE_ITEM)
    #         self.last_index = next_index
    #         self.nav_step.setCurrentRow(next_index)
    #         # As the current row have changed, set_nav is called

    # def s_previous(self):
    #     """Signal to set the previous page of w_page_stack as accessible (and selected)

    #     Parameters
    #     ----------
    #     self : DMachineSetup
    #         A DMachineSetup object
    #     """
    #     next_index = self.nav_step.currentRow() - 1
    #     self.nav_step.setCurrentRow(next_index)
    #     # As the current row have change, set_nav is called