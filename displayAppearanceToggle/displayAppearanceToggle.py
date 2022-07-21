#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import maya.cmds as cmds

#---------------------------------------.
# modesに指定した順番で表示モードを切り替える
# modesに指定できるモードは下記の通り
# @param[in] modes ['wireframe','points','boundingBox','smoothShaded','flatShaded','wireframeOnShaded'].
# @return None.
#---------------------------------------.
def main(modes = ['wireframe','points','boundingBox','smoothShaded','flatShaded','wireframeOnShaded']):
    #print(modes)
    currentPanel = cmds.getPanel(withFocus=True)#現在アクティブなパネルを取得
    panelType = cmds.getPanel(typeOf=currentPanel)#取得したパネルのタイプを取得
    #print(currentPanel)
    #print(panelType)

    if panelType == "modelPanel":
        currentDAMode = cmds.modelEditor(currentPanel, q=True, displayAppearance=True)#取得したパネルの現在の表示モードを取得
        isWireframeOnShaded = cmds.modelEditor(currentPanel, q=True, wireframeOnShaded=True)#wireframeOnShaded表示かどうか
        if isWireframeOnShaded and (currentDAMode == 'smoothShaded'):#wireframeOnShaded表示がonで かつ 現在の表示モードがsmoothShadedであれば
            currentDAMode = 'wireframeOnShaded'#wireframeOnShaded表示とみなす
        #print(currentDAMode)
        #print(isWireframeOnShaded)

        currentIndex = modes.index(currentDAMode)#現在の表示モードが該当するインデックスを取得
        newIndex = (currentIndex + 1) % len(modes)#インデックスを1つ次へ(切り替えがループする様に調整)
        newMode = modes[newIndex]
        #print(currentIndex)
        #print(newIndex)
        #print(newMode)
        print('Now changed \'{0}\' mode.'.format(newMode))

        if newMode == 'wireframeOnShaded':#表示モードをwireframeOnShadedにする場合は
            cmds.modelEditor(currentPanel, e=True, displayAppearance='smoothShaded')#smoothShadedにして
            cmds.modelEditor(currentPanel, e=True, wireframeOnShaded=True)#wireframeOnShaded表示をonにする
        else:#その他の場合は
            if isWireframeOnShaded == True:#wireframeOnShadedがonであれば
                cmds.modelEditor(currentPanel, e=True, wireframeOnShaded=False)#wireframeOnShadedをoffにして
            cmds.modelEditor(currentPanel, e=True, displayAppearance=newMode)#newModeに変更