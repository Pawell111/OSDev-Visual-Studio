class Memory:
    name = "Memory"
    category = "System"
    description = "Allocates or frees memory."
    color = "#2e2e2e"
    inputs = ["in"]
    outputs = ["next"]
    properties = [
        {"name": "operation", "type": "choice", "default": "alloc", "options": ["alloc", "free"]},
        {"name": "size", "type": "int", "default": 256}
    ]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        op = node.properties.get("operation", "alloc")
        size = node.properties.get("size", 256)
        out = []
        if lang == "c":
            if op == "alloc":
                out.append((f"{pad}// --- Alloc {size} bytes ---", node.id))
                out.append((f"{pad}void* ptr = alloc_memory({size});", node.id))
                out.append((f'{pad}print_string("Allocated {size} bytes\\n");', node.id))
            else:
                out.append((f"{pad}// --- Free (stub) ---", node.id))
                out.append((f'{pad}print_string("Freed memory\\n");', node.id))
        else:
            if op == "alloc":
                context.msgs.append(f"msg_{node.id}: db 'Allocated {size} bytes', 0")
                out.append((f"{pad}; --- Alloc {size} ---", node.id))
                out.append((f"{pad}mov eax, {size}", node.id))
                out.append((f"{pad}call alloc_memory", node.id))
            else:
                context.msgs.append(f"msg_{node.id}: db 'Freed memory', 0")
                out.append((f"{pad}; --- Free (stub) ---", node.id))
            out.append((f"{pad}mov si, msg_{node.id}", node.id))
            out.append((f"{pad}call print_string", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out