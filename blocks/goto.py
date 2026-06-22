class GoTo:
    name = "Go to"
    category = "Control"
    description = "Jumps execution directly to the block connected to its output."
    color = "#27ae60"
    inputs = ["in"]
    outputs = ["next"]
    properties = []

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        out = []
        if lang == "c":
            conn = next((c for c in context.connections if c["from_node"] == node.id and c["from_port"] == "next"), None)
            if conn:
                target_id = conn["to_node"]
                out.append((f"{pad}goto goto_target_{target_id};", node.id))
            else:
                out.append((f"{pad}// Go to block has no target!", node.id))
        else:
            out.append((f"{pad}; Go to block (C only)", node.id))
        return out