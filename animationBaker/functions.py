#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from maya import cmds

def get_all_joints(root):
    """
    指定したルート以下の全てのジョイントを取得してリストで返す

    Args:
        root (str): 検索のルートとなるノード名

    Returns:
        list: 検索したジョイント名を格納したリスト
    """
    # 検索結果を格納するリストを初期化
    result = []
    # ルートの子ノードを順番に調べる
    children = cmds.listRelatives(root, children=True, fullPath=True)
    if children is None:
        children = []
    for child in children:
        # 子ノードがジョイントである場合、結果リストに追加
        if cmds.nodeType(child) == "joint":
            result.append(child)
        # 子ノードにさらに子ノードがある場合、再帰的に検索する
        if cmds.listRelatives(child, children=True, fullPath=True) is not None:
            result.extend(get_all_joints(child))
    return result

def get_all_constraints(node):
    """指定されたノード以下に存在する全てのコンストレイントをリストで返す

    Args:
        node (str): 検索対象となるノード名

    Returns:
        list: 検索対象となるノード以下に存在する全てのコンストレイントの名前を含むリスト
    """
    # 検索結果を格納するリストを初期化
    result = []
    # ルートの子ノードを順番に調べる
    children = cmds.listRelatives(node, children=True, fullPath=True)
    if children is None:
        children = []
    for child_node in children:
        child_node_type = cmds.ls(child_node, showType=True)[1]
        # 子ノードがコンストレイントである場合、結果リストに追加
        if ("constraint" in child_node_type):
            result.append(child_node)
        if cmds.listRelatives(child_node, children=True, fullPath=True) is not None:
            result.extend(get_all_constraints(child_node))
    return result

def get_constraint_connection(node):
    """
    引数に渡したコンストレイントノードのsourceとdestinationとをタプルにして返す
    :param node: コンストレイントノード
    :type node: str
    :return: sourceとdestinationのタプル
    :rtype: tuple
    """
    # コネクションが存在しない場合は[None]を返す
    source = cmds.listConnections(node+".target[0].targetParentMatrix", source=True, destination=False) or [None]
    destination = cmds.listConnections(node+".constraintParentInverseMatrix", source=True, destination=False) or [None]
    return (source[0], destination[0])

def duplicate_root(root, name="new"):
    """
    root以下のパスを変更しないように複製する
    複製したrootの親に新しいグループノードが追加される
    :param root: 複製するルートノード
    :param name: 複製後の名前
    :return: 複製されたルートノード
    """
    # パスを揃えるために複製元をグループノードで包む
    temp = cmds.group(root, name="root_temp")

    # 複製
    duplicated_root = cmds.duplicate(temp, name=name, returnRootsOnly=True)

    # 複製元のグループノードを削除
    cmds.delete(temp)

    # 複製されたノードをグループ化
    duplicated_root = cmds.group(duplicated_root, name="duplicated_root")

    return duplicated_root

def get_bake_source_joint_attr_dict(joint_list, start_frame, end_frame, epsilon=1e-4):
    """指定した期間中にアトリビュートが変化したジョイントと、そのジョイントの変化したアトリビュートを返す

    Args:
        joint_list (list[str]): 取得するジョイントのリスト
        start_frame (int): ベイクの開始フレーム
        end_frame (int): ベイクの終了フレーム
        epsilon (float): 許容誤差。アトリビュートの値がこれ以上変化しなければ変化がないと判断する。

    Returns:
        dict: キーは変化があったジョイント名、値は変化したアトリビュートのリスト(translate, rotate, scale)を示すブール値のタプル
    """
    pre_values_dict = {}
    bake_source_joint_attr_dict = {}

    for frame in range(start_frame, end_frame + 1):
        for joint in joint_list:
            # そのフレームの各アトリビュートを取得
            values = cmds.getAttr(joint+".translate", joint+".rotate", joint+".scale", time=frame)
            # 直前のアトリビュートの値が辞書に登録されていなかったら登録
            if joint not in pre_values_dict:
                pre_values_dict[joint] = values
            else:
                changed_attrs = [False, False, False]
                for attr_index in range(3):
                    for axis_index in range(3):
                        if abs(values[attr_index][axis_index] - pre_values_dict[joint][attr_index][axis_index]) > epsilon:
                            changed_attrs[attr_index] = True
                            break
                # アトリビュートが1つでも変化してたら辞書に追加
                if any(changed_attrs):
                    bake_source_joint_attr_dict[joint] = tuple(changed_attrs)
                    pre_values_dict[joint] = values

    return bake_source_joint_attr_dict

def get_all_transforms(root):
    """階層下のトランスフォームを全て検索してリストで返す"""
    # 検索結果を格納するリストを初期化
    result = []
    # ルートの子ノードを順番に調べる
    children = cmds.listRelatives(root, children=True, fullPath=True)
    if children is None:
        children = []
    for child in children:
        # トランスフォームノードのみリストに追加
        if cmds.nodeType(child) == "transform":
            result.append(child)
        # 子ノードにさらに子ノードがある場合、再帰的に検索する
        if cmds.listRelatives(child, children=True, fullPath=True) is not None:
            result.extend(get_all_transforms(child))
    return result

def get_all_shapes(transforms):
    """トランスフォームノードのリストから接続されているシェイプノードをリストで返す"""
    result = []
    for transform in transforms:
        shape = cmds.listRelatives(transform, fullPath=True, noIntermediate=True, shapes=True)
        if shape is not None:
            result.extend(shape)
    return result

def get_all_histories(shapes):
    """シェイプノードのリストから、シェイプノードをキー、そのヒストリーのリストをバリューにした辞書を返す"""
    result = {}
    for shape in shapes:
        history = cmds.listHistory(shape, pruneDagObjects=True, interestLevel=2)
        result[shape] = history
    return result

def get_all_skin_clusters(shapes):
    """
    シェイプノードのリストから、シェイプノードをキー、そのスキンクラスターをバリューにした辞書を返す。
    スキンクラスターが存在しない場合は、辞書から除外する。
    :param shapes: シェイプノードのリスト
    :return: シェイプノードとスキンクラスターの辞書
    """
    histories = get_all_histories(shapes)
    skin_clusters = {}
    for shape in shapes:
        skin_cluster = cmds.ls(histories[shape], type="skinCluster")
        # スキンクラスターが存在する場合にのみ、辞書に追加する
        if skin_cluster:
            skin_clusters[shape] = skin_cluster[0]
    return skin_clusters

def get_all_influences(skin_clusters):
    """スキンクラスターのリストから、スキンクラスターをキー、そのインフルエンスのリストをバリューにした辞書を返す。
    :param skin_clusters: スキンクラスターのリスト
    :return: スキンクラスターとインフルエンスの辞書
    """
    result = {}
    for skin_cluster in skin_clusters:
        influences = cmds.skinCluster(skin_cluster, q=True, influence=True)
        influence_full_paths = cmds.ls(influences, long=True)
        result[skin_cluster] = influence_full_paths
    return result

def get_fixed_path(root_name, path, before_name = False):
    """
    指定されたパスの親にルートの名前を追加したパスを返す
    before_nameがTrueの場合、逆にルートの名前を追加する前のパスを返す
    :param root_name: ルートの名前
    :param path: 修正前のパス
    :param before_name: 修正前の名前を返す場合はTrue、修正後の名前を返す場合はFalse
    :return: 修正後のパス
    """
    if before_name:
        return path[len(root_name)+1:]
    else:
        if path[0] == "|":
            return root_name + path
        else:
            return root_name + "|" + path