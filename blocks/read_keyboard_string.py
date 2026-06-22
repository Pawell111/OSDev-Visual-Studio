class ReadKeyboardString:
    name = "Read String"
    category = "I/O (Hardware)"
    description = "Reads a string from the keyboard into a variable."
    color = "#e74c3c"
    inputs = ["in"]
    outputs = ["next"]
    properties = [{"name": "var_name", "type": "string", "default": "user_input"}]
    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        var = node.properties.get("var_name", "str")
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Read String into {var} ---", node.id))
            out.append((f"{pad}read_string({var});", node.id))
        else:
            out.append((f"{pad}; --- Read String (C only) ---", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out