import tkinter as tk

CATEGORY_COLORS = {
    "Core": "#c0392b",
    "I/O": "#2980b9",
    "Control": "#27ae60",
    "System": "#8e44ad",
    "Variables": "#16a085",
    "Math / Logic": "#f39c12",
    "I/O (Hardware)": "#e74c3c",
    "Advanced": "#d35400",
    "Misc": "#7f8c8d"
}

CATEGORY_ORDER = ["Core", "I/O", "Control", "System", "Variables", "Math / Logic", "I/O (Hardware)", "Advanced", "Misc"]

class Sidebar:
    def __init__(self, parent, blocks, canvas):
        self.frame = tk.Frame(parent, bg="#222222", width=200)
        self.frame.pack_propagate(False)
        self.canvas = canvas
        self.blocks = blocks
        self.drag_data = None
        self.ghost = None
        
        tk.Label(self.frame, text="BLOCKS", fg="#e0e0e0", bg="#222222", font=("Helvetica", 12, "bold"), pady=10).pack(fill=tk.X)
        
        self.info_label = tk.Label(self.frame, text="Hover a block for info", fg="#aaaaaa", bg="#222222", font=("Helvetica", 8), wraplength=180, justify=tk.LEFT)
        self.info_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.scroll_canvas = tk.Canvas(self.frame, bg="#222222", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.scroll_canvas.yview, bg="#222222", troughcolor="#1e1e1e", width=10)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        
        self.content_frame = tk.Frame(self.scroll_canvas, bg="#222222")
        self.content_window = self.scroll_canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        self.content_frame.bind("<Configure>", lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))
        self.scroll_canvas.bind("<Configure>", self.on_canvas_configure)
        
        categories = {}
        for btype, block in blocks.items():
            cat = getattr(block, "category", "Misc")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((btype, block))
            
        def sort_key(cat):
            return CATEGORY_ORDER.index(cat) if cat in CATEGORY_ORDER else 99
        sorted_cats = sorted(categories.keys(), key=sort_key)
        
        for cat in sorted_cats:
            items = categories[cat]
            color = CATEGORY_COLORS.get(cat, getattr(items[0][1], "color", "#7f8c8d"))
            tk.Label(self.content_frame, text=f" {cat.upper()}", fg="white", bg=color, font=("Helvetica", 9, "bold"), anchor="w").pack(fill=tk.X, padx=5, pady=(10, 2))
            
            for btype, block in items:
                btn = tk.Frame(self.content_frame, bg="#2e2e2e", cursor="hand2")
                btn.pack(fill=tk.X, padx=10, pady=2)
                
                strip = tk.Frame(btn, bg=color, width=4)
                strip.pack(side=tk.LEFT, fill=tk.Y)
                
                lbl = tk.Label(btn, text=block.name, fg="#e0e0e0", bg="#2e2e2e", font=("Helvetica", 10), padx=10, pady=6)
                lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                lbl.bind("<ButtonPress-1>", lambda e, t=btype: self.start_drag(e, t))
                btn.bind("<Enter>", lambda e, b=block: self.show_info(b))
                lbl.bind("<Enter>", lambda e, b=block: self.show_info(b))
                
        self._bind_mousewheel(self.frame)
        
    def on_canvas_configure(self, event):
        self.scroll_canvas.itemconfig(self.content_window, width=event.width)
        
    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        for child in widget.winfo_children():
            self._bind_mousewheel(child)
        
    def _on_mousewheel(self, event):
        self.scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def show_info(self, block):
        self.info_label.config(text=block.description)
        
    def start_drag(self, event, block_type):
        self.drag_data = {"type": block_type}
        self.ghost = tk.Toplevel()
        self.ghost.wm_overrideredirect(True)
        self.ghost.attributes("-alpha", 0.7)
        lbl = tk.Label(self.ghost, text=self.blocks[block_type].name, bg="#2e2e2e", fg="#e0e0e0", padx=20, pady=10)
        lbl.pack()
        self.ghost.geometry(f"+{event.x_root - 20}+{event.y_root - 10}")
        
        self.frame.bind_all("<B1-Motion>", self.on_drag)
        self.frame.bind_all("<ButtonRelease-1>", self.on_drop)
        
    def on_drag(self, event):
        if self.ghost:
            self.ghost.geometry(f"+{event.x_root - 20}+{event.y_root - 10}")
            
    def on_drop(self, event):
        self.frame.unbind_all("<B1-Motion>")
        self.frame.unbind_all("<ButtonRelease-1>")
        if self.ghost:
            self.ghost.destroy()
            self.ghost = None
            
        target = self.frame.winfo_containing(event.x_root, event.y_root)
        if target and target == self.canvas.canvas:
            x = event.x_root - self.canvas.canvas.winfo_rootx()
            y = event.y_root - self.canvas.canvas.winfo_rooty()
            wx = x - self.canvas.offset_x
            wy = y - self.canvas.offset_y
            self.canvas.add_node(self.drag_data["type"], wx, wy)
        self.drag_data = None