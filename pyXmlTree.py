""" Helper Functions for grabbing SpeedTree data from an exported .xml file """
import xml.etree.cElementTree as ET

class TreeNode:
    """ TreeNode class """
    def __init__(self, XML_node):
        self.name = XML_node.attrib['Name']
        self.id = float(XML_node.attrib['ID'])
        self.parent_id = float(XML_node.attrib['ParentID'])
        self.x, self.y, self.z = get_points(XML_node)
        self.abs_x = [x  + float(XML_node.attrib['AbsX']) for x in self.x]
        self.abs_y = [y  + float(XML_node.attrib['AbsY']) for y in self.y]
        self.abs_z = [z  + float(XML_node.attrib['AbsZ']) for z in self.z]


# function opens a .xml file and returns an xml object
def open_xml(file_name):
    tree = ET.parse(file_name)
    root = tree.getroot()
    return root

def get_all_tree_nodes(root):
    """ Returns a list of all tree nodes """
    tree_nodes = []

    Objects = None
    # given the root of the xml, get the Objects 'child'
    for child in root:
        if child.tag == 'Objects':
            Objects = child
            break
    
    # get all the tree nodes, they are children of Objects
    for child in Objects:
        if child.tag == 'Object' and child.attrib['ID'] != '0':
            tree_nodes.append(child)

    return tree_nodes

def get_points(node):
    """ Returns the xyz coordinates of all points in a node """
    x, y, z = [], [], []
    for child in node:
        if child.tag == 'Points':
            for dimension in child:
                if dimension.tag == 'X':
                    x = [float(i) for i in dimension.text.split()]
                if dimension.tag == 'Y':
                    y = [float(i) for i in dimension.text.split()]
                if dimension.tag == 'Z':
                    z = [float(i) for i in dimension.text.split()]
    return x, y, z



""" Returns 3 lists of all tree nodes """
# Returns a tuple of Trunk, Branch, Frond nodes
def get_tree_pointcloud(file_path):
    debug = False

    my_xml_tree_nodes = open_xml(file_path)

    # get all the tree nodes in raw XML unparsed format
    my_xml_tree_nodes = get_all_tree_nodes(my_xml_tree_nodes)
    
    Tree_Nodes = []
    for node in my_xml_tree_nodes:
        Tree_Nodes.append(TreeNode(node))

    # Unique node names are : Trunk, Branch, Cap, Shell, Frond
    # get the unique node names
    unique_node_names = []
    number_of_node_occurances = []
    number_of_points_in_node = []
    for node in Tree_Nodes:
        parsed_node_name = node.name.split('_')[0].lower()
        if parsed_node_name not in unique_node_names:
            unique_node_names.append(parsed_node_name)
            number_of_node_occurances.append(1)
            number_of_points_in_node.append(len(node.abs_x))
        else:
            number_of_node_occurances[unique_node_names.index(parsed_node_name)] += 1
            number_of_points_in_node[unique_node_names.index(parsed_node_name)] += len(node.abs_x)
    if debug:
        print(unique_node_names)
        print(number_of_node_occurances)
        print(number_of_points_in_node)

    # get all nodes with parent id of 0 (Trunk)
    trunk_keywords = ['trunk', 'cavity', 'shell', 'lump', 'roots', 'knot']
    trunk_nodes = [node for node in Tree_Nodes if any(keyword in node.name.lower().split('_')[0] for keyword in trunk_keywords)]
    if debug:
        print("Number of Trunks:", len(trunk_nodes))
    # for every trunk, get the total number of all points
    total_points = 0
    for trunk in trunk_nodes:
        total_points += len(trunk.x)
    if debug:
        print("Total Number of Trunk Points:", total_points)

    # get all nodes with name that start with the word 
    branch_keywords = ['bifurcating', 'branch', 'big', 'cap', 'large','twigs','little']
    parent_id_1 = [node for node in Tree_Nodes if any(keyword in node.name.lower().split('_')[0] for keyword in branch_keywords)]
    if debug:
        print("Number of Branches: " + str(len(parent_id_1)))
    # for every branch, get the total number of all points
    total_points = 0
    for node in parent_id_1:
        total_points += len(node.x)
    if debug:
        print("Total Number of Branch Points: " + str(total_points))

    # get all nodes with name that start with the word 'Branch' or 'Shell'
    leaf_keywords = ['batchedleaf','frond','leaf']
    parent_id_2 = [node for node in Tree_Nodes if any(keyword in node.name.lower().split('_')[0] for keyword in leaf_keywords)]
    if debug:
        print("Number of Nodes with leaves: " + str(len(parent_id_2)))
    # for every second order branch, get the total number of all points
    total_points = 0
    for node in parent_id_2:
        total_points += len(node.x)
    if debug:
        print("Total Number of Leaf Points: " + str(total_points))

    return trunk_nodes, parent_id_1, parent_id_2

def get_tree_pointcloud_from_xml(file_path):
    trunk_nodes, branch_nodes, leaf_nodes = get_tree_pointcloud(file_path)

    x = []
    y = []
    z = []

    for node in trunk_nodes:
        x += node.abs_x
        y += node.abs_y
        z += node.abs_z

    for node in branch_nodes:
        x += node.abs_x
        y += node.abs_y
        z += node.abs_z

    for node in leaf_nodes:
        x += node.abs_x
        y += node.abs_y
        z += node.abs_z
    
    return x,y,z

def get_trunk_pointcloud_from_xml(file_path):
    trunk_nodes, _, _ = get_tree_pointcloud(file_path)

    x = []
    y = []
    z = []

    for node in trunk_nodes:
        x += node.abs_x
        y += node.abs_y
        z += node.abs_z

    return x,y,z

def get_branch_pointcloud_from_xml(file_path):
    _, branch_nodes, _ = get_tree_pointcloud(file_path)

    x = []
    y = []
    z = []

    for node in branch_nodes:
        x += node.abs_x
        y += node.abs_y
        z += node.abs_z

    return x,y,z

def get_leaf_pointcloud_from_xml(file_path):
    _, _, leaf_nodes = get_tree_pointcloud(file_path)

    x = []
    y = []
    z = []

    for node in leaf_nodes:
        x += node.abs_x
        y += node.abs_y
        z += node.abs_z

    return x,y,z
