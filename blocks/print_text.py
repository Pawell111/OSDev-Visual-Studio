class PrintText:
    name = "Print"
    category = "I/O"
    description = "Outputs text to the screen using the currently active colors."
    color = "#2e2e2e"
    inputs = ["in"]
    outputs = ["next"]
    properties = [
        {"name": "text", "type": "string", "default": "Hello, OS World!"},
        {"name": "newline", "type": "choice", "default": "True", "options": ["True", "False"]}
    ]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        text = node.properties.get("text", "").replace("\\", "\\\\").replace('"', '\\"')
        newline = node.properties.get("newline", "True") == "True"
        suffix = "\\n" if newline else ""
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Print ---", node.id))
            out.append((f'{pad}print_string("{text}{suffix}");', node.id))
        else:
            text_asm = text.replace("'", "\\'")
            out.append((f"{pad}; --- Print ---", node.id))
            # In NASM, 10 is the ASCII code for newline
            suffix_asm = ", 10" if newline else ""
            context.msgs.append(f"msg_{node.id}: db '{text_asm}'{suffix_asm}, 0")
            out.append((f"{pad}mov si, msg_{node.id}", node.id))
            out.append((f"{pad}call print_string", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out