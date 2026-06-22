class Node:
    _next_id = 1
    def __init__(self, node_type, x=100, y=100):
        self.id = Node._next_id
        Node._next_id += 1
        self.type = node_type
        self.x = x
        self.y = y
        self.w = 150
        self.h = 64
        self.properties = {}