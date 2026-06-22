class Compare:
    name = "Compare"
    category = "Math / Logic"
    description = "Compares A and B. Result is 1 (true) or 0 (false). Can be fed to an If block."
    color = "#f39c12"
    inputs = ["in"]
    outputs = ["next"]
    properties = [
        {"name": "result", "type": "string", "default": "is_equal"},
        {"name": "a", "type": "string", "default": "0"},
        {"name": "b", "type": "string", "default": "0"},
        {"name": "op", "type": "choice", "default": "==", "options": ["==", "!=", ">", "<", ">=", "<="]}
    ]
    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        res = node.properties.get("result", "res")
        a = node.properties.get("a", "0")
        b = node.properties.get("b", "0")
        op = node.properties.get("op", "==")
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Compare: {res} = {a} {op} {b} ---", node.id))
            out.append((f"{pad}{res} = ({a} {op} {b});", node.id))
        else:
            out.append((f"{pad}; --- Compare ---", node.id))
            out.append((f"{pad}mov eax, {a}", node.id))
            out.append((f"{pad}cmp eax, {b}", node.id))
            if op == "==": out.append((f"{pad}sete al", node.id))
            elif op == "!=": out.append((f"{pad}setne al", node.id))
            elif op == ">": out.append((f"{pad}setg al", node.id))
            elif op == "<": out.append((f"{pad}setl al", node.id))
            elif op == ">=": out.append((f"{pad}setge al", node.id))
            elif op == "<=": out.append((f"{pad}setle al", node.id))
            out.append((f"{pad}movzx {res}, al", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out