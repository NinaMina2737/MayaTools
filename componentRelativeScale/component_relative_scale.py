#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import maya.cmds as cmds

def calculate_vertex_positions_center(pos_list):
    """
    Calculates the center point of the given vertex positions.

    Args:
        pos_list (list): A list of vertex positions in the format of [x, y, z].

    Returns:
        A list representing the center point in the format of [x, y, z].

    Raises:
        ValueError: If the given list is empty.
    """
    # Raise an exception if the given list is empty
    if not pos_list:
        raise ValueError("The given list is empty.")

    # Calculate the center point
    center = [0, 0, 0]
    for pos in pos_list:
        center[0] += pos[0]
        center[1] += pos[1]
        center[2] += pos[2]
    center[0] /= len(pos_list)
    center[1] /= len(pos_list)
    center[2] /= len(pos_list)

    # Return the calculated center point
    return center

def calculate_bounding_box(vertices):
    """
    Calculates the bounding box of the given vertices.

    Args:
        vertices (list): A list of vertices in the format of [(x, y, z), (x, y, z), ...].

    Returns:
        A list representing the two diagonal points of the bounding box in the format of [(x, y, z), (x, y, z)].

    Raises:
        ValueError: If the given list is empty.
    """
    # Raise an exception if the given list is empty
    if not vertices:
        raise ValueError("The given list is empty.")

    # Set the initial values for the bounding box
    min_x, max_x = vertices[0][0], vertices[0][0]
    min_y, max_y = vertices[0][1], vertices[0][1]
    min_z, max_z = vertices[0][2], vertices[0][2]

    # Update the bounding box values for each vertex
    for vertex in vertices:
        x, y, z = vertex

        if x < min_x:
            min_x = x
        elif x > max_x:
            max_x = x

        if y < min_y:
            min_y = y
        elif y > max_y:
            max_y = y

        if z < min_z:
            min_z = z
        elif z > max_z:
            max_z = z

    # Return the two diagonal points of the bounding box
    return [(min_x, min_y, min_z), (max_x, max_y, max_z)]

def get_vertex_positions(is_bbox=False):
    """
    Gets the vertex positions of the selected vertices, edges, or faces.

    Args:
        is_bbox (bool): Whether to calculate the bounding box of the selection instead of the vertex positions.

    Returns:
        A list of vertex positions in the format of [(x, y, z), (x, y, z), ...].

    Raises:
        ValueError: If nothing is selected.
        ValueError: If the selection is invalid.
    """
    # Get the current selection
    selected_items = cmds.ls(long=True, selection=True)

    # Raise an exception if nothing is selected
    if not selected_items:
        raise ValueError("Nothing is selected.")

    # Determine the type of selection (vertex, edge, or face)
    selection_type_map = {".vtx": 31, ".e": 32, ".f": 34}
    selection_type = None
    for key in selection_type_map:
        if key in selected_items[0]:
            selection_type = key
            break

    # Raise an exception if the selection is invalid
    if selection_type is None:
        raise ValueError("Invalid selection. You can only select 'vtx', 'edge', or 'face'.")

    # Filter the selection to only include vertices, edges, or faces
    selection_mask = selection_type_map[selection_type]
    selected_items = cmds.filterExpand(selected_items, selectionMask=selection_mask)

    # Create a list of the positions of the selected vertices, edges, or faces
    pos_list = []
    for item_name in selected_items:
        # Get the world space position of each vertex, edge, or face in the selection
        item_positions = cmds.xform(item_name, q=True, worldSpace=True, translation=True)

        # Separate the positions into groups of 3
        item_positions = [item_positions[i:i + 3] for i in range(0, len(item_positions), 3)]

        for pos in item_positions:
            # Add each vertex position of selected item in the format of [x, y, z] to the pos_list
            pos_list.append((pos[0], pos[1], pos[2]))

    # Calculate the bounding box if is_bbox is True
    if is_bbox:
        # Calculate the vertices of the bounding box
        bounding_box_vertices = calculate_bounding_box(pos_list)

        # Make pos_list equal to the bounding box vertices
        pos_list = bounding_box_vertices

    return pos_list

def scale_from_selection_pivot(x_scale, y_scale, z_scale, is_bbox=True):
    """
    Scales the selected vertices, edges, or faces from the center point of the selection.

    Args:
        x_scale (float): The scale factor along the x-axis.
        y_scale (float): The scale factor along the y-axis.
        z_scale (float): The scale factor along the z-axis.
        is_bbox (bool): Whether to calculate the bounding box of the selection instead of the vertex positions.

    Raises:
        ValueError: If all of the scale values are within 1e-6 of 1.0.
    """

    # Get the vertex positions of the selection
    pos_list = get_vertex_positions(is_bbox)

    # Calculate the center point of the selection
    pivot_center = calculate_vertex_positions_center(pos_list)

    # If no valid center point is found, exit the method
    if pivot_center is None:
        return

    # If all of the scale values are within 1e-6 of 1.0, raise a ValueError
    epsilon = 1e-6
    if abs(x_scale - 1.0) < epsilon and abs(y_scale - 1.0) < epsilon and abs(z_scale - 1.0) < epsilon:
        raise ValueError("All of the scale values are within 1e-6 of 1.0.")

    # Apply the scale transformation using Maya's built-in scale function
    cmds.scale(x_scale, y_scale, z_scale, pivot=pivot_center, relative=True)

def execute(x_scale=1.0, y_scale=1.0, z_scale=1.0, is_bbox=True):
    """
    Executes the script.

    Args:
        x_scale (float): The scale factor along the x-axis.
        y_scale (float): The scale factor along the y-axis.
        z_scale (float): The scale factor along the z-axis.
        is_bbox (bool): Whether to calculate the bounding box of the selection instead of the vertex positions.

    Raises:
        ValueError: If nothing is selected.
        ValueError: If the selection is invalid.
        ValueError: If all of the scale values are within 1e-6 of 1.0.
    """
    try:
        # Open an undo chunk
        cmds.undoInfo(openChunk=True)
        # Scale the polygon based on the given scale values and the center point of the selected vertices, edges, or faces
        scale_from_selection_pivot(x_scale, y_scale, z_scale, is_bbox)
    except Exception as e:
        # Print the error message
        cmds.warning("An error occurred: {}".format(str(e)))
        # Print the file name where the error occurred
        cmds.warning("File name: {}".format(__file__))
        # Print the line number where the error occurred
        cmds.warning("Line number: {}".format(e.__traceback__.tb_lineno))
    finally:
        # Close the undo chunk
        cmds.undoInfo(closeChunk=True)

if __name__ == '__main__':
    # Execute the script
    execute()
