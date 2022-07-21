#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import maya.cmds as cmds

def renameNode(search_text, user_text, mode='rename'):
    cmds.undoInfo(openChunk=True)
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

def addNameNode(search_text, user_text, pos='beginning'):
    cmds.undoInfo(openChunk=True)
    nodeList = cmds.ls(sl=True)
    for nodeName in nodeList:
        newName = None
        if pos == 'beginning':
            newName = user_text + nodeName
        elif pos == 'end':
            newName = nodeName + user_text
        elif pos == 'before':
            search_text_index = nodeName.find(search_text)
            newName = nodeName[:search_text_index] + user_text + nodeName[search_text_index:]
        elif pos == 'after':
            search_text_index = nodeName.find(search_text) + len(search_text)
            newName = nodeName[:search_text_index] + user_text + nodeName[search_text_index:]
        if nodeName == newName:
            pass
        else:
            cmds.rename( nodeName, newName )
    cmds.undoInfo(closeChunk=True)