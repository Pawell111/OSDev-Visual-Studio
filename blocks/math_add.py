class MathAdd:
    name = "Add"
    category = "Math / Logic"
    description = "Adds two numbers or variables. Result is stored in a variable."
    color = "#f39c12"
    inputs = ["in"]
    outputs = ["next"]
    properties = [
        {"name": "result", "type": "string", "default": "sum"},
        {"name": "a", "type": "string", "default": "0"},
        {"name": "b", "type": "string", "default": "0"}
    ]
    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        res = node.properties.get("result", "res")
        a = node.properties.get("a", "0")
        b = node.properties.get("b", "0")
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Add: {res} = {a} + {b} ---", node.id))
            out.append((f"{pad}{res} = {a} + {b};", node.id))
        else:
            out.append((f"{pad}; --- Add ---", node.id))
            out.append((f"{pad}mov eax, {a}", node.id))
            out.append((f"{pad}add eax, {b}", node.id))
            out.append((f"{pad}mov [{res}], eax", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out