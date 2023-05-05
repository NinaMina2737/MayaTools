#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from abc import abstractmethod

from maya import cmds
from PySide2.QtWidgets import *
from PySide2 import QtCore

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 270

SCENE_SETTING = "Scene Setting"
REFERENCE_FILE = "Reference File"
TEXTURE = "Texture"
MESH = "Mesh"
CHARACTER = "Character"
ANIMATION = "Animation"
CHECKLIST = {
    SCENE_SETTING : [
        {"単位がCM" : cmds.polyCube},
        {"角度が度" : cmds.polyCube},
        {"FPSが30fps" : cmds.polyCube},
        {"カラーマネジメントが無効" : cmds.polyCube},
    ],

    REFERENCE_FILE : [
        {"壊れたリファレンス" : cmds.polySphere},
        {"存在しないリファレンスファイル" : cmds.polySphere},
        {"リファレンスファイルのパス" : cmds.polySphere},
    ],

    TEXTURE : [
        {"存在しないテクスチャファイル" : cmds.polyCone},
        {"テクスチャファイルのサイズ" : cmds.polyCylinder},
        {"テクスチャファイルのパス" : cmds.polyCylinder},
    ],

    MESH : [
        {"フェイスの重複" : cmds.polyDisc},
        {"空のUVセット" : cmds.polyDisc},
        {"UVセットの構造" : cmds.polyDisc},
        {"共有可能な法線" : cmds.polyDisc},
        {"無効なメッシュノード" : cmds.polyDisc},
        {"多角形ポリゴン" : cmds.polyDisc},
    ],

    CHARACTER : [
        {"指定数のジョイントへの割り振り" : cmds.polyPyramid},
        {"ウェイトの合計が1.0" : cmds.polyPyramid},
        {"スキンクラスターの設定" : cmds.polyPyramid},
        {"セグメントスケール補正が無効" : cmds.polyPyramid},
    ],

    ANIMATION : [
        {"ロックされている頂点" : cmds.polyTorus},
        {"フリーズされていないトランスフォーム" : cmds.polyTorus},
        {"ヒストリが残っているノード" : cmds.polyTorus},
        {"コンストレイントが使われているジョイント" : cmds.polyTorus},
    ],
}
SHOW_ORDER = [
    SCENE_SETTING,
    REFERENCE_FILE,
    TEXTURE,
    MESH,
    CHARACTER,
    ANIMATION,
]

# class Tester():
#     def __init__(self, name):
#         self.name = name

#     @abstractmethod
#     def exec(self):
#         """execute"""
#         pass

class MyWindow(QMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super(MyWindow, self).__init__(parent, *args, **kwargs)
        self.initUI()

    def initUI(self):
        """initialize UI"""
        # set geometry(x, y, width, height)
        self.setGeometry(500, 300, WINDOW_WIDTH, WINDOW_HEIGHT)
        # set minimum size(width, height)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        # set title of widow
        self.setWindowTitle("MyValidator")

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

        # checklist groupBoxes
        checklist_gBoxes = []
        # make group box of checklist from list already made
        for item in SHOW_ORDER:
            checklist_gBoxes.append(self.makeCheckGroupFromKey(item))

        # make vertical box layout for checklist
        checklist_vbl = QVBoxLayout()
        # add checklist group boxes to checklist layout
        for group in checklist_gBoxes:
            # add group box widget to the layout
            checklist_vbl.addWidget(group)

        # make widget for checklist layout
        checklist_widget = QWidget(self)
        # set layout to the widget
        checklist_widget.setLayout(checklist_vbl)

        # make scroll area
        checklist_scrollArea = QScrollArea()
        # make scroll area resizable
        checklist_scrollArea.setWidgetResizable(True)
        # set checklist widget to the scroll area
        checklist_scrollArea.setWidget(checklist_widget)

        # make vertical box layout for main
        main_vbl = QVBoxLayout()
        # add scroll area of checklist to main layout
        main_vbl.addWidget(checklist_scrollArea)

        # make button to run validation
        validate_button = QPushButton("Validate")
        # connect action to validate function
        # validate_button.clicked.connect()

        # make button to close the window
        exit_button = QPushButton("Exit")
        # connect action to close function inherited from parent
        exit_button.clicked.connect(self.close)

        # add buttons
        main_vbl.addWidget(validate_button)
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

    def makeCheckGroupFromKey(self, key):
        """make vertical box layout as checklist from key
        Return: QGroupBox"""
        # make vertical layout
        vBoxLayout = QVBoxLayout()
        # register check items to layout
        for item in CHECKLIST[key]:
            # get text for label
            text = item.keys()[0]
            # make checkbox with text
            checkbox = QCheckBox(text)
            # add to layout
            vBoxLayout.addWidget(checkbox)
        # make grouped box
        groupBox = QGroupBox(key)
        # make grouped box checkable
        groupBox.setCheckable(True)
        # set the layout to the grouped box
        groupBox.setLayout(vBoxLayout)
        return groupBox

def main():
    app = QApplication.instance()
    window = MyWindow()
    window.show()
    sys.exit()
    app.exec_()

if __name__ == '__main__':
    main()
