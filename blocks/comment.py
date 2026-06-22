class Comment:
    name = "Comment"
    category = "Misc"
    description = "A sticky note for leaving reminders. Does not generate code."
    color = "#f4d03f"
    inputs = []
    outputs = []
    properties = [{"name": "text", "type": "string", "default": "Note..."}]

    def generate(self, node, lang, indent, context):
        return []