class ReadKeyboardInt:
    name = "Read Int"
    category = "I/O (Hardware)"
    description = "Reads an integer from the keyboard into a variable."
    color = "#e74c3c"
    inputs = ["in"]
    outputs = ["next"]
    properties = [{"name": "var_name", "type": "string", "default": "user_num"}]
    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        var = node.properties.get("var_name", "num")
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Read Int into {var} ---", node.id))
            out.append((f"{pad}{var} = read_int();", node.id))
        else:
            out.append((f"{pad}; --- Read Int (C only) ---", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out