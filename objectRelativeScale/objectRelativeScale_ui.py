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

    base_axis = None
    s_num = None

    def __init__(self, *args, **kwargs):        
        super(CreatePolygonUI, self).__init__(*args, **kwargs)

        # ウインドウのタイトルを指定する
        self.setWindowTitle("objectRelativeScale")

        # uiファイルからウィジェットを作成
        ui_filename = this_dir("objectRelativeScale_ui.ui")  # uiファイル名を指定する
        self.ui = self.initUI(ui_filename)

        # ウインドウのサイズに追従するようにレイアウトを作成
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.addWidget(self.ui)

        # ウィジェットのシグナルに関数を紐づける
        self.ui.scale_freeze_button.clicked.connect(self.on_click_push_scale_freeze_button)
        self.ui.run_button.clicked.connect(self.on_click_push_run_button)

    def initUI(self, ui_filename):
        ui_loader = QtUiTools.QUiLoader()        
        ui_file = QtCore.QFile(ui_filename)        
        ui_file.open(QtCore.QFile.ReadOnly)        
        ui = ui_loader.load(ui_file, parentWidget=self)        
        ui_file.close()
        return ui
    
    def on_click_push_scale_freeze_button(self):

        #選択したオブジェクトを取得
        obj = cmds.ls(selection=True, long=True)
        print("obj:{0}".format(obj))

        for line in obj:
            cmds.makeIdentity( line, apply=True, scale=True )#scaleフリーズ
            print('「{0}」の"scale"をフリーズしました'.format(line.lstrip('|')))

    def on_click_push_run_button(self):

        # 各ウィジェットの値を取得

        if self.ui.radioButton_x.isChecked() == True:
            self.base_axis = 'x'
        elif self.ui.radioButton_y.isChecked() == True:
            self.base_axis = 'y'
        elif self.ui.radioButton_z.isChecked() == True:
            self.base_axis = 'z'
        else:
            print("軸を選択していません")

        self.s_num = self.ui.scale_widget.value()
        if self.s_num == 0:
            print("scale値は0以外で指定してください")
            self.s_num = None

        print()
        print("指定した軸:{0}".format(self.base_axis))
        print("指定した長さ{0}".format(self.s_num))
        print()

        if not(self.base_axis == None) and not(self.s_num == None):
            self.body()
        else:
            print("正しい設定を行ってください")

    def calc_lengh(self,a,b):
        return abs(a-b)

    def manage_scaleValue(self,manageType,axis,obj,setValue=1.00):
        if manageType == 'g' or manageType == 'get':
            if axis == 'x':
                return cmds.getAttr('{0}.scaleX'.format(obj))
            elif axis == 'y':
                return cmds.getAttr('{0}.scaleY'.format(obj))
            elif axis == 'z':
                return cmds.getAttr('{0}.scaleZ'.format(obj))
            else:
                return False
        elif manageType == 's' or manageType == 'set':
            if axis == 'x':
                cmds.setAttr('{0}.scaleX'.format(obj),setValue)
            elif axis == 'y':
                cmds.setAttr('{0}.scaleY'.format(obj),setValue)
            elif axis == 'z':
                cmds.setAttr('{0}.scaleZ'.format(obj),setValue)
            else:
                return False

    def ratio_check(self,base,x,y,z):
        base_value = 0
        if base == 'x':
            base_value = x
        elif base == 'y':
            base_value = y
        elif base == 'z':
            base_value = z
        else:
            return False
        X = x / base_value
        Y = y / base_value
        Z = z / base_value 
        ratio = [X,Y,Z]
        return ratio

    def body(self):

        #選択したオブジェクトを取得
        obj = cmds.ls(selection=True, long=True)
        print("obj:{0}".format(obj))

        #バウンディングボックスの情報を取得
        before_bb = [[None,None,None,None,None,None] for _ in range(len(obj))]
        for i in range(len(obj)):
            before_bb[i] = cmds.exactWorldBoundingBox(obj[i])
        #print('before_bb:{0}'.format(before_bb))

        #各objの元々の長さ(x,y,z)を格納
        before_obj_lengh = [[None,None,None] for _ in range(len(obj))]
        for i in range(len(obj)):
            x_min = before_bb[i][0]
            y_min = before_bb[i][1]
            z_min = before_bb[i][2]
            x_max = before_bb[i][3]
            y_max = before_bb[i][4]
            z_max = before_bb[i][5]
            x = self.calc_lengh(x_min,x_max)
            y = self.calc_lengh(y_min,y_max)
            z = self.calc_lengh(z_min,z_max)
            before_obj_lengh[i] = [x,y,z]
        #print('before_obj_lengh:{0}'.format(before_obj_lengh))

        #for文のためのリスト
        axis = ['x','y','z']

        #scale値をget
        before_scale_value_list = [[None,None,None] for _ in range(len(obj))]
        #print("ini_before_scale_value_list:{0}".format(before_scale_value_list))
        for i in range(len(obj)):
            for j,k in zip(range(3),axis):
                before_scale_value_list[i][j] = self.manage_scaleValue('g',k,obj[i])
        #print("before_scale_value_list:{0}".format(before_scale_value_list))

        #指定の軸を基準とした比を求める(Debug用)
        before_s_ratio = [None] * len(obj)
        for i,line in enumerate(before_scale_value_list):
            before_s_ratio[i] = self.ratio_check(self.base_axis,line[0],line[1],line[2])
        #print("before_s_ratio:{0}".format(before_s_ratio))

        #元の長さを基に現在のscale値を何倍すればよいか求める(指定の長さ/元の長さ=元の長さを何倍すれば指定の長さになるかの比)
        ratio_list = [None] * len(obj)
        for i in range(len(obj)):
            if self.base_axis == 'x':
                ratio_list[i] = self.s_num / before_obj_lengh[i][0]
            elif self.base_axis == 'y':
                ratio_list[i] = self.s_num / before_obj_lengh[i][1]
            elif self.base_axis == 'z':
                ratio_list[i] = self.s_num / before_obj_lengh[i][2]
            else:
                pass
        #print("ratio_list:{0}".format(ratio_list))

        #元のscale値を求めた倍率でscaleする
        for_set_scale_value_list = [[None,None,None] for _ in range(len(obj))]
        for i in range(len(obj)):
            x = before_scale_value_list[i][0] * ratio_list[i]
            y = before_scale_value_list[i][1] * ratio_list[i]
            z = before_scale_value_list[i][2] * ratio_list[i]
            for_set_scale_value_list[i] = [x,y,z]
        #print("for_set_before_scale_value_list:{0}".format(before_scale_value_list))

        #scale
        cmds.undoInfo(openChunk=True)#ヒストリをまとめる(open)
        for i in range(len(obj)):
            for j,k in zip(range(3),axis):
                self.manage_scaleValue('s',k,obj[i],setValue=for_set_scale_value_list[i][j])
        cmds.undoInfo(closeChunk=True)#ヒストリをまとめる(close)

        #再度scale値をget
        after_scale_value_list = [[None,None,None] for _ in range(len(obj))]
        for i in range(len(obj)):
            for j,k in zip(range(3),axis):
                after_scale_value_list[i][j] = self.manage_scaleValue('g',k,obj[i])
        #print("after_scale_value_list:{0}".format(after_scale_value_list))

        #再度、指定の軸を基準とした比を求める(Debug用)
        after_s_ratio = [None] * len(obj)
        for i,line in enumerate(after_scale_value_list):
            after_s_ratio[i] = self.ratio_check(self.base_axis,line[0],line[1],line[2])
        #print("after_s_ratio:{0}".format(after_s_ratio))

        #再度バウンディングボックスの情報を取得
        after_bb = [[None,None,None,None,None,None] for _ in range(len(obj))]
        for i in range(len(obj)):
            after_bb[i] = cmds.exactWorldBoundingBox(obj[i])
        #print('after_bb:{0}'.format(after_bb))

        #再度、各objの長さ(x,y,z)を格納
        after_obj_lengh = [[None,None,None] for _ in range(len(obj))]
        for i in range(len(obj)):
            x_min = after_bb[i][0]
            y_min = after_bb[i][1]
            z_min = after_bb[i][2]
            x_max = after_bb[i][3]
            y_max = after_bb[i][4]
            z_max = after_bb[i][5]
            x = self.calc_lengh(x_min,x_max)
            y = self.calc_lengh(y_min,y_max)
            z = self.calc_lengh(z_min,z_max)
            after_obj_lengh[i] = [x,y,z]
        #print('after_obj_lengh:{0}'.format(after_obj_lengh))

        #表示
        print()
        print('before_obj_lengh:{0}'.format(before_obj_lengh))
        print("before_scale_value_list:{0}".format(before_scale_value_list))
        print("before_s_ratio:{0}".format(before_s_ratio))
        print()

        print("ratio_list:{0}".format(ratio_list))
        print()
        
        print('after_obj_lengh:{0}'.format(after_obj_lengh))
        print("after_scale_value_list:{0}".format(after_scale_value_list))
        print("after_s_ratio:{0}".format(after_s_ratio))
        print()

        print('"{0}"軸 の幅を "{1}"cm にしました'.format(self.base_axis.upper(),self.s_num))
        print()

def main():
    win = CreatePolygonUI()
    win.show()