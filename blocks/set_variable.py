class SetVariable:
    name = "Set Variable"
    category = "Variables"
    description = "Updates an integer variable with a value."
    color = "#16a085"
    inputs = ["in"]
    outputs = ["next"]
    properties = [
        {"name": "name", "type": "string", "default": "my_var"},
        {"name": "value", "type": "string", "default": "0"}
    ]
    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        name = node.properties.get("name", "var")
        val = node.properties.get("value", "0")
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Set Variable {name} ---", node.id))
            out.append((f"{pad}{name} = {val};", node.id))
        else:
            out.append((f"{pad}; --- Set Variable {name} ---", node.id))
            out.append((f"{pad}mov dword [{name}], {val}", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out