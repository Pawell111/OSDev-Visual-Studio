class IfBlock:
    name = "If"
    category = "Control"
    description = "Branches based on a condition."
    color = "#2e2e2e"
    inputs = ["in"]
    outputs = ["true", "false"]
    properties = [{"name": "condition", "type": "string", "default": "1"}]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        cond = node.properties.get("condition", "1")
        out = []
        if lang == "c":
            out.append((f"{pad}// --- If {cond} ---", node.id))
            out.append((f"{pad}if ({cond}) {{", node.id))
            out += context.generate_chain(node.id, "true", indent + 1)
            out.append((f"{pad}}} else {{", node.id))
            out += context.generate_chain(node.id, "false", indent + 1)
            out.append((f"{pad}}}", node.id))
        else:
            out.append((f"{pad}; --- If {cond} ---", node.id))
            out.append((f"{pad}mov eax, {cond}", node.id))
            out.append((f"{pad}cmp eax, 0", node.id))
            out.append((f"{pad}je .else_{node.id}", node.id))
            out += context.generate_chain(node.id, "true", indent)
            out.append((f"{pad}jmp .end_if_{node.id}", node.id))
            out.append((f"{pad}.else_{node.id}:", node.id))
            out += context.generate_chain(node.id, "false", indent)
            out.append((f"{pad}.end_if_{node.id}:", node.id))
        return out