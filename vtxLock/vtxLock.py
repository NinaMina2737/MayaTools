#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import maya.cmds as mc

def toggle():
    selVtxList = mc.ls(sl=True, flatten=True, type="float3")
    mc.undoInfo(openChunk=True)
    for selVtx in selVtxList:
        mc.setAttr(selVtx + ".px", lock = not (mc.getAttr(selVtx + ".px", lock=True)))
        mc.setAttr(selVtx + ".py", lock = not (mc.getAttr(selVtx + ".py", lock=True)))
        mc.setAttr(selVtx + ".pz", lock = not (mc.getAttr(selVtx + ".pz", lock=True)))
    mc.undoInfo(closeChunk=True)

def on():
    selVtxList = mc.ls(sl=True, flatten=True, type="float3")
    mc.undoInfo(openChunk=True)
    for selVtx in selVtxList:
        mc.setAttr(selVtx + ".px", lock = True)
        mc.setAttr(selVtx + ".py", lock = True)
        mc.setAttr(selVtx + ".pz", lock = True)
    mc.undoInfo(closeChunk=True)

def off():
    selVtxList = mc.ls(sl=True, flatten=True, type="float3")
    mc.undoInfo(openChunk=True)
    for selVtx in selVtxList:
        mc.setAttr(selVtx + ".px", lock = False)
        mc.setAttr(selVtx + ".py", lock = False)
        mc.setAttr(selVtx + ".pz", lock = False)
    mc.undoInfo(closeChunk=True)