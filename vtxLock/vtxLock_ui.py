#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import os.path

from maya import cmds
from maya import OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin
from PySide2 import QtCore, QtGui, QtWidgets, QtUiTools
from shiboken2 import wrapInstance 


def this_dir(*args):
    """このスクリプトと同じフォルダからの相対パスをフルパスに変換して返す"""
    dir_path = os.path.dirname(__file__.decode(u"cp932"))
    return os.path.join(dir_path, *args)


class CreatePolygonUI(MayaQWidgetBaseMixin, QtWidgets.QWidget):    
    def __init__(self, *args, **kwargs):        
        super(CreatePolygonUI, self).__init__(*args, **kwargs)

        # すでにUIが出来てる場合は削除する #
        # mayaのMainWindowの子Windowを取得
        if self.parent():
            child_list = self.parent().children()
            for c in child_list:
                # 自分と同じ名前のUIのクラスオブジェクトが存在してたらCloseする
                if self.__class__.__name__ == c.__class__.__name__:
                    c.close()
        # ------------------------ #

        # ウインドウのタイトルを指定する
        self.setWindowTitle("vtxLock")

        # uiファイルからウィジェットを作成
        ui_filename = this_dir("vtxLock_ui.ui")  # uiファイル名を指定する
        self.ui = self.initUI(ui_filename)

        # ウインドウのサイズに追従するようにレイアウトを作成
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.addWidget(self.ui)

        # ウィジェットのシグナルに関数を紐づける
        self.ui.button_toggle.clicked.connect(self.toggle)
        self.ui.button_on.clicked.connect(self.on)
        self.ui.button_off.clicked.connect(self.off)

    def initUI(self, ui_filename):
        ui_loader = QtUiTools.QUiLoader()        
        ui_file = QtCore.QFile(ui_filename)        
        ui_file.open(QtCore.QFile.ReadOnly)        
        ui = ui_loader.load(ui_file, parentWidget=self)        
        ui_file.close()
        return ui

    def toggle(self):
        selVtxList = cmds.ls(sl=True, flatten=True, type="float3")
        cmds.undoInfo(openChunk=True)
        for selVtx in selVtxList:
            cmds.setAttr(selVtx + ".px", lock = not (cmds.getAttr(selVtx + ".px", lock=True)))
            cmds.setAttr(selVtx + ".py", lock = not (cmds.getAttr(selVtx + ".py", lock=True)))
            cmds.setAttr(selVtx + ".pz", lock = not (cmds.getAttr(selVtx + ".pz", lock=True)))
        cmds.undoInfo(closeChunk=True)

    def on(self):
        selVtxList = cmds.ls(sl=True, flatten=True, type="float3")
        cmds.undoInfo(openChunk=True)
        for selVtx in selVtxList:
            cmds.setAttr(selVtx + ".px", lock = True)
            cmds.setAttr(selVtx + ".py", lock = True)
            cmds.setAttr(selVtx + ".pz", lock = True)
        cmds.undoInfo(closeChunk=True)

    def off(self):
        selVtxList = cmds.ls(sl=True, flatten=True, type="float3")
        cmds.undoInfo(openChunk=True)
        for selVtx in selVtxList:
            cmds.setAttr(selVtx + ".px", lock = False)
            cmds.setAttr(selVtx + ".py", lock = False)
            cmds.setAttr(selVtx + ".pz", lock = False)
        cmds.undoInfo(closeChunk=True)

def main():
    win = CreatePolygonUI()
    win.show()