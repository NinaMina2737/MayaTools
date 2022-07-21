#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import os.path
import math

from maya import cmds
from maya import OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin
from PySide2 import QtCore, QtGui, QtWidgets, QtUiTools
from shiboken2 import wrapInstance


def this_dir(*args):
    """このスクリプトと同じフォルダからの相対パスをフルパスに変換して返す"""
    dir_path = os.path.dirname(__file__.decode(u"cp932"))
    return os.path.join(dir_path, *args)

#---------------------------------------.
# ゼロチェック.
# @param[in] v   実数値.
# @return ゼロの場合はTrue.
#---------------------------------------.
def isZero (v):
    minV = 1e-5
    if v > -minV and v < minV:
        return True
    return False

#---------------------------------------.
# ベクトルの長さを計算.
# @param[in] v   ベクトル値.
# @return ベクトルの長さ.
#---------------------------------------.
def length_vec3(v):
    return pow(v[0]*v[0] + v[1]*v[1] + v[2]*v[2], 0.5)
def length_vec4(v):
    return pow(v[0]*v[0] + v[1]*v[1] + v[2]*v[2] + v[3]*v[3], 0.5)

#---------------------------------------.
# 単位ベクトルを計算.
# @param[in] v   xyzのベクトル値.
# @return 正規化されたベクトル値.
#---------------------------------------.
def normalize_vec3(v):
    len = length_vec3(v)
    if isZero(len):
        return [0, 0, 0]
    return [v[0]/len,v[1]/len,v[2]/len]
def normalize_vec4(v):
    len = length_vec4(v)
    if isZero(len):
        return [0, 0, 0]
    return [v[0]/len,v[1]/len,v[2]/len,v[3]/len]

#---------------------------------------.
# 内積を計算.
# @param[in] v1   xyzのベクトル1.
# @param[in] v2   xyzのベクトル2.
# @return 内積の値.
#---------------------------------------.
def dot_vec3 (v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

#---------------------------------------.
# 外積を計算.
# @param[in] v1 --> xyzのベクトル1.
# @param[in] v2 --> xyzのベクトル2.
# @return 外積のベクトル.
#---------------------------------------.
def cross_vec3 (v1, v2):
    return [v1[1]*v2[2]-v1[2]*v2[1], v1[2]*v2[0]-v1[0]*v2[2], v1[0]*v2[1]-v1[1]*v2[0]]

#---------------------------------------.
# ベクトルの平均を計算.
# @param[in] *args --> 複数のベクトル.
# @return ベクトルの平均.
#---------------------------------------.
def ave_vec3 (*args):
	vec = [0.0,0.0,0.0]
	for arg in args:
		vec[0] += arg[0]
		vec[1] += arg[1]
		vec[2] += arg[2]
	return [vec[0]/len(args),vec[1]/len(args),vec[2]/len(args)]

#---------------------------------------.
# クォータニオンを作成.
# @param[in] v --> 回転軸.
# @param[in] rad --> 角度.
# @return クォータニオン.
#---------------------------------------.
def MyQuaternion(v, rad):
    return [v[0]*math.sin(rad/2), v[1]*math.sin(rad/2), v[2]*math.sin(rad/2), math.cos(rad/2)]

#---------------------------------------.
# xyzの回転角度(度数法)からクォータニオンを作成.
# @param[in] x --> x軸回転角度.
# @param[in] y --> y軸回転角度.
# @param[in] z --> z軸回転角度.
# @return クォータニオン.
#---------------------------------------.
def MyQuaternionFromXYZ(x,y,z):
    sin_x = math.sin(x/2.0)
    cos_x = math.cos(x/2.0)
    sin_y = math.sin(y/2.0)
    cos_y = math.cos(y/2.0)
    sin_z = math.sin(z/2.0)
    cos_z = math.cos(z/2.0)

    mat = [0 for _ in range(4)]
    mat[0] = cos_x*sin_y*sin_z + sin_x*cos_y*cos_z
    mat[1] = -1*sin_x*cos_y*sin_z + cos_x*sin_y*cos_z
    mat[2] = cos_x*cos_y*sin_z + sin_x*sin_y*cos_z
    mat[3] = -1*sin_x*sin_y*sin_z + cos_x*cos_y*cos_z
    return mat

#---------------------------------------.
# xyzの回転角度(度数法)から回転行列を作成.
# @param[in] x --> x軸回転角度.
# @param[in] y --> y軸回転角度.
# @param[in] z --> z軸回転角度.
# @return 回転行列.
#---------------------------------------.
def MyRotateMatrixFromXYZ(x,y,z):
    sin_x = math.sin(x)
    cos_x = math.cos(x)
    sin_y = math.sin(y)
    cos_y = math.cos(y)
    sin_z = math.sin(z)
    cos_z = math.cos(z)

    mat = [[1 for _ in range(4)] for _ in range(4)]

    mat[0][0] = cos_y*cos_z
    mat[0][1] = -1*cos_y*sin_z
    mat[0][1] = -1*cos_x*sin_z + sin_x*sin_y*cos_z

    mat[0][2] = sin_y
    mat[0][2] = sin_x*sin_z + cos_x*sin_y*cos_z
    mat[0][3] = 0.0

    mat[1][0] = sin_x*sin_y*cos_z + cos_x*sin_z
    mat[1][1] = -1*sin_x*sin_y*sin_z + cos_x*cos_z
    mat[1][2] = -1*sin_x*cos_y
    mat[1][3] = 0.0

    mat[2][0] = -cos_x*sin_y*cos_z + sin_x*sin_z
    mat[2][1] = cos_x*sin_y+sin_z + sin_x*cos_z
    mat[2][2] = cos_x*cos_y
    mat[2][3] = 0.0

    mat[0][0] = cos_y*cos_z
    mat[0][1] = -1*cos_x*sin_z + sin_x*sin_y*cos_z
    mat[0][2] = sin_x*sin_z + cos_x*sin_y*cos_z
    mat[0][3] = 0.0

    mat[1][0] = cos_y*sin_z
    mat[1][1] = cos_x*cos_z + sin_x*sin_y*sin_z
    mat[1][2] = -1*sin_x*cos_z + cos_x*sin_y*sin_z
    mat[1][3] = 0.0

    mat[2][0] = -1*sin_y
    mat[2][1] = sin_x*cos_y
    mat[2][2] = cos_x*cos_y
    mat[2][3] = 0.0

    mat[3][0] = 0.0
    mat[3][1] = 0.0
    mat[3][2] = 0.0
    mat[3][3] = 1.0
    return mat

#---------------------------------------.
# クォータニオンから回転行列(4x4)を作成.
# @param[in] quat --> クォータニオン.
# @return 回転行列(4x4).
#---------------------------------------.
def MyQuaternionToMatrix4x4(quat):
    mat = [[1 for _ in range(4)] for _ in range(4)]

    mat[0][0] = 1 - 2*(quat[1]*quat[1]) - 2*(quat[2]*quat[2])
    mat[0][1] = 2*quat[0]*quat[1] + 2*quat[3]*quat[2]
    mat[0][2] = 2*quat[0]*quat[2] - 2*quat[3]*quat[1]
    mat[0][3] = 0.0

    mat[1][0] = 2*quat[0]*quat[1] - 2*quat[3]*quat[2]
    mat[1][1] = 1 - 2*(quat[0]*quat[0]) - 2*(quat[2]*quat[2])
    mat[1][2] = 2*quat[1]*quat[2] + 2*quat[3]*quat[0]
    mat[1][3] = 0.0

    mat[2][0] = 2*quat[0]*quat[2] + 2*quat[3]*quat[1]
    mat[2][1] = 2*quat[1]*quat[2] - 2*quat[3]*quat[0]
    mat[2][2] = 1 - 2*(quat[0]*quat[0]) - 2*(quat[1]*quat[1])
    mat[2][3] = 0.0

    mat[3][0] = 0.0
    mat[3][1] = 0.0
    mat[3][2] = 0.0
    mat[3][3] = 1.0

    return mat

#---------------------------------------.
# 回転行列(4x4)から配列(float x16)を作成.
# @param[in] m --> 回転行列(4x4).
# @return 配列(float x16).
#---------------------------------------.
def MyMatrix4x4ToFloatx16(m):
    return [m[0][0],m[0][1],m[0][2],m[0][3],
            m[1][0],m[1][1],m[1][2],m[1][3],
            m[2][0],m[2][1],m[2][2],m[2][3],
            m[3][0],m[3][1],m[3][2],m[3][3],]

def getRadianFromDegree(deg):
    return deg / 180 * math.pi
def getDegreeFromRadian(rad):
    return rad / math.pi * 180

#return = A * B
def matrixTransform(matA,matB):
    m1 = matA
    m2 = matB
    m2.append(1.0)
    m = [1 for _ in range(4)]
    #print(m1)
    #print(m2)
    m[0] = m1[0][0]*m2[0] + m1[0][1]*m2[1] + m1[0][2]*m2[2] + m1[0][3]*m2[3]
    m[1] = m1[1][0]*m2[0] + m1[1][1]*m2[1] + m1[1][2]*m2[2] + m1[1][3]*m2[3]
    m[2] = m1[2][0]*m2[0] + m1[2][1]*m2[1] + m1[2][2]*m2[2] + m1[2][3]*m2[3]
    m[3] = m1[3][0]*m2[0] + m1[3][1]*m2[1] + m1[3][2]*m2[2] + m1[3][3]*m2[3]
    return [m[0],m[1],m[2]]

def normalAdjusterByFace():
    objectName = cmds.ls(selection=True, objectsOnly=True)[0]
    #print(objectName)

    transformName = cmds.listRelatives(objectName, parent=True)[0]
    #print(transformName)

    selectNodeName = cmds.ls(selection=True, long=True)[0]
    #print(selectNodeName)

    index = selectNodeName.rfind(".")
    faceNumber = selectNodeName[index:]
    #print(faceNumber)

    faceName = transformName + faceNumber
    #print(faceName)

    faceNormal = cmds.polyInfo(faceName, faceNormals=True)[0]
    temp = faceNormal.split(' ')
    faceNormal = [float(temp[-3]), float(temp[-2]), float(temp[-1])]
    #print(faceNormal)

    rotX = getRadianFromDegree(cmds.getAttr(transformName + '.rotateX'))
    rotY = getRadianFromDegree(cmds.getAttr(transformName + '.rotateY'))
    rotZ = getRadianFromDegree(cmds.getAttr(transformName + '.rotateZ'))
    #print(rotX)
    #print(rotY)
    #print(rotZ)

    #回転角度(ラジアン)から回転行列を作成
    mat = MyRotateMatrixFromXYZ(rotX,rotY,rotZ)
    #表示
    #[print(i) for i in mat]
    #フリーズ前のフェース法線をフリーズ後に変換
    faceNormal = matrixTransform(mat,faceNormal)
    #print(faceNormal)
    return faceNormal

def normalAdjusterByVtx():
    objs = cmds.filterExpand(sm=31)#選択(expand)
    #print(objs)

    points = []#各頂点の座標入れ
    for obj in objs:
        points.append(cmds.pointPosition(obj))
    #print(points)

    vec1 = [points[1][0]-points[0][0],points[1][1]-points[0][1],points[1][2]-points[0][2]]#ベクトルAB
    vec2 = [points[2][0]-points[0][0],points[2][1]-points[0][1],points[2][2]-points[0][2]]#ベクトルAC
    #print(vec1)
    #print(vec2)
    cross_vec = cross_vec3 (vec1, vec2)#外積(=法線)
    #print(cross_vec)

    vtxNormals = []#各頂点法線入れ
    for obj in objs:
        vtxNormal = cmds.polyNormalPerVertex( query=True, xyz=True )
        ave = ave_vec3(vtxNormal[0:3],vtxNormal[3:6],vtxNormal[6:9])#頂点法線は3つあるので平均値を入れる
        vtxNormals.append(ave)

    ave_vtxNormal = ave_vec3(*vtxNormals)#全頂点法線の平均
    #print(ave_vtxNormal)

    if dot_vec3(cross_vec, ave_vtxNormal) < 0:#計算した法線と選択した頂点の頂点法線の平均との向きが逆方向なら
        cross_vec = [value*-1.0 for value in cross_vec]#逆ベクトルにする
        #print(cross_vec)

    for i in range(len(cross_vec)):
        if abs(cross_vec[i]) < 0.0001:
            cross_vec[i] = 0.0
    #print(cross_vec)

    faceNormal = normalize_vec3(cross_vec)
    #print(faceNormal)
    return faceNormal

class CreatePolygonUI(MayaQWidgetBaseMixin, QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(CreatePolygonUI, self).__init__(*args, **kwargs)

        # ウインドウのタイトルを指定する
        self.setWindowTitle("setGround")

        # uiファイルからウィジェットを作成
        ui_filename = this_dir("setGround.ui")  # uiファイル名を指定する
        self.ui = self.initUI(ui_filename)

        # ウインドウのサイズに追従するようにレイアウトを作成
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.vertical_layout.addWidget(self.ui)

        # ウィジェットのシグナルに関数を紐づける
        self.ui.button_set.clicked.connect(self.setGround)

    def initUI(self, ui_filename):
        ui_loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_filename)
        ui_file.open(QtCore.QFile.ReadOnly)
        ui = ui_loader.load(ui_file, parentWidget=self)
        ui_file.close()
        return ui

    def setGround(self,mode=".f"):
        #selection = cmds.ls(selection=True, long=True)
        selection = cmds.filterExpand(selectionMask=(31,34), fullPath=True)
        #print(selection)
        select_length = len(selection)
        #print(select_length)

        if (select_length == 0) or (select_length == 2) or (select_length > 3):#error
            print("You have to select ONE face or THREE vertices(vertexes).")
            return

        mode = None
        if '.f' in selection[0]:
            mode = '.f'
        elif '.vtx' in selection[0]:
            mode = '.vtx'

        for obj in selection:
            if not mode in obj:
                print('Component selection is wrong, check selection then retry again.')
                return

        #v1(対象のフェースの法線)
        #v2(対象の平面の法線の逆ベクトル)
        v1 = [0.0, 0.0, 0.0]
        v2 = [0.0, 0.0, 0.0]

        if mode == '.f':#face
            v1 = normalAdjusterByFace()
        elif mode == '.vtx':#vertex
            v1 = normalAdjusterByVtx()
        #print(v1)
        #print(mode)

        plane = self.ui.comboBox_plane.currentText()
        sign = self.ui.comboBox_sign.currentText()
        print(plane)
        print(sign)

        if plane == "XY" and sign == "+":
            v2 = [0.0,0.0,-1.0]
        elif plane == "XY" and sign == "-":
            v2 = [0.0,0.0,1.0]
        elif plane == "XZ" and sign == "+":
            v2 = [0.0,-1.0,0.0]
        elif plane == "XZ" and sign == "-":
            v2 = [0.0,1.0,0.0]
        elif plane == "YZ" and sign == "+":
            v2 = [-1.0,0.0,0.0]
        elif plane == "YZ" and sign == "-":
            v2 = [1.0,0.0,0.0]
        #print(v1)
        #print(v2)

        #v1とv2との外積 --> 回転軸
        pivot = cross_vec3 (v1, v2)
        #クォータニオンを作成するために正規化しておく
        pivot = normalize_vec3(pivot)
        #表示
        #print(pivot)

        #v1とv2とがなす角を求めるため内積
        dot = dot_vec3(v1, v2)
        #表示
        #print(dot)

        #v1とv2とがなす角を求めるための余弦(cos)の値
        cos = dot / (length_vec3(v1)*length_vec3(v2))
        #表示
        #print(cos)

        #v1とv2とがなす角を求める
        #余弦(cos)の値から角度(ラジアン)を求めるには逆余弦関数(acos)を使う
        rad = math.acos(cos)
        #表示
        #print(rad)

        #ラジアン(弧度法)を度(度数法)に変換
        #degree = getDegreeFromRadian(rad)
        #表示
        #print(degree)

        #クォータニオンを作成
        quat = MyQuaternion(pivot, rad)
        #表示
        #print(quat)

        #クォータニオンから回転行列(4x4)を作成
        mat = MyQuaternionToMatrix4x4(quat)
        #表示
        #[print(i) for i in mat]

        #回転行列(4x4)から配列(float x16)を作成
        mat_float = MyMatrix4x4ToFloatx16(mat)
        #表示
        #print(mat_float)

        #選択しているオブジェクト(ノード)名のみ
        objName = cmds.ls(selection=True, objectsOnly=True)[0]
        #トランスフォームオブジェクト名
        transName = cmds.listRelatives(objName, parent=True)[0]
        #選択しているフェースの番号を取得
        #faceNumber = cmds.ls(selection=True, long=True)[0]
        #index = faceNumber.rfind(".")
        #faceNumber = faceNumber[index:]
        #選択しているフェース名(番号を含む)を取得
        #faceName = transName + faceNumber
        #print(objName)
        #print(transName)
        #print(faceNumber)
        #print(faceName)

        #回転
        cmds.xform(transName, relative=True, matrix=mat_float)

def main():
    win = CreatePolygonUI()
    win.show()