#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import maya.cmds as cmds

def main():
    #print(cmds.selectPref(q=True,useDepth=True))
    if cmds.selectPref(q=True,useDepth=True):
        cmds.selectPref(useDepth=False)
    else:
        cmds.selectPref(useDepth=True)
    #print(cmds.selectPref(q=True,useDepth=True))