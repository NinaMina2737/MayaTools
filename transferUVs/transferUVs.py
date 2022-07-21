#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import maya.cmds as cmds

def main():
    objs = cmds.ls(selection=True)

    base = objs.pop(0)

    cmds.undoInfo(openChunk=True)
    for obj in objs:
        cmds.select([base,obj])
        cmds.transferAttributes(sampleSpace=4,transferUVs=2,transferColors=2)
    cmds.undoInfo(closeChunk=True)