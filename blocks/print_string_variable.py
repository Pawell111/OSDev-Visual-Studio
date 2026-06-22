class PrintStringVariable:
    name = "Print String"
    category = "I/O (Hardware)"
    description = "Prints the value of a string variable to the screen."
    color = "#e74c3c"
    inputs = ["in"]
    outputs = ["next"]
    properties = [
        {"name": "var_name", "type": "string", "default": "user_input"},
        {"name": "newline", "type": "choice", "default": "True", "options": ["True", "False"]}
    ]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        var = node.properties.get("var_name", "str")
        newline = node.properties.get("newline", "True") == "True"
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Print String {var} ---", node.id))
            out.append((f"{pad}print_string({var});", node.id))
            if newline:
                out.append((f'{pad}print_string("\\n");', node.id))
        else:
            out.append((f"{pad}; Print String (C only)", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out