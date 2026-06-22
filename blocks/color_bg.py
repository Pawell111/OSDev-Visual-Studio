from blocks.color_fg import VGA_COLORS, VGA_CODES

class ColorBG:
    name = "BG Color"
    category = "I/O"
    description = "Sets the background color for subsequent Print blocks."
    color = "#2e2e2e"
    inputs = ["in"]
    outputs = ["next"]
    properties = [{"name": "color", "type": "choice", "default": "Black", "options": VGA_COLORS}]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        color_name = node.properties.get("color", "Black")
        code = VGA_CODES[color_name]
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Set BG Color: {color_name} ---", node.id))
            out.append((f"{pad}current_bg = 0x{code:X};", node.id))
        else:
            out.append((f"{pad}; --- Set BG Color: {color_name} ---", node.id))
            out.append((f"{pad}mov byte [current_bg], 0x{code:X}", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out