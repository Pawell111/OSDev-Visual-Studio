class IfVariable:
    name = "If Variable (Int)"
    category = "Control"
    description = "Branches execution by comparing an integer variable to a number."
    color = "#27ae60"
    inputs = ["in"]
    outputs = ["true", "false"]
    properties = [
        {"name": "var_name", "type": "string", "default": "x"},
        {"name": "op", "type": "choice", "default": "==", "options": ["==", "!=", ">", "<", ">=", "<="]},
        {"name": "value", "type": "int", "default": 0}
    ]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        var = node.properties.get("var_name", "x")
        op = node.properties.get("op", "==")
        val = node.properties.get("value", 0)
        out = []
        if lang == "c":
            out.append((f"{pad}// --- If {var} {op} {val} ---", node.id))
            out.append((f"{pad}if ({var} {op} {val}) {{", node.id))
            out += context.generate_chain(node.id, "true", indent + 1)
            out.append((f"{pad}}} else {{", node.id))
            out += context.generate_chain(node.id, "false", indent + 1)
            out.append((f"{pad}}}", node.id))
        else:
            out.append((f"{pad}; --- If {var} {op} {val} ---", node.id))
            out.append((f"{pad}mov eax, [{var}]", node.id))
            out.append((f"{pad}cmp eax, {val}", node.id))
            if op == "==": out.append((f"{pad}jne .else_{node.id}", node.id))
            elif op == "!=": out.append((f"{pad}je .else_{node.id}", node.id))
            elif op == ">": out.append((f"{pad}jle .else_{node.id}", node.id))
            elif op == "<": out.append((f"{pad}jge .else_{node.id}", node.id))
            elif op == ">=": out.append((f"{pad}jl .else_{node.id}", node.id))
            elif op == "<=": out.append((f"{pad}jg .else_{node.id}", node.id))
            
            out += context.generate_chain(node.id, "true", indent)
            out.append((f"{pad}jmp .end_if_{node.id}", node.id))
            out.append((f"{pad}.else_{node.id}:", node.id))
            out += context.generate_chain(node.id, "false", indent)
            out.append((f"{pad}.end_if_{node.id}:", node.id))
        return out