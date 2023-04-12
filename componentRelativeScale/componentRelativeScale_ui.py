#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os
import os.path

from maya import cmds as mc
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from PySide2 import QtCore, QtWidgets, QtUiTools
# from Qt import QtWidgets, QtUiTools, QtCore

def get_path(*args):
    """Get the full path of a file or folder in the same directory as the script."""
    # Get the directory path of the script
    dir_path = os.path.dirname(os.path.abspath(__file__))
    # Join the directory path with the input arguments
    return os.path.join(dir_path, *args)

class ScaleComponentsUI(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    """This class provides a user interface to create a polygon and scale it based on the user's inputs."""

    #: bool: Whether to calculate the center of the polygon using its bounding box (True) or its polygon (False).
    _calculate_bbox_center = True

    #: float: The scale factor to apply to the X axis.
    _x_value = 1.0

    #: float: The scale factor to apply to the Y axis.
    _y_value = 1.0

    #: float: The scale factor to apply to the Z axis.
    _z_value = 1.0

    def __init__(self, parent=None):
        """
        Initializes the ScaleComponentsUI class and creates a UI with various components such as sliders and checkboxes.

        :param parent: parent widget
        """
        super(self.__class__, self).__init__(parent=parent)

        # If there is a parent widget, close any existing instances of this class
        if self.parent():
            child_list = self.parent().children()
            for c in child_list:
                if self.__class__ == c.__class__:
                    c.close()

        # Set window title and load UI from file
        self.setWindowTitle("componentRelativeScale")
        ui_filename = get_path("componentRelativeScale_ui.ui")
        self.ui = self.initUI(ui_filename)

        # Set layout and add UI to it
        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().addWidget(self.ui)

        # Connect signals to slots
        self.ui.doubleSpinBox_X.valueChanged.connect(self.reloadValue)
        self.ui.doubleSpinBox_Y.valueChanged.connect(self.reloadValue)
        self.ui.doubleSpinBox_Z.valueChanged.connect(self.reloadValue)
        self.ui.isCalcCenterByBox.stateChanged.connect(self.reloadIsCalcCenterByBox)
        self.ui.scaleButton.clicked.connect(self.scaleFromPivot)

    def init_ui(self, ui_filename):
        """Creates the user interface with various components such as sliders and checkboxes."""
        ui_loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_filename)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = ui_loader.load(ui_file, parentWidget=self)
        ui_file.close()
        return ui

    def reload_values(self):
        """Updates the scale values of the UI based on the given input values."""
        self._x_value = self.ui.doubleSpinBox_X.value()
        self._y_value = self.ui.doubleSpinBox_Y.value()
        self._z_value = self.ui.doubleSpinBox_Z.value()

    def reload_is_calculate_bbox_center(self):
        """Updates the checkbox state of the UI based on the given input value."""
        self._calculate_bbox_center = self.ui.isCalcCenterByBox.isChecked()

    def calculate_polygon_center(self, pos_list):
        """Calculates the center of the polygon based on the given vertex positions."""
        ans = [0, 0, 0]
        for pos in pos_list:
            ans[0] += pos[0]
            ans[1] += pos[1]
            ans[2] += pos[2]
        ans[0] /= len(pos_list)
        ans[1] /= len(pos_list)
        ans[2] /= len(pos_list)
        return ans

    def calculate_bbox_center(self, pos_list):
        """Calculates the center of the bounding box of the vertex positions."""
        _min = [pos_list[0][0], pos_list[0][1], pos_list[0][2]]
        _max = [pos_list[0][0], pos_list[0][1], pos_list[0][2]]
        for pos in pos_list:
            for i in range(3):
                if pos[i] < _min[i]:
                    _min[i] = pos[i]
                if pos[i] > _max[i]:
                    _max[i] = pos[i]
        ans = [(_max[0] + _min[0]) / 2, (_max[1] + _min[1]) / 2, (_max[2] + _min[2]) / 2]
        return ans

    def get_selection_pivot(self):
        """
        Calculates the center point of the selected vertices, edges, or faces.

        Returns:
            The calculated center point as a list of 3 floats representing the x, y, and z coordinates.

        Raises:
            ValueError: If nothing is selected, or if the selection is invalid.
        """
        # Get the current selection
        selected_items = mc.ls(long=True, selection=True)
        # Raise an exception if nothing is selected
        if not selected_items:
            raise ValueError("Nothing is selected.")
        # Determine the type of selection (vertex, edge, or face)
        selection_type_map = {".vtx": 31, ".e": 32, ".f": 34}
        selection_type = None
        for key in selection_type_map:
            if key in selected_items[0]:
                selection_type = key
                break
        if selection_type is None:
            raise ValueError("Invalid selection. You can only select 'vtx', 'edge', or 'face'.")
        selection_mask = selection_type_map[selection_type]
        selected_items = mc.filterExpand(selected_items, selectionMask=selection_mask)
        # Create a list of the positions of the selected vertices, edges, or faces
        pos_list = []
        for name in selected_items:
            # Get the world space position of each selected item
            item_positions = mc.xform(name, q=True, worldSpace=True, translation=True)
            for pos in item_positions:
                # Add each position in the format of [x, y, z] to the pos_list
                pos_list.append([pos[0], pos[1], pos[2]])
        # Calculate the center point
        center = None
        if self.calculate_bbox_center:
            center = self.calculate_bbox_center(pos_list)
        else:
            center = self.calculate_polygon_center(pos_list)
        # Return the center point
        return center

    def scale_from_selection_pivot(self):
        """
        Scales the polygon based on the given scale values and the center point of the selected vertices, edges, or faces.

        Raises:
            ValueError: If any of the scale values are within 1e-6 of 1.0.
        """
        # Get the center point of the selection
        pivot_center = self.get_selection_pivot()
        # If no valid center point is found, exit the method
        if pivot_center is None:
            return
        # If any of the scale values are within 1e-6 of 1.0, raise a ValueError
        epsilon = 1e-6
        if abs(self.x_scale - 1.0) < epsilon or abs(self.y_scale - 1.0) < epsilon or abs(self.z_scale - 1.0) < epsilon:
            raise ValueError("Scale values must not be within 1e-6 of 1.0.")
        # Apply the scale transformation using Maya's built-in scale function
        mc.undoInfo(openChunk=True)
        mc.scale(self.x_scale, self.y_scale, self.z_scale, pivot=pivot_center, relative=True)
        mc.undoInfo(closeChunk=True)

def main():
    try:
        win = ScaleComponentsUI()
        win.show()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()