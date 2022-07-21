#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import maya.cmds as mc

def calcCenter(posList):
    ans = [0,0,0]
    for pos in posList:
        ans[0] += pos[0]
        ans[1] += pos[1]
        ans[2] += pos[2]
    ans[0] /= len(posList)
    ans[1] /= len(posList)
    ans[2] /= len(posList)
    return ans

def calcCenterByBox(posList):
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

def calcPivotCenterPoint():
    _type = None
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
    result = calcCenterByBox(posList)
    print(result)
    
    return result

def scaleFromPivot(x,y,z):
    pivotPos = calcPivotCenterPoint()
    if pivotPos == None:
        return
    elif not (x*y*z) == 1.00:
        mc.undoInfo(openChunk=True)
        mc.scale(x,y,z,pivot=pivotPos,relative=True)
        mc.undoInfo(closeChunk=True)

def relativeScaleByPivot(x,y,z):
    scaleFromPivot(x,y,z)