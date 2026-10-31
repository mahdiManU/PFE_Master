"""
bpmn_utils.py - small helpers shared by all verification modules.

The BPMN file is read as plain text, line by line. These helpers hold the
operations that several modules need, so each one exists only once.
"""
import re

# ---------------------------------------------------------------------------
# Colour palettes used to highlight faulty elements in the diagram.
# Each palette is (stroke colour, fill colour).
# ---------------------------------------------------------------------------
PALETTE_STRUCTURAL = ("#831311", "#ffcdd2")      # red    - structural errors (S)
PALETTE_CONTRADICTION = ("#5b176d", "#e1bee7")   # purple - contradictions (C)
PALETTE_MISSING_INFO = ("#6b3c00", "#ffe0b2")    # orange - missing information (MI)


def color_task(bpmnfile, id_task, palette):
    """
    Highlight one element in the BPMN diagram by adding colour attributes
    to its <bpmndi:BPMNShape> line (the graphical part of the file).

    bpmnfile : path of the .bpmn file (modified in place)
    id_task  : id of the element to colour, e.g. "Activity_0abc123"
    palette  : one of the PALETTE_* constants above

    An element that is already coloured is left untouched.
    """
    stroke, fill = palette
    new_lines = []
    with open(bpmnfile, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if ("<bpmndi:BPMNShape" in line) and (id_task in line) and ("bioc:stroke" not in line):
            new_lines.append(
                line[:-2]
                + f' bioc:stroke="{stroke}" bioc:fill="{fill}"'
                + f' color:background-color="{fill}" color:border-color="{stroke}">\n'
            )
        else:
            new_lines.append(line)
    with open(bpmnfile, 'w') as file:
        file.truncate(0)
        file.writelines(new_lines)


def supprimer_doublons(liste):
    """Remove duplicates from a list while keeping the original order."""
    vue = []
    resultat = []
    for element in liste:
        if element not in vue:
            resultat.append(element)
            vue.append(element)
    return resultat


def get_lane_id_from_flow_node(bpmn_file_path, flow_node_id):
    """
    Return the id of the lane (organisational role) that contains the given
    element, or "" if none is found. Used to find the role of a task.
    """
    lane_id = ""
    with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if "<lane id=" in line:
            lane_match = re.search(r'<lane id="([^"]+)"', line)
            if lane_match:
                current_lane_id = lane_match.group(1)

        if "<flowNodeRef>" in line and flow_node_id in line:
            flow_node_match = re.search(r'<flowNodeRef>(.*?)</flowNodeRef>', line)
            if flow_node_match and flow_node_match.group(1) == flow_node_id:
                lane_id = current_lane_id
                break

    return lane_id