class IfVariableString:
    name = "If Variable (String)"
    category = "Control"
    description = "Branches execution by comparing a string variable to text."
    color = "#27ae60"
    inputs = ["in"]
    outputs = ["true", "false"]
    properties = [
        {"name": "var_name", "type": "string", "default": "user_input"},
        {"name": "op", "type": "choice", "default": "==", "options": ["==", "!="]},
        {"name": "value", "type": "string", "default": "hello"}
    ]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        var = node.properties.get("var_name", "str")
        op = node.properties.get("op", "==")
        val = node.properties.get("value", "").replace("\\", "\\\\").replace('"', '\\"')
        
        out = []
        if lang == "c":
            cmp_str = f"strcmp({var}, \"{val}\")"
            cond = f"{cmp_str} == 0" if op == "==" else f"{cmp_str} != 0"
            
            out.append((f"{pad}// --- If {var} {op} \"{val}\" ---", node.id))
            out.append((f"{pad}if ({cond}) {{", node.id))
            out += context.generate_chain(node.id, "true", indent + 1)
            out.append((f"{pad}}} else {{", node.id))
            out += context.generate_chain(node.id, "false", indent + 1)
            out.append((f"{pad}}}", node.id))
        else:
            out.append((f"{pad}; If Variable String (C only)", node.id))
        return out