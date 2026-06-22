class DeclareConstant:
    name = "Declare Constant"
    category = "Variables"
    description = "Declares an integer variable with an initial value."
    color = "#16a085"
    inputs = ["in"]
    outputs = ["next"]
    properties = [
        {"name": "name", "type": "string", "default": "MAX_VAL"},
        {"name": "value", "type": "int", "default": 10}
    ]
    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        name = node.properties.get("name", "CONST")
        val = node.properties.get("value", 0)
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Declare Constant {name} ---", node.id))
            out.append((f"{pad}{name} = {val};", node.id))
        else:
            out.append((f"{pad}; --- Declare Constant {name} ---", node.id))
            out.append((f"{pad}mov dword [{name}], {val}", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out