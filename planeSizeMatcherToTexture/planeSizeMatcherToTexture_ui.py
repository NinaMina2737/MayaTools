#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import os.path

import maya.cmds as cmds
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
        self.setWindowTitle("planeSizeMatcherToTexture")

        # uiファイルからウィジェットを作成
        ui_filename = this_dir("planeSizeMatcherToTexture_ui.ui")  # uiファイル名を指定する
        self.ui = self.initUI(ui_filename)

        # ウインドウのサイズに追従するようにレイアウトを作成
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.addWidget(self.ui)

        # ウィジェットのシグナルに関数を紐づける        
        self.ui.resizeButton.clicked.connect(self.body)

    def initUI(self, ui_filename):
        ui_loader = QtUiTools.QUiLoader()        
        ui_file = QtCore.QFile(ui_filename)        
        ui_file.open(QtCore.QFile.ReadOnly)        
        ui = ui_loader.load(ui_file, parentWidget=self)        
        ui_file.close()
        return ui
    
    def check_size(self):
        #選択したオブジェクトのリストを取得
        objs = cmds.ls(selection=True,long=True)
        #print(objs)

        #選択したオブジェクトのシェイプノードのリストを取得
        shapes = cmds.listRelatives(objs, shapes=True)
        #print(shapes)

        #マテリアルにたどり着くためにシェープノードの次に接続されているシェーディンググループ(ShadingGroup)ノードのリストを取得
        sgs = cmds.listConnections(shapes, source=False, destination=True, type='shadingEngine')
        #print(sgs)

        #シェーディンググループ(sg)ノードから、その前に接続されているマテリアルノードのリストを取得
        mats = cmds.ls(cmds.listConnections(sgs, source=True, destination=False), mat=True)
        #print(mats)

        #ファイルノードのリストを取得するために各マテリアル名にアトリビュート名をつけておく('.baseColor' or '.color')
        mat_attrs = [
                        mat+'.color'
                        if ('lambert' in mat) or ('phong' in mat) or ('blinn' in mat) else mat+'.baseColor'
                        for mat in mats
                    ]
        #print(mat_attrs)

        #各マテリアルの"ベースカラー(またはカラー)"アトリビュートの前に接続されているファイルノードを取得する
        #これまでに作成したリストのインデックスを揃えるためにNoneも追加したいので各マテリアルごとにリストに追加する
        file_names = [
                        cmds.listConnections(mat_attr, source=True, destination=False)[0]
                        if cmds.listConnections(mat_attr, source=True, destination=False) else None
                        for mat_attr in mat_attrs
                    ]
        #print(file_names)

        #ファイルのサイズを取得する
        file_sizes = [(cmds.getAttr(_file_name + '.outSizeX'),cmds.getAttr(_file_name + '.outSizeY')) if _file_name else None for _file_name in file_names]
        #print(file_sizes)

        """
        #ファイルパスを取得する
        file_paths = [
                        cmds.getAttr(_file_name+'.fileTextureName')
                        if _file_name else None
                        for _file_name in file_names
                    ]
        #print(filepaths)
        """

        #print('-'*10)

        #バウンディングボックスのサイズを取得してオブジェクトの高さ(z)と幅(x)を取得する(ﾊﾞｳﾝﾃﾞｨﾝｸﾞﾎﾞｯｸｽ-->[-x,-y,-z,x,y,z])
        obj_sizes = []
        for obj, file_name in zip(objs, file_names):
            if file_name:
                box = cmds.exactWorldBoundingBox(obj)
                obj_sizes.append((abs(box[3] - box[0]), abs(box[5] - box[2])))#(width, height)-->(x_lengh, z_lengh)
            else:
                obj_sizes.append(None)
        #print(obj_sizes)

        del shapes, sgs, mats, mat_attrs, file_names

        return (objs,obj_sizes,file_sizes)

    def match_size(self, obj_list, obj_size_list, file_size_list, ratio=0.01):
        cmds.undoInfo(openChunk=True)
        for obj, obj_size, file_size in zip(obj_list, obj_size_list, file_size_list):
            if file_size:
                cmds.scale(file_size[0]/obj_size[0]*ratio, file_size[1]/obj_size[1]*ratio, obj, relative=True, xz=True)
        cmds.undoInfo(closeChunk=True)
    
    def body(self):
        _obj_list = self.check_size()[0]
        _obj_size_list = self.check_size()[1]
        _file_size_list = self.check_size()[2]
        if self.ui.radioButton_1.isChecked():
            _ratio = 1
        elif self.ui.radioButton_10.isChecked():
            _ratio = 0.1
        elif self.ui.radioButton_100.isChecked():
            _ratio = 0.01
        elif self.ui.radioButton_1000.isChecked():
            _ratio = 0.001
        self.match_size(obj_list=_obj_list, obj_size_list=_obj_size_list, file_size_list=_file_size_list, ratio=_ratio)

def main():
    win = CreatePolygonUI()
    win.show()