class TriggerCycles:
    name = "Trigger (Background)"
    category = "Control"
    description = "Runs independently in the background via the hardware timer interrupt. Executes its chain continuously while the main OS runs."
    color = "#27ae60"
    inputs = ["in"]
    outputs = ["next"]
    properties = [{"name": "frequency", "type": "int", "default": 10}]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Trigger Execution ---", node.id))
        else:
            out.append((f"{pad}; --- Trigger Execution (C only) ---", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out