class MathDivide:
    name = "Divide"
    category = "Math / Logic"
    description = "Divides A by B. Result is stored in a variable."
    color = "#f39c12"
    inputs = ["in"]
    outputs = ["next"]
    properties = [
        {"name": "result", "type": "string", "default": "quotient"},
        {"name": "a", "type": "string", "default": "0"},
        {"name": "b", "type": "string", "default": "1"}
    ]
    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        res = node.properties.get("result", "res")
        a = node.properties.get("a", "0")
        b = node.properties.get("b", "1")
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Divide: {res} = {a} / {b} ---", node.id))
            out.append((f"{pad}{res} = {a} / {b};", node.id))
        else:
            out.append((f"{pad}; --- Divide ---", node.id))
            out.append((f"{pad}mov eax, {a}", node.id))
            out.append((f"{pad}cdq", node.id))
            out.append((f"{pad}mov ebx, {b}", node.id))
            out.append((f"{pad}idiv ebx", node.id))
            out.append((f"{pad}mov [{res}], eax", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out