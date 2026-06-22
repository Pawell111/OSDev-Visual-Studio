class Wait:
    name = "Wait"
    category = "Control"
    description = "Pauses execution for approx. X seconds based on CPU cycles."
    color = "#27ae60"
    inputs = ["in"]
    outputs = ["next"]
    properties = [{"name": "cycles", "type": "int", "default": 300000000}]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        cycles = node.properties.get("cycles", 300000000)
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Wait {cycles} cycles ---", node.id))
            out.append((f"{pad}for (volatile long long i=0; i<{cycles}; i++) {{ __asm__ __volatile__(\"nop\"); }}", node.id))
        else:
            out.append((f"{pad}; --- Wait {cycles} cycles ---", node.id))
            out.append((f"{pad}mov ecx, {cycles}", node.id))
            out.append((f"{pad}.wait_{node.id}:", node.id))
            out.append((f"{pad}    nop", node.id))
            out.append((f"{pad}    loop .wait_{node.id}", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out