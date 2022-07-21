#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from maya import cmds
from maya import mel

"""スキンバインドまでを終わらせた段階で、メッシュ選択状態にして実行すれば使用できます。"""
def main():
    THRESHOLD_WEIGHT = 0.5
    FIX_WEIGHT = 1.0

    can_fix = True
    selections = cmds.ls(sl=True) or None
    # 選択物チェック
    if selections is None:
        cmds.warning("Not any selected.")
        can_fix = False
    # skinClusterチェック&取得
    if can_fix:
        obj = selections[0]
        skin_cluster = mel.eval("findRelatedSkinCluster {};".format(obj))
        if skin_cluster == "":
            cmds.warning("Selected object does not have skinCluster.")
            can_fix = False

    if can_fix:        
        # ウェイト値が閾値以下のものを削除
        mel.eval("doPruneSkinClusterWeightsArgList 1 {\""+repr(THRESHOLD_WEIGHT)+"\"};")
        
        jnts = cmds.ls(type="joint")
        cmds.progressWindow(isInterruptable=True, title="Weight Fixing...", maxValue=len(jnts))
        for jnt in jnts:
            # スキンインフルエンスの存在確認
            connections = cmds.listConnections(jnt, destination=True)
            exists_skinCluster = False
            for connect in connections:
                if connect == skin_cluster:
                    exists_skinCluster = True
                    break
            
            if exists_skinCluster:
                # 影響を受けている頂点の選択
                cmds.select(cl=True)
                cmds.skinCluster(skin_cluster, e=True, selectInfluenceVerts=jnt)
                # 値を指定値に補正
                for vtx in cmds.ls(sl=True, fl=True):
                    if vtx != "{}Shape".format(obj):
                        cmds.skinPercent(skin_cluster, vtx, transformValue=[(jnt, FIX_WEIGHT)])
            cmds.progressWindow(edit=True, step = 1)
        cmds.progressWindow(endProgress=True)
        cmds.select(cl=True)