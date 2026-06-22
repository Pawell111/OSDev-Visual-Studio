class GetVariable:
    name = "Get Variable"
    category = "Variables"
    description = "Placeholder to remind you a variable exists. Type its name in Math or Print blocks."
    color = "#16a085"
    inputs = ["in"]
    outputs = ["next"]
    properties = [{"name": "name", "type": "string", "default": "my_var"}]
    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        name = node.properties.get("name", "var")
        out = []
        if lang == "c":
            out.append((f"{pad}// --- Accessing variable: {name} ---", node.id))
        else:
            out.append((f"{pad}; --- Accessing variable: {name} ---", node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out