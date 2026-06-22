VGA_COLORS = [
    "Black", "Blue", "Green", "Cyan", "Red", "Magenta", "Brown", "Light Gray",
    "Dark Gray", "Light Blue", "Light Green", "Light Cyan", "Light Red",
    "Light Magenta", "Yellow", "White"
]
VGA_CODES = {
    "Black": 0x0, "Blue": 0x1, "Green": 0x2, "Cyan": 0x3, "Red": 0x4,
    "Magenta": 0x5, "Brown": 0x6, "Light Gray": 0x7, "Dark Gray": 0x8,
    "Light Blue": 0x9, "Light Green": 0xA, "Light Cyan": 0xB, "Light Red": 0xC,
    "Light Magenta": 0xD, "Yellow": 0xE, "White": 0xF
}

class ColorFG:
    name = "Text Color"
    category = "I/O"
    description = "Sets the text color for subsequent Print blocks."
    color = "#2e2e2e"
    inputs = ["in"]
    outputs = ["next"]
    properties = [{"name": "color", "type": "choice", "default": "Light Gray", "options": VGA_COLORS}]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        color_name = node.properties.get("color", "Light Gray")
        code = VGA_CODES[color_name]
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Set Text Color: {color_name} ---", node.id))
            out.append((f"{pad}current_fg = 0x{code:X};", node.id))
        else:
            out.append((f"{pad}; --- Set Text Color: {color_name} ---", node.id))
            out.append((f"{pad}mov byte [current_fg], 0x{code:X}", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out