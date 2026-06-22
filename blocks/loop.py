class Loop:
    name = "Loop"
    category = "Control"
    description = "Repeats the connected body N times."
    color = "#2e2e2e"
    inputs = ["in"]
    outputs = ["body", "done"]
    properties = [{"name": "count", "type": "int", "default": 5}]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        count = node.properties.get("count", 5)
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Loop {count} times ---", node.id))
            out.append((f"{pad}for (int i=0; i<{count}; i++) {{", node.id))
            out += context.generate_chain(node.id, "body", indent + 1)
            out.append((f"{pad}}}", node.id))
        else:
            out.append((f"{pad}; --- Loop {count} times ---", node.id))
            out.append((f"{pad}mov ecx, {count}", node.id))
            out.append((f"{pad}.loop_{node.id}:", node.id))
            out.append((f"{pad}    push ecx", node.id))
            out += context.generate_chain(node.id, "body", indent + 1)
            out.append((f"{pad}    pop ecx", node.id))
            out.append((f"{pad}    loop .loop_{node.id}", node.id))
        out += context.generate_chain(node.id, "done", indent)
        return out