class Node:
    """
    create tree node
    """
    def __init__(self, name):
        self.children = []
        self.probes = []
        self.name = name
        self.node_id = id(self)
        # print("[*] create node {} ({})".format(self.name, self.node_id))

    def add_child(self, child, probe_id=None):
        """
        add a child to a node. If the child is already in the node's children list, then simply pass that child node.
        If not, then create a new node, and put it in the children node list.
        :param child:
        :param probe_id: default 0 is for node which does not contain any probe
        :return: either newly created child or the existing child
        """
        node = None
        matching_nodes = [x for x in self.children if x.name == child.name] # see if the added node has already in its children list
        # print("[*] add children with the name {}.. matching_nodes: {}".format(child.name, matching_nodes))
        if len(matching_nodes) > 0:
            node = matching_nodes[0]
            if probe_id is not None:
                node.probes = probe_id
            # print("\t[*] current node: {}".format(node.name))
        if node is None:
            if probe_id is not None:
                child.probes = probe_id
            self.children.append(child)
            node = child
            # print("\t[*] node {} is appended to {} child list".format(node.name, self.name))
        return node

    def __repr__(self):
        return str(self.name) + '->' + str(self.children)
