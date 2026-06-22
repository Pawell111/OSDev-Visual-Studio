class CustomCode:
    name = "Custom Code"
    category = "Advanced"
    description = "Type raw C or ASM. Double-click to edit."
    color = "#2e2e2e"
    inputs = ["in"]
    outputs = ["next"]
    properties = [{"name": "code", "type": "text", "default": "// Type your code here..."}]

    def generate(self, node, lang, indent, context):
        pad = "    " * indent
        code = node.properties.get("code", "")
        out = []
        for line in code.split("\n"):
            out.append((pad + line, node.id))
        out += context.generate_chain(node.id, "next", indent)
        return out