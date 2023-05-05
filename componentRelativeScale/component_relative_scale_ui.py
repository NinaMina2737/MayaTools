#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from PySide2 import QtCore, QtWidgets

import component_relative_scale as crs
reload(crs)

class ScaleComponentsUI(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    """
    A UI for scaling components relative to their center or bounding box.

    Attributes:
        scale_x_spinbox (QtWidgets.QDoubleSpinBox): The spinbox for the X scale.
        scale_y_spinbox (QtWidgets.QDoubleSpinBox): The spinbox for the Y scale.
        scale_z_spinbox (QtWidgets.QDoubleSpinBox): The spinbox for the Z scale.
        is_bbox_checkbox (QtWidgets.QCheckBox): The checkbox for using the bounding box scale.
        scale_button (QtWidgets.QPushButton): The button for executing the scale command.
    """
    def __init__(self):
        """
        Initializes the class.
        """
        super(self.__class__, self).__init__()
        self.setWindowTitle("Component Relative Scale")
        self.create_widget()
        self.create_layout()

    def create_widget(self):
        """
        Creates the widgets for the UI.
        """
        range_min = 0.0001
        range_max = 1000.0
        single_step = 0.01
        default_value = 1.0
        default_is_bbox = True

        self.scale_x_spinbox = QtWidgets.QDoubleSpinBox()
        self.scale_x_spinbox.setRange(range_min, range_max)
        self.scale_x_spinbox.setSingleStep(single_step)
        self.scale_x_spinbox.setValue(default_value)

        self.scale_y_spinbox = QtWidgets.QDoubleSpinBox()
        self.scale_y_spinbox.setRange(range_min, range_max)
        self.scale_y_spinbox.setSingleStep(single_step)
        self.scale_y_spinbox.setValue(default_value)

        self.scale_z_spinbox = QtWidgets.QDoubleSpinBox()
        self.scale_z_spinbox.setRange(range_min, range_max)
        self.scale_z_spinbox.setSingleStep(single_step)
        self.scale_z_spinbox.setValue(default_value)

        self.is_bbox_checkbox = QtWidgets.QCheckBox("Use bounding box scale")
        self.is_bbox_checkbox.setChecked(default_is_bbox)

        self.scale_button = QtWidgets.QPushButton("Scale")
        self.scale_button.clicked.connect(self.on_scale_button_clicked)

    def create_layout(self):
        """
        Creates the layout for the UI.
        """
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(QtWidgets.QLabel("Scale X:"))
        main_layout.addWidget(self.scale_x_spinbox)
        main_layout.addWidget(QtWidgets.QLabel("Scale Y:"))
        main_layout.addWidget(self.scale_y_spinbox)
        main_layout.addWidget(QtWidgets.QLabel("Scale Z:"))
        main_layout.addWidget(self.scale_z_spinbox)

        main_layout.addWidget(self.is_bbox_checkbox)
        main_layout.addWidget(self.scale_button)
        self.setLayout(main_layout)

    def on_scale_button_clicked(self):
        """
        Executes the scale command.
        """
        x_scale = self.scale_x_spinbox.value()
        y_scale = self.scale_y_spinbox.value()
        z_scale = self.scale_z_spinbox.value()
        is_bbox = self.is_bbox_checkbox.isChecked()
        crs.execute(x_scale, y_scale, z_scale, is_bbox)

def execute():
    """
    Executes the UI.

    Raises:
        Exception: An error occurred.
    """
    try:
        # Check if the window already exists
        if cmds.window("joint_symmetry_window", exists=True):
            cmds.deleteUI("joint_symmetry_window")

        # Create the window
        window = ScaleComponentsUI()
        window.show()
    except Exception as e:
        # Print the error message
        cmds.warning("An error occurred: {}".format(str(e)))

if __name__ == "__main__":
    execute()
