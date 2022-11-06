#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from maya import cmds

def getAllJoint(root):
    """階層下のジョイントを全て検索してリストで返す"""
    result = []
    for child in root:
        child_type = cmds.ls(child, showType=True)[1]
        if(child_type == "joint"):
            result.append(child)
        new_root = cmds.listRelatives(child, children=True, fullPath=True)
        if(new_root is not None):
            result.extend(getAllJoint(new_root))
    return result

def getAllConstraint(root):
    """階層下のコンストレイントを全て検索してリストで返す"""
    result = []
    for child in root:
        child_type = cmds.ls(child, showType=True)[1]
        if("Constraint" in child_type):
            result.append(child)
        new_root = cmds.listRelatives(child, children=True, fullPath=True)
        if(new_root is not None):
            result.extend(getAllConstraint(new_root))
    return result

def getConstraintConnection(node):
    """引数に渡したコンストレイントノードのsourceとdestinationとをタプルにして返す"""
    source = cmds.listConnections(node+".target[0].targetParentMatrix", source=True, destination=False)[0]
    destination = cmds.listConnections(node+".constraintParentInverseMatrix", source=True, destination=False)[0]
    return (source, destination)

def duplicateRoot(root, name="new"):
    """引数に渡したroot以下のパスを揃えた形で複製する"""
    # パスを揃えるためにグループ化
    temp = cmds.group(root, name="root_temp")
    # 複製
    duplicated_root = cmds.duplicate(temp, name=name, returnRootsOnly=True)
    # グループ化を解除する
    cmds.ungroup(temp)
    # return
    return duplicated_root

def getBakeSourceJointToTargetAttrDict(joint_list, startFrame, endFrame, epsilon=1e-4):
    """ベイクのソースになるジョイントがキー、各アトリビュートにベイクが必要かどうかのタプルがバリューの辞書を返す

    Keyword arguments:\n
    joint_list -- joint list\n
    startFrame -- frame number of start bake\n
    endFrame -- frame number of end bake\n
    epsilon -- 誤差を出すための微小値 (default 1e-4)\n

    Return:\n
    bakeSourceJointToTargetAttr_dict -- dictionary {key:value}\n
                     key -- ベイクのソースになるジョイント\n
                     value -- 各アトリビュートにベイクが必要かどうかのタプル(translate, rotate, scale)\n
    """
    # 開始フレーム
    start_frame = startFrame
    # 終了フレーム
    end_frame = endFrame
    # 確認するフレーム数
    frames = end_frame - start_frame + 1
    # 差分を比較する用の値
    ep = epsilon
    # 比較用の前フレームの値を初期化
    pre_values_dict = {}
    # 処理が必要かどうかのチェックリスト[translate,rotate,scale]を初期化
    check_list_dict = {}
    # return用の辞書
    bakeSourceJointToTargetAttr_Dict = {}

    # フレーム毎に確認
    for i in range(frames):
        # 時間を更新
        now_frame = start_frame + i
        for joint in joint_list:
            # 指定した時間(=フレーム)でのアトリビュートの値を取得
            values = []
            values.extend(cmds.getAttr(joint+".translate", time=now_frame))
            values.extend(cmds.getAttr(joint+".rotate", time=now_frame))
            values.extend(cmds.getAttr(joint+".scale", time=now_frame))
            # 最初のフレームなら
            if(i == 0):
                # 初期状態を保存
                pre_values_dict[joint] = values
                # 各アトリビュートがベイク対象かどうかのチェックリスト[translate,rotate,scale]を初期化
                check_list_dict[joint] = [False,False,False]
                # 次のジョイントへ
                continue
            # アトリビュート、軸毎に値の変化を見る
            for i in range(3): # (translate, rotate, scale)
                for j in range(3): # (x, y, z)
                    # 前フレームと比べて変化しているか
                    if(abs(values[i][j]-pre_values_dict[joint][i][j])>ep):
                        # 該当するアトリビュートにチェック
                        check_list_dict[joint][i] = True
                        # x,y,zのいずれかがTrueであれば次のアトリビュートへ
                        break
            # チェックリストが全部Trueであれば
            if not(False in check_list_dict[joint]):
                # 次のジョイントへ
                continue
            # それ以外は
            else:
                # 前フレームの値として保持
                pre_values_dict[joint] = values
    for joint in joint_list:
        # チェックリストにひとつでもTrueが存在していたらベイク対象に追加
        if(True in check_list_dict[joint]):
            bakeSourceJointToTargetAttr_Dict[joint] = tuple(check_list_dict[joint])
    return bakeSourceJointToTargetAttr_Dict

def getAllTransform(root):
    """階層下のトランスフォームを全て検索してリストで返す"""
    result = []
    for child in root:
        child_type = cmds.ls(child, showType=True)[1]
        if(child_type == "transform"):
            result.append(child)
        new_root = cmds.listRelatives(child, children=True, fullPath=True)
        if(new_root is not None):
            result.extend(getAllTransform(new_root))
    return result

def getAllShape(transforms):
    """トランスフォームノードのリストから接続されているシェイプノードをリストで返す"""
    result = []
    for t in transforms:
        shape = cmds.listRelatives(t, fullPath=True, noIntermediate=True, shapes=True)
        if not (shape is None):
            result.extend(shape)
    return result

def getAllHistory(shapes):
    """シェイプノードのリストから、シェイプノードをキー、そのヒストリーのリストをバリューにした辞書を返す"""
    result = {}
    for shape in shapes:
        history = cmds.listHistory(shape, pruneDagObjects=True, interestLevel=2)
        result[shape] = history
    return result

def getAllSkinCluster(shapes):
    """シェイプノードのリストから、シェイプノードをキー、そのスキンクラスターをバリューにした辞書を返す(スキンクラスターが無い場合は除外)"""
    histories = getAllHistory(shapes)
    result = {}
    for shape in shapes:
        skinCluster = cmds.ls(histories[shape], type="skinCluster")
        # リストが空かNoneではないなら→リストに何か入っていれば
        if skinCluster:
            result[shape] = skinCluster[0]
    return result

def getAllInfluence(skinClusters):
    """スキンクラスターのリストから、スキンクラスターをキー、そのインフルエンスのリストをバリューにした辞書を返す"""
    result = {}
    for sc in skinClusters:
        influence_list = cmds.skinCluster(sc, q=True, influence=True)
        influence_fullPath_list = cmds.ls(influence_list, long=True)
        result[sc] = influence_fullPath_list
        # print(result[sc])
    return result

def getFixedPath(rootName, path, beforeName=False):
    """パスの最初を修正して複製前後のパスを返す"""
    if beforeName:
        return path[len(rootName+1):]
    else:
        if(path[0]=="|"):
            return rootName + path
        else:
            return rootName + "|" + path

def main():
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
    joint_list = getAllJoint(root_list)
    # print(joint_list)

    # rootからトランスフォームノードを取得
    transform_list = getAllTransform(root_list)
    # print(transform_list)

    # トランスフォームノードからシェイプノードを取得
    shape_list = getAllShape(transform_list)
    # print(shape_list)

    # シェイプノードからヒストリーを取得
    # history_list = getAllHistory(shape_list)
    # print(history_list)

    # シェイプノードからスキンクラスターを取得
    shapeToSkinCluster_dict = getAllSkinCluster(shape_list)
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
    skinClusterToInfluence_dict = getAllInfluence(skinCluster_list)
    # print(skinClusterToInfluence_dict)

    # rootを複製
    duplicated_root = duplicateRoot(root_list, name=new_root_name)

    # 複製したrootの階層下のコンストレイントを全て取得する
    duplicated_constraint_list = getAllConstraint(duplicated_root)
    # print(duplicated_constraint_list)

    # 複製した方にはコンストレイントは不要なので削除する
    cmds.delete(duplicated_constraint_list)

    # 元のノードのパスを修正して複製したシェイプノードを取得して辞書にする
    shapeToDuplicated_dict = {shape:getFixedPath(new_root_name, shape) for shape in shape_list}
    # print(shapeToDuplicated_dict)

    # 元のノードのパスを修正して複製したジョイントを取得して辞書にする
    jointToDuplicated_dict = {joint:getFixedPath(new_root_name, joint) for joint in joint_list}
    # print(jointToDuplicated_dict)

    # 新しいスキンクラスターを保存するための辞書
    skinClusterToDuplicated_dict = {}
    # 複製されたシェイプノードとジョイントを使ってバインド
    for skinCluster in skinCluster_list:
        # 元のインフルエンスのリスト
        influence_list = skinClusterToInfluence_dict[skinCluster]
        # 複製したインフルエンスのリスト
        duplicated_influence_list = [getFixedPath(new_root_name, influence) for influence in influence_list]
        # 元のシェイプノード
        shape = skinClusterToShape_dict[skinCluster]
        # バインドするために複製したシェイプノードをリストの末尾に追加する
        duplicated_influence_list.append(getFixedPath(new_root_name, shape))

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
    bakeSourceJointToTargetAttr_dict = getBakeSourceJointToTargetAttrDict(joint_list, startFrame=start_frame, endFrame=end_frame)
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

try:
    # undo用のチャンクを開く
    cmds.undoInfo(openChunk=True)
    # 実行
    main()
finally:
    # undo用のチャンクを閉じる
    cmds.undoInfo(closeChunk=True)