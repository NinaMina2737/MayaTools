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

from functools import partial


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
        self.setWindowTitle("renameTool")

        # uiファイルからウィジェットを作成
        ui_filename = this_dir("renameTool_ui.ui")  # uiファイル名を指定する
        self.ui = self.initUI(ui_filename)

        # ウインドウのサイズに追従するようにレイアウトを作成
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.addWidget(self.ui)

        # ウィジェットのシグナルに関数を紐づける
        self.ui.rename_button.clicked.connect(partial(self.renameNode,"rename"))
        self.ui.replace_button.clicked.connect(partial(self.renameNode,"replace"))
        self.ui.add_bos_button.clicked.connect(partial(self.addNameNode,"beginning"))
        self.ui.add_eos_button.clicked.connect(partial(self.addNameNode,"end"))
        self.ui.add_before_button.clicked.connect(partial(self.addNameNode,"before"))
        self.ui.add_after_button.clicked.connect(partial(self.addNameNode,"after"))

    def initUI(self, ui_filename):
        ui_loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_filename)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = ui_loader.load(ui_file, parentWidget=self)
        ui_file.close()
        return ui

    def renameNode(self, mode='rename'):
        cmds.undoInfo(openChunk=True)
        search_text = self.ui.search_text.text()
        user_text = self.ui.user_text.text()
        if (search_text == "" or search_text == None) and mode == 'replace':
            print("検索する文字列を指定してください。")
            return
        if user_text == "" or user_text == None:
            print("置換/削除/追加する文字列を指定してください。")
            return
        nodeList = cmds.ls(sl=True)
        for nodeName in nodeList:
            newName = None
            if mode == 'rename':
                newName = user_text
            elif mode == 'replace':
                newName = nodeName.replace(search_text,user_text)
            if newName == nodeName:
                pass
            else:
                cmds.rename( nodeName, newName )
        cmds.undoInfo(closeChunk=True)

    def addNameNode(self, mode="beginning"):
        cmds.undoInfo(openChunk=True)
        search_text = self.ui.search_text.text()
        user_text = self.ui.user_text.text()
        if (search_text == "" or search_text == None) and (mode == 'before' or mode == 'after'):
            print("検索する文字列を指定してください。")
            return
        if user_text == "" or user_text == None:
            print("置換/削除/追加する文字列を指定してください。")
            return
        nodeList = cmds.ls(sl=True)
        for nodeName in nodeList:
            newName = None
            if mode == 'beginning':
                newName = user_text + nodeName
            elif mode == 'end':
                newName = nodeName + user_text
            elif mode == 'before':
                search_text_index = nodeName.find(search_text)
                newName = nodeName[:search_text_index] + user_text + nodeName[search_text_index:]
            elif mode == 'after':
                search_text_index = nodeName.find(search_text) + len(search_text)
                newName = nodeName[:search_text_index] + user_text + nodeName[search_text_index:]
            if nodeName == newName:
                pass
            else:
                cmds.rename( nodeName, newName )
        cmds.undoInfo(closeChunk=True)

def main():
    win = CreatePolygonUI()
    win.show()