#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import maya.cmds as cmds

def check_size():
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

def match_size(obj_list, obj_size_list, file_size_list, ratio=0.01):
    cmds.undoInfo(openChunk=True)
    for obj, obj_size, file_size in zip(obj_list, obj_size_list, file_size_list):
        if file_size:
            cmds.scale(file_size[0]/obj_size[0]*ratio, file_size[1]/obj_size[1]*ratio, obj, relative=True, xz=True)
    cmds.undoInfo(closeChunk=True)

_obj_list = check_size()[0]
_obj_size_list = check_size()[1]
_file_size_list = check_size()[2]
_ratio = 0.01
match_size(_obj_list, _obj_size_list, _file_size_list, ratio=_ratio)