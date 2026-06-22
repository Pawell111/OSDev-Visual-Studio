import os
import importlib.util

def load_blocks():
    blocks = {}
    blocks_dir = os.path.dirname(__file__)
    for filename in os.listdir(blocks_dir):
        if filename.endswith(".py") and not filename.startswith("__") and not filename.startswith("BLOCK_TEMPLATE"):
            module_name = filename[:-3]
            spec = importlib.util.spec_from_file_location(module_name, os.path.join(blocks_dir, filename))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and hasattr(attr, 'name') and hasattr(attr, 'generate'):
                    if attr.__name__ not in ["Block", "BlockTemplate"]:
                        blocks[module_name] = attr()
    return blocks