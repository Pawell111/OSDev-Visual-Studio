import tkinter as tk
import tkinter.font as tkfont
from tkinter import simpledialog, messagebox
from nodes import Node

PORT_RADIUS = 6
PORT_HIT_RADIUS = 12

CATEGORY_COLORS = {
    "Core": "#c0392b", "I/O": "#2980b9", "Control": "#27ae60",
    "System": "#8e44ad", "Variables": "#16a085", 
    "Math / Logic": "#f39c12", "I/O (Hardware)": "#e74c3c",
    "Advanced": "#d35400", "Misc": "#7f8c8d"
}

class VisualCanvas:
    def __init__(self, parent, blocks, on_change_callback=None, on_select_callback=None):
        self.parent = parent
        self.blocks = blocks
        self.on_change = on_change_callback
        self.on_select = on_select_callback
        
        self.frame = tk.Frame(parent, bg="#1a1a1a")
        self.canvas = tk.Canvas(self.frame, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.nodes = []
        self.connections = []
        self.selected_node = None
        self.selected_nodes = set()
        self.selected_conn = None
        self.dragging = None
        self.drag_offset = (0, 0)
        self.connecting = None
        self.connecting_mouse = (0, 0)
        self.hover_node = None
        
        self.offset_x = 0
        self.offset_y = 0
        
        self.panning = False
        self.pan_start = (0, 0)
        self.pan_offset_start = (0, 0)
        
        self.selecting = False
        self.sel_start = (0, 0)
        self.sel_end = (0, 0)
        
        self.clipboard = []
        self.alt_held = False
        
        self.comment_font = tkfont.Font(family="Helvetica", size=10, weight="bold")
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-2>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<B2-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonRelease-2>", self.on_release)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Delete>", lambda e: self.delete_selected())
        self.canvas.bind("<BackSpace>", lambda e: self.delete_selected())
        self.canvas.bind("<Escape>", lambda e: self.cancel_connecting())
        
        self.canvas.bind("<Control-c>", self.copy_nodes)
        self.canvas.bind("<Control-v>", self.paste_nodes)
        
        self.canvas.bind_all("<KeyPress-Alt_L>", lambda e: setattr(self, 'alt_held', True))
        self.canvas.bind_all("<KeyRelease-Alt_L>", lambda e: setattr(self, 'alt_held', False))
        self.canvas.bind_all("<KeyPress-Alt_R>", lambda e: setattr(self, 'alt_held', True))
        self.canvas.bind_all("<KeyRelease-Alt_R>", lambda e: setattr(self, 'alt_held', False))
        
    def update_comment_size(self, node):
        text = node.properties.get("text", "Note...")
        lines = text.split('\n')
        
        max_w = 0
        for line in lines:
            lw = self.comment_font.measure(line)
            if lw > max_w:
                max_w = lw
                
        node.w = max(80, max_w + 20)
        line_h = self.comment_font.metrics("linespace") + 4
        node.h = max(40, 20 + len(lines) * line_h)

    def on_motion(self, event):
        if self.connecting:
            self.connecting_mouse = (event.x, event.y)
            self.redraw()
            return
            
        if not self.panning and not self.dragging:
            wx = event.x - self.offset_x
            wy = event.y - self.offset_y
            if self.find_port_at(wx, wy) or self.find_node_at(wx, wy):
                self.canvas.config(cursor="hand2")
            else:
                self.canvas.config(cursor="arrow")

    def on_release(self, event):
        if event.num == 2:
            self.panning = False
        elif event.num == 1:
            self.dragging = None
            self.selecting = False
            
        wx = event.x - self.offset_x
        wy = event.y - self.offset_y
        if self.find_port_at(wx, wy) or self.find_node_at(wx, wy):
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.config(cursor="arrow")
            
        self.redraw()

    def notify_change(self):
        if self.on_change: self.on_change()
        
    def add_node(self, node_type, x, y):
        node = Node(node_type, x, y)
        meta = self.blocks[node_type]
        for prop in meta.properties:
            node.properties[prop["name"]] = prop["default"]
        if node.type == "comment":
            self.update_comment_size(node)
        self.nodes.append(node)
        self.redraw()
        self.notify_change()
        return node
        
    def get_node(self, node_id):
        return next((n for n in self.nodes if n.id == node_id), None)
        
    def get_port_pos(self, node, port_name, is_output):
        meta = self.blocks[node.type]
        ports = meta.outputs if is_output else meta.inputs
        wx = node.x + node.w if is_output else node.x
        idx = ports.index(port_name)
        total = len(ports)
        if total == 1:
            wy = node.y + node.h // 2
        else:
            spacing = node.h / (total + 1)
            wy = node.y + int(spacing * (idx + 1))
        return wx, wy
        
    def find_port_at(self, wx, wy):
        hit_r = PORT_HIT_RADIUS
        for node in self.nodes:
            meta = self.blocks[node.type]
            for port in meta.outputs:
                px, py = self.get_port_pos(node, port, True)
                if (wx - px)**2 + (wy - py)**2 <= hit_r**2:
                    return node, port, True
            for port in meta.inputs:
                px, py = self.get_port_pos(node, port, False)
                if (wx - px)**2 + (wy - py)**2 <= hit_r**2:
                    return node, port, False
        return None
        
    def find_node_at(self, wx, wy):
        for node in self.nodes:
            if (node.x <= wx <= node.x + node.w and node.y <= wy <= node.y + node.h):
                return node
        return None
        
    def find_conn_at(self, wx, wy, threshold=8):
        th = threshold
        for conn in self.connections:
            fn = self.get_node(conn["from_node"])
            tn = self.get_node(conn["to_node"])
            if not fn or not tn: continue
            x1, y1 = self.get_port_pos(fn, conn["from_port"], True)
            x2, y2 = self.get_port_pos(tn, conn["to_port"], False)
            pts = self.get_wire_points(x1, y1, x2, y2)
            for i in range(0, len(pts)-2, 2):
                px1, py1 = pts[i], pts[i+1]
                px2, py2 = pts[i+2], pts[i+3]
                dx = px2 - px1
                dy = py2 - py1
                if dx == 0 and dy == 0:
                    if (wx-px1)**2 + (wy-py1)**2 <= th**2: return conn
                    continue
                t = max(0, min(1, ((wx-px1)*dx + (wy-py1)*dy) / (dx*dx + dy*dy)))
                px, py = px1 + t*dx, py1 + t*dy
                if (wx-px)**2 + (wy-py)**2 <= th**2:
                    return conn
        return None
        
    def get_wire_points(self, x1, y1, x2, y2):
        # Simple Bézier curve control points
        dx = max(abs(x2 - x1) * 0.5, 30)
        return [x1, y1, x1 + dx, y1, x2 - dx, y2, x2, y2]
        
    def on_click(self, event):
        self.canvas.focus_set()
        wx = event.x - self.offset_x
        wy = event.y - self.offset_y
        
        if event.num == 2:
            self.panning = True
            self.pan_start = (event.x, event.y)
            self.pan_offset_start = (self.offset_x, self.offset_y)
            self.canvas.config(cursor="fleur")
            return
            
        port_hit = self.find_port_at(wx, wy)
        if port_hit:
            node, port, is_output = port_hit
            if is_output:
                self.connecting = (node, port)
                self.connecting_mouse = (event.x, event.y)
                self.redraw()
            else:
                if self.connecting:
                    fn, fp = self.connecting
                    if fn.id != node.id:
                        if fn.type != "goto":
                            self.connections = [
                                c for c in self.connections 
                                if not (c["to_node"] == node.id and c["to_port"] == port and self.get_node(c["from_node"]).type != "goto")
                            ]
                        self.connections.append({"from_node": fn.id, "from_port": fp, "to_node": node.id, "to_port": port})
                        self.notify_change()
                    self.connecting = None
                    self.redraw()
            return
            
        node = self.find_node_at(wx, wy)
        if node:
            self.selecting = False
            if node not in self.selected_nodes:
                self.selected_nodes.clear()
                self.selected_nodes.add(node)
            self.selected_node = node
            self.selected_conn = None
            self.dragging = node
            self.drag_offset = (wx - node.x, wy - node.y)
            self.canvas.config(cursor="hand2")
            if self.on_select: self.on_select()
            self.redraw()
            return
            
        conn = self.find_conn_at(wx, wy)
        if conn:
            self.selecting = False
            self.selected_conn = conn
            self.selected_node = None
            self.selected_nodes.clear()
            self.redraw()
            return
            
        self.selected_nodes.clear()
        self.selected_node = None
        self.selected_conn = None
        if self.on_select: self.on_select()
        if self.connecting: self.connecting = None
            
        self.selecting = True
        self.sel_start = (wx, wy)
        self.sel_end = (wx, wy)
        self.redraw()
        
    def on_drag(self, event):
        wx = event.x - self.offset_x
        wy = event.y - self.offset_y
        
        if self.panning:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            self.offset_x = self.pan_offset_start[0] + dx
            self.offset_y = self.pan_offset_start[1] + dy
            self.redraw()
            return
            
        if self.selecting:
            self.sel_end = (wx, wy)
            x1, y1 = self.sel_start
            x2, y2 = self.sel_end
            self.selected_nodes.clear()
            for n in self.nodes:
                if (n.x < max(x1,x2) and n.x + n.w > min(x1,x2) and
                    n.y < max(y1,y2) and n.y + n.h > min(y1,y2)):
                    self.selected_nodes.add(n)
            self.redraw()
            return
            
        if self.dragging:
            target_x = wx - self.drag_offset[0]
            target_y = wy - self.drag_offset[1]
            
            if self.alt_held:
                target_x = round(target_x / 40) * 40
                target_y = round(target_y / 40) * 40
                
            if self.selected_nodes:
                dx = target_x - self.dragging.x
                dy = target_y - self.dragging.y
                for n in self.selected_nodes:
                    n.x += dx
                    n.y += dy
            else:
                self.dragging.x = target_x
                self.dragging.y = target_y
            self.redraw()
            
    def on_right_click(self, event):
        wx = event.x - self.offset_x
        wy = event.y - self.offset_y
        node = self.find_node_at(wx, wy)
        if node:
            self.edit_node_properties(node)
                
    def on_double_click(self, event):
        wx = event.x - self.offset_x
        wy = event.y - self.offset_y
        node = self.find_node_at(wx, wy)
        if node and node.type == "custom_code":
            self.open_code_editor(node)
            
    def open_code_editor(self, node):
        win = tk.Toplevel(self.parent)
        win.title("Custom Code Editor")
        win.geometry("500x400")
        win.configure(bg="#1e1e1e")
        
        btn_frame = tk.Frame(win, bg="#222222", height=50)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        def save():
            node.properties["code"] = txt.get("1.0", "end-1c")
            self.redraw()
            self.notify_change()
            win.destroy()
            
        tk.Button(btn_frame, text="Save Code", command=save, bg="#27ae60", fg="white", font=("Helvetica", 12, "bold"), pady=10).pack(side=tk.RIGHT, padx=10, pady=10)
        
        txt = tk.Text(win, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white", font=("Consolas", 11), undo=True)
        txt.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        txt.insert("1.0", node.properties.get("code", ""))
        
    def edit_node_properties(self, node):
        meta = self.blocks[node.type]
        for prop in meta.properties:
            if prop["name"] == "code": continue
            name = prop["name"]
            ptype = prop["type"]
            current = node.properties.get(name, prop["default"])
            if ptype == "string":
                val = simpledialog.askstring("Edit", f"{name}:", initialvalue=str(current), parent=self.parent)
                if val is not None: node.properties[name] = val
            elif ptype == "int":
                val = simpledialog.askinteger("Edit", f"{name}:", initialvalue=int(current), parent=self.parent)
                if val is not None: node.properties[name] = val
            elif ptype == "choice":
                val = self._choice_dialog(name, prop["options"], current)
                if val is not None: node.properties[name] = val
        if node.type == "comment":
            self.update_comment_size(node)
        self.redraw()
        self.notify_change()
        
    def _choice_dialog(self, name, options, current):
        dlg = tk.Toplevel(self.parent)
        dlg.title(f"Choose {name}")
        dlg.configure(bg="#222222")
        var = tk.StringVar(value=current)
        tk.Label(dlg, text=f"Select {name}:", fg="white", bg="#222222").pack(pady=10)
        for opt in options:
            tk.Radiobutton(dlg, text=opt, variable=var, value=opt, bg="#222222", fg="white", selectcolor="#2e2e2e").pack(anchor=tk.W, padx=40)
        result = [None]
        def ok():
            result[0] = var.get()
            dlg.destroy()
        tk.Button(dlg, text="OK", command=ok, bg="#4a4a4a", fg="white").pack(pady=10)
        dlg.wait_window()
        return result[0]
        
    def delete_selected(self):
        if self.selected_nodes:
            for node in self.selected_nodes:
                self.nodes = [n for n in self.nodes if n.id != node.id]
                self.connections = [c for c in self.connections if c["from_node"] != node.id and c["to_node"] != node.id]
            self.selected_nodes.clear()
            self.selected_node = None
            if self.on_select: self.on_select()
            self.redraw()
            self.notify_change()
        elif self.selected_conn:
            self.connections.remove(self.selected_conn)
            self.selected_conn = None
            self.redraw()
            self.notify_change()
            
    def copy_nodes(self, event=None):
        if self.selected_nodes:
            self.clipboard = {"nodes": [], "conns": []}
            ids = [n.id for n in self.selected_nodes]
            for n in self.selected_nodes:
                self.clipboard["nodes"].append({"id": n.id, "type": n.type, "x": n.x, "y": n.y, "w": n.w, "h": n.h, "properties": n.properties.copy()})
            for c in self.connections:
                if c["from_node"] in ids and c["to_node"] in ids:
                    self.clipboard["conns"].append({"from_port": c["from_port"], "to_port": c["to_port"], "from_id": c["from_node"], "to_id": c["to_node"]})

    def paste_nodes(self, event=None):
        if self.clipboard:
            id_map = {}
            self.selected_nodes.clear()
            for n_data in self.clipboard["nodes"]:
                n = Node(n_data["type"], n_data["x"] + 20, n_data["y"] + 20)
                n.properties = n_data["properties"].copy()
                if "w" in n_data: n.w = n_data["w"]
                if "h" in n_data: n.h = n_data["h"]
                self.nodes.append(n)
                id_map[n_data["id"]] = n.id
                self.selected_nodes.add(n)
            for c_data in self.clipboard["conns"]:
                self.connections.append({
                    "from_node": id_map[c_data["from_id"]],
                    "from_port": c_data["from_port"],
                    "to_node": id_map[c_data["to_id"]],
                    "to_port": c_data["to_port"]
                })
            self.redraw()
            self.notify_change()

    def cancel_connecting(self):
        if self.connecting:
            self.connecting = None
            self.redraw()
            
    def set_hover_node(self, node_id):
        if node_id is not None:
            self.hover_node = self.get_node(node_id)
        else:
            self.hover_node = None
        self.redraw()
        
    def redraw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        grid_size = 40
        start_x = self.offset_x % grid_size
        start_y = self.offset_y % grid_size
        for x in range(int(start_x), w, int(grid_size)):
            for y in range(int(start_y), h, int(grid_size)):
                self.canvas.create_oval(x-1, y-1, x+1, y+1, fill="#333333", outline="")
                
        if self.selecting:
            wx1, wy1 = self.sel_start
            wx2, wy2 = self.sel_end
            x1, y1 = wx1 + self.offset_x, wy1 + self.offset_y
            x2, y2 = wx2 + self.offset_x, wy2 + self.offset_y
            self.canvas.create_rectangle(min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2), outline="#2980b9", dash=(4, 4))
            
        # Draw nodes FIRST
        for node in self.nodes:
            self._draw_node(node)
            
        # Draw connections AFTER so they overlap the blocks
        for conn in self.connections:
            fn = self.get_node(conn["from_node"])
            tn = self.get_node(conn["to_node"])
            if not fn or not tn: continue
            wx1, wy1 = self.get_port_pos(fn, conn["from_port"], True)
            wx2, wy2 = self.get_port_pos(tn, conn["to_port"], False)
            color = "#f1c40f" if conn == self.selected_conn else "#555555"
            self._draw_wire(wx1, wy1, wx2, wy2, color)
            
        if self.connecting:
            fn, fp = self.connecting
            wx1, wy1 = self.get_port_pos(fn, fp, True)
            mx = self.connecting_mouse[0]
            my = self.connecting_mouse[1]
            wx2 = mx - self.offset_x
            wy2 = my - self.offset_y
            self._draw_wire(wx1, wy1, wx2, wy2, "#888888", dashed=True)
            
    def _draw_wire(self, x1, y1, x2, y2, color, dashed=False):
        pts = self.get_wire_points(x1, y1, x2, y2)
        scaled_pts = []
        for i in range(0, len(pts), 2):
            scaled_pts.append(pts[i] + self.offset_x)
            scaled_pts.append(pts[i+1] + self.offset_y)
        self.canvas.create_line(*scaled_pts, smooth=True, fill=color, width=2, dash=(5, 3) if dashed else None, arrow=tk.LAST)
        
    def _draw_node(self, node):
        meta = self.blocks[node.type]
        sx = node.x + self.offset_x
        sy = node.y + self.offset_y
        w = node.w
        h = node.h
        
        if node.type == "comment":
            self.canvas.create_rectangle(sx, sy, sx + w, sy + h, fill="#f4d03f", outline="#d4ac0d", width=2)
            self.canvas.create_text(
                sx + w / 2, 
                sy + h / 2, 
                text=node.properties.get("text", "Note..."), 
                fill="#222222", 
                font=("Helvetica", 10, "bold"), 
                anchor=tk.CENTER,       
                justify=tk.CENTER       
            )
            return
            
        cat_color = CATEGORY_COLORS.get(meta.category, getattr(meta, "color", "#7f8c8d"))
        fill = "#2e2e2e"
        
        if node in self.selected_nodes or node == self.selected_node:
            outline, ow = "#f1c40f", 2
        elif node == self.hover_node:
            outline, ow = "#888888", 1
        else:
            outline, ow = "#444444", 1
            
        self.canvas.create_rectangle(sx, sy, sx + w, sy + h, fill=fill, outline=outline, width=ow)
        self.canvas.create_rectangle(sx, sy, sx + w, sy + 5, fill=cat_color, outline="")
        self.canvas.create_text(sx + w // 2, sy + 18, text=meta.name, fill="#e0e0e0", font=("Helvetica", 11, "bold"))
        
        prop_text = ""
        for prop in meta.properties:
            if prop["name"] == "code": 
                prop_text += "code: ...\n"
                continue
            val = node.properties.get(prop["name"], prop["default"])
            prop_text += f"{prop['name']}: {val}\n"
        if prop_text:
            self.canvas.create_text(sx + w // 2, sy + 38, text=prop_text.strip(), fill="#a0a0a0", font=("Helvetica", 8), justify=tk.CENTER)
            
        for port in meta.inputs:
            wx, wy = self.get_port_pos(node, port, False)
            px, py = wx + self.offset_x, wy + self.offset_y
            r = PORT_RADIUS
            self.canvas.create_oval(px - r, py - r, px + r, py + r, fill="#e0e0e0", outline="#444444")
        for port in meta.outputs:
            wx, wy = self.get_port_pos(node, port, True)
            px, py = wx + self.offset_x, wy + self.offset_y
            r = PORT_RADIUS
            self.canvas.create_oval(px - r, py - r, px + r, py + r, fill="#2e2e2e", outline="#e0e0e0")
            
    def deselect_all(self):
        self.selected_nodes.clear()
        self.selected_node = None
        self.selected_conn = None