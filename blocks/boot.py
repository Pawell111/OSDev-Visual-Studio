class Boot:
    name = "Boot"
    category = "Core"
    description = "Entry point of the OS. Sets up VGA and starts the kernel."
    color = "#2e2e2e"
    inputs = []
    outputs = ["next"]
    properties = []

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        out = []
        if lang == "c":
            out.append((f"{pad}// ===== BOOT =====", node.id))
            out.append((f"{pad}clear_screen();", node.id))
            out.append((f'{pad}print_string("OS booted!\\n\\n");', node.id))
        else:
            context.msgs.append("msg_boot: db 'OS booted!', 0")
            out.append((f"{pad}; ===== BOOT =====", node.id))
            out.append((f"{pad}mov si, msg_boot", node.id))
            out.append((f"{pad}call print_string", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out