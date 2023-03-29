#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import os.path

from maya import cmds as mc
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from PySide2 import QtCore, QtWidgets, QtUiTools


def this_dir(*args):
    """このスクリプトと同じフォルダからの相対パスをフルパスに変換して返す"""
    dir_path = os.path.dirname(__file__.decode(u"cp932"))
    return os.path.join(dir_path, *args)


class CreatePolygonUI(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    isCalcCenterByBox = True
    x_value = 1
    y_value = 1
    z_value = 1
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
        self.setWindowTitle("componentRelativeScale")

        # uiファイルからウィジェットを作成
        ui_filename = this_dir("componentRelativeScale_ui.ui")  # uiファイル名を指定する
        self.ui = self.initUI(ui_filename)

        # ウインドウのサイズに追従するようにレイアウトを作成
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.addWidget(self.ui)

        # ウィジェットのシグナルに関数を紐づける
        self.ui.doubleSpinBox_X.editingFinished.connect(self.reloadValue)
        self.ui.doubleSpinBox_Y.editingFinished.connect(self.reloadValue)
        self.ui.doubleSpinBox_Z.editingFinished.connect(self.reloadValue)
        self.ui.isCalcCenterByBox.stateChanged.connect(self.reloadIsCalcCenterByBox)
        self.ui.scaleButton.clicked.connect(self.scaleFromPivot)

    def initUI(self, ui_filename):
        ui_loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_filename)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = ui_loader.load(ui_file, parentWidget=self)
        ui_file.close()
        return ui

    def reloadValue(self):
        self.x_value = float(self.ui.doubleSpinBox_X.text())
        self.y_value = float(self.ui.doubleSpinBox_Y.text())
        self.z_value = float(self.ui.doubleSpinBox_Z.text())

    def reloadIsCalcCenterByBox(self):
        if self.ui.isCalcCenterByBox.isChecked():
            self.isCalcCenterByBox = True
        else:
            self.isCalcCenterByBox = False

    def calcCenter(self,posList):
        ans = [0,0,0]
        for pos in posList:
            ans[0] += pos[0]
            ans[1] += pos[1]
            ans[2] += pos[2]
        ans[0] /= len(posList)
        ans[1] /= len(posList)
        ans[2] /= len(posList)
        return ans

    def calcCenterByBox(self,posList):
        _min = [posList[0][0],posList[0][1],posList[0][2]]
        _max = [posList[0][0],posList[0][1],posList[0][2]]
        for pos in posList:
            for i in range(3):
                if pos[i] < _min[i]:
                    _min[i] = pos[i]
                if pos[i] > _max[i]:
                    _max[i] = pos[i]
        ans = [(_max[0]+_min[0])/2,(_max[1]+_min[1])/2,(_max[2]+_min[2])/2]
        return ans

    def calcPivotCenterPoint(self):
        selections = mc.ls(long=True,selection=True)
        if not len(selections):
            return
        if ".vtx" in selections[0]:
            _type = "vtx"
            selections = mc.filterExpand(selections, selectionMask= 31)
        elif ".e" in selections[0]:
            _type = "edge"
            selections = mc.filterExpand(selections, selectionMask= 32)
        elif ".f" in selections[0]:
            _type = "face"
            selections = mc.filterExpand(selections, selectionMask= 34)
        else:
            print("You can select 'vtx', 'edge', 'face', only.")
            return None
        posList = []
        for name in selections:
            if _type == "vtx":
                pos = mc.xform(name,q=True,worldSpace=True,translation=True)
                posList.append([pos[0],pos[1],pos[2]])
            elif _type == "edge":
                pos = mc.xform(name,q=True,worldSpace=True,translation=True)
                posList.append([pos[0],pos[1],pos[2]])
                posList.append([pos[3],pos[4],pos[5]])
            elif _type == "face":
                pos = mc.xform(name,q=True,worldSpace=True,translation=True)
                posList.append([pos[0],pos[ 1],pos[ 2]])
                posList.append([pos[3],pos[ 4],pos[ 5]])
                posList.append([pos[6],pos[ 7],pos[ 8]])
                posList.append([pos[9],pos[10],pos[11]])
        if self.isCalcCenterByBox:
            result = self.calcCenterByBox(posList)
        else:
            result = self.calcCenter(posList)

        print(result)

        return result

    def scaleFromPivot(self):
        pivotPos = self.calcPivotCenterPoint()
        if pivotPos == None:
            return
        elif not (self.x_value*self.y_value*self.z_value) == 1.00:
            mc.undoInfo(openChunk=True)
            mc.scale(self.x_value,self.y_value,self.z_value,pivot=pivotPos,relative=True)
            mc.undoInfo(closeChunk=True)

def main():
    win = CreatePolygonUI()
    win.show()