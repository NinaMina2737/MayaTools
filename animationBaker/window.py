#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

from maya import cmds
from maya.app.general import mayaMixin
from PySide2.QtWidgets import *
from PySide2 import QtCore, QtGui

from animationBaker import bake

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 270

class MyWindow(mayaMixin.MayaQWidgetBaseMixin,QMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super(MyWindow, self).__init__(parent, *args, **kwargs)
        self.startFrame = 1
        self.endFrame = 30
        self.bakeFunction = bake
        self.initUI()

    def initUI(self):
        """initialize UI"""
        # set geometry(x, y, width, height)
        self.setGeometry(500, 300, WINDOW_WIDTH, WINDOW_HEIGHT)
        # set minimum size(width, height)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # set title of widow
        self.setWindowTitle("AnimationBaker")

        # make action to close the window
        exitAction = QAction("Exit", self)
        # make shortcut of the action
        exitAction.setShortcut("Ctrl+W")
        # connect action to close function inherited from parent
        exitAction.triggered.connect(self.close)

        # make menu bar
        menuBar = self.menuBar()
        # make menu named "File" and add this to menu
        fileMenu = menuBar.addMenu("File")
        # add close action to "File" menu
        fileMenu.addAction(exitAction)

        # send message to status bar
        self.sendStatusMessage("Ready")

        # make vertical box layout for main
        main_vbl = QVBoxLayout()

        # make horizontal box layout for input
        startFrame_input_hbl = QHBoxLayout()
        endFrame_input_hbl = QHBoxLayout()

        # make QLabel and QLineEdit to set frames
        startFrame_label = QLabel("Start Frame :")
        startFrame_le = QLineEdit(str(self.startFrame))
        endFrame_label = QLabel("End Frame :")
        endFrame_le = QLineEdit(str(self.endFrame))

        # set a validator to restrict the input to integers
        intValidator = QtGui.QIntValidator()
        startFrame_le.setValidator(intValidator)
        endFrame_le.setValidator(intValidator)

        # add QLabel and QLineEdit to each layout
        startFrame_input_hbl.addWidget(startFrame_label)
        startFrame_input_hbl.addWidget(startFrame_le)
        endFrame_input_hbl.addWidget(endFrame_label)
        endFrame_input_hbl.addWidget(endFrame_le)

        # add each layout to main
        main_vbl.addLayout(startFrame_input_hbl)
        main_vbl.addLayout(endFrame_input_hbl)

        # make button to run validation
        bake_button = QPushButton("Bake")
        # connect action to validate function
        bake_button.clicked.connect(self.bakeFunction)

        # make button to close the window
        exit_button = QPushButton("Exit")
        # connect action to close function inherited from parent
        exit_button.clicked.connect(self.close)

        # add buttons
        main_vbl.addWidget(bake_button)
        main_vbl.addWidget(exit_button)

        # make widget for main layout
        main_widget = QWidget(self)
        # set layout to the widget
        main_widget.setLayout(main_vbl)

        # make main widget to center
        self.setCentralWidget(main_widget)

    def sendStatusMessage(self, message):
        """send massage to status bar"""
        self.statusBar().showMessage(message)

def main():
    app = QApplication.instance()
    window = MyWindow()
    window.show()
    if __name__ == '__main__':
        sys.exit()
        app.exec_()

if __name__ == '__main__':
    main()