class BlockTemplate:
    name = "Template"
    category = "Custom"
    description = "Copy this file to create a new block."
    color = "#2e2e2e"
    inputs = ["in"]
    outputs = ["next"]
    properties = []
    
    def generate(self, node, lang, indent, context):
        # lang is 'c' or 'asm'
        # node is the Node instance (has .id, .properties)
        # indent is the integer indentation level
        # context has .generate_chain(from_id, port, indent) which returns [(line, node_id), ...]
        pad = "    " * indent
        out = []
        out.append((f"{pad}// My custom block code", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out