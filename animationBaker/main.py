#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from maya import cmds

from animationBaker.functions import *

def execute():
    """実行部分
    """
    new_root_name = "new"
    start_frame = 1
    end_frame = 30
    frames = end_frame - start_frame + 1

    # 選択しているオブジェクトをrootのリストとして取得
    root_list = cmds.ls(selection=True)
    # print(root_list)

    # rootからジョイントを取得(バインドを効率良くするため)
    joint_list = get_all_joints(root_list)
    # print(joint_list)

    # rootからトランスフォームノードを取得
    transform_list = get_all_transforms(root_list)
    # print(transform_list)

    # トランスフォームノードからシェイプノードを取得
    shape_list = get_all_shapes(transform_list)
    # print(shape_list)

    # シェイプノードからヒストリーを取得
    # history_list = getAllHistory(shape_list)
    # print(history_list)

    # シェイプノードからスキンクラスターを取得
    shapeToSkinCluster_dict = get_all_skin_clusters(shape_list)
    # print(shapeToSkinCluster_dict)

    # {スキンクラスター:シェイプノード}の辞書を作成
    skinClusterToShape_dict = {v:k for k,v in shapeToSkinCluster_dict.items()}
    # print(skinClusterToShape_dict)

    # スキンクラスターだけのリストを作成
    skinCluster_list = []
    for shape in shape_list:
        if not shape in shapeToSkinCluster_dict.keys():
            continue
        skinCluster_list.append(shapeToSkinCluster_dict[shape])
    # print(skinCluster_list)

    # スキンクラスターからインフルエンス(ジョイント)を取得
    skinClusterToInfluence_dict = get_all_influences(skinCluster_list)
    # print(skinClusterToInfluence_dict)

    # rootを複製
    duplicated_root = duplicate_root(root_list, name=new_root_name)

    # 複製したrootの階層下のコンストレイントを全て取得する
    duplicated_constraint_list = get_all_constraints(duplicated_root)
    # print(duplicated_constraint_list)

    # 複製した方にはコンストレイントは不要なので削除する
    cmds.delete(duplicated_constraint_list)

    # 元のノードのパスを修正して複製したシェイプノードを取得して辞書にする
    shapeToDuplicated_dict = {shape:get_fixed_path(new_root_name, shape) for shape in shape_list}
    # print(shapeToDuplicated_dict)

    # 元のノードのパスを修正して複製したジョイントを取得して辞書にする
    jointToDuplicated_dict = {joint:get_fixed_path(new_root_name, joint) for joint in joint_list}
    # print(jointToDuplicated_dict)

    # 新しいスキンクラスターを保存するための辞書
    skinClusterToDuplicated_dict = {}
    # 複製されたシェイプノードとジョイントを使ってバインド
    for skinCluster in skinCluster_list:
        # 元のインフルエンスのリスト
        influence_list = skinClusterToInfluence_dict[skinCluster]
        # 複製したインフルエンスのリスト
        duplicated_influence_list = [get_fixed_path(new_root_name, influence) for influence in influence_list]
        # 元のシェイプノード
        shape = skinClusterToShape_dict[skinCluster]
        # バインドするために複製したシェイプノードをリストの末尾に追加する
        duplicated_influence_list.append(get_fixed_path(new_root_name, shape))

        # 新しいスキンクラスターを辞書に保存
        skinClusterToDuplicated_dict[skinCluster] = cmds.skinCluster(duplicated_influence_list, toSelectedBones=True)[0]
    # print(skinClusterToDuplicated_dict)

    # 元のスキンクラスターから後のスキンクラスターへコピースキンウェイト
    for skinCluster in skinCluster_list:
        cmds.copySkinWeights(
            sourceSkin = skinCluster,
            destinationSkin = skinClusterToDuplicated_dict[skinCluster],
            noMirror=True,
            influenceAssociation="oneToOne",
            surfaceAssociation="closestPoint"
        )

    # 元のインフルエンス(ジョイント)の各フレームの変化からベイク対象を選別
    # translate or rotate or scale or visibilityのいずれかに変化があったかどうか
    bakeSourceJointToTargetAttr_dict = get_bake_source_joint_attr_dict(joint_list, startFrame=start_frame, endFrame=end_frame)
    # print(bakeSourceJointToTargetAttr_dict)

    # フレーム毎にキーを打つ(=ベイクする)
    for i in range(frames):
        # 時間(フレーム)を更新する
        now_time = start_frame + i
        # ベイクのソースになるジョイント、ベイク対象かどうかのタプル(translate,rotate,scale)
        for source, check_tuple in bakeSourceJointToTargetAttr_dict.items():
            # ベイクのターゲットを取得
            target = jointToDuplicated_dict[source]
            # translate,rotate,scaleの3つを確認
            for i in range(3):
                # アトリビュートがベイク対象であれば
                if check_tuple[i]:
                    # アトリビュートの種類
                    if(i==0):attr=".translate"
                    elif(i==1):attr=".rotate"
                    elif(i==2):attr=".scale"
                    # ソースのアトリビュートの指定した時間の値を取得
                    source_transform_tuple = cmds.getAttr(source+attr, time=now_time)[0]
                    # ターゲットのアトリビュートの指定した時間の値にキーを打つ
                    cmds.setKeyframe(target, attribute=attr+"X", time=now_time, value=source_transform_tuple[0])
                    cmds.setKeyframe(target, attribute=attr+"Y", time=now_time, value=source_transform_tuple[1])
                    cmds.setKeyframe(target, attribute=attr+"Z", time=now_time, value=source_transform_tuple[2])

def bake():
    try:
        # undo用のチャンクを開く
        cmds.undoInfo(openChunk=True)
        print("bake!")
        # 実行
        execute()
    except:
        print("error!")
        pass
    else:
        print("done!")
    finally:
        # undo用のチャンクを閉じる
        cmds.undoInfo(closeChunk=True)

if __name__ == '__main__':
    # 実行
    bake()