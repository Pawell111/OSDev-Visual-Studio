class ClearScreen:
    name = "Clear Screen"
    category = "I/O"
    description = "Clears all text from the screen."
    color = "#2e2e2e"
    inputs = ["in"]
    outputs = ["next"]
    properties = []

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Clear Screen ---", node.id))
            out.append((f"{pad}clear_screen();", node.id))
        else:
            out.append((f"{pad}; --- Clear Screen ---", node.id))
            out.append((f"{pad}call clear_screen", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out