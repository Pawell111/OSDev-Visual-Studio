class Interrupt:
    name = "Interrupt"
    category = "System"
    description = "Registers an Interrupt Service Routine."
    color = "#2e2e2e"
    inputs = ["in"]
    outputs = ["next"]
    properties = [
        {"name": "number", "type": "int", "default": 0x20},
        {"name": "name", "type": "string", "default": "timer"}
    ]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        num = node.properties.get("number", 0x20)
        name = node.properties.get("name", "isr")
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Interrupt 0x{num:X} ---", node.id))
            out.append((f"{pad}register_interrupt(0x{num:X}, {name}_handler);", node.id))
            out.append((f'{pad}print_string("Registered ISR 0x{num:X}\\n");', node.id))
        else:
            context.msgs.append(f"msg_{node.id}: db 'Registered ISR 0x{num:X}', 0")
            out.append((f"{pad}; --- Interrupt 0x{num:X} ---", node.id))
            out.append((f"{pad}mov si, msg_{node.id}", node.id))
            out.append((f"{pad}call print_string", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out