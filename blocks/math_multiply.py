class MathMultiply:
    name = "Multiply"
    category = "Math / Logic"
    description = "Multiplies A and B. Result is stored in a variable."
    color = "#f39c12"
    inputs = ["in"]
    outputs = ["next"]
    properties = [
        {"name": "result", "type": "string", "default": "product"},
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
            out.append((f"{pad}// --- Multiply: {res} = {a} * {b} ---", node.id))
            out.append((f"{pad}{res} = {a} * {b};", node.id))
        else:
            out.append((f"{pad}; --- Multiply ---", node.id))
            out.append((f"{pad}mov eax, {a}", node.id))
            out.append((f"{pad}imul eax, {b}", node.id))
            out.append((f"{pad}mov [{res}], eax", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out