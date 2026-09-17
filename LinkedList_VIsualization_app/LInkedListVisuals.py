import time
import tkinter as tk
from tkinter import messagebox, ttk


class Node:

    def __init__(self, value, address):
        self.value = value
        self.address = address
        self.next = None
        self.prev = None


class ModernTechyLinkedListVisualizer:

    def __init__(self, root):
        self.root = root
        self.root.title("NEXUS // Linked List Algorithm Engine")
        self.root.geometry("1200x780")
        self.root.configure(bg="#0f172a")

        self.head = None
        self.addr_counter = 0x7F00
        self.animation_queue = []
        self.is_animating = False

        self._configure_styles()
        self._setup_ui()

    def _generate_addr(self):
        self.addr_counter += 0x0008
        return hex(self.addr_counter).upper()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure(".", background="#0f172a", foreground="#f8fafc")
        style.configure("TFrame", background="#0f172a")
        style.configure(
            "TLabelframe",
            background="#1e293b",
            foreground="#38bdf8",
            borderColor="#334155",
        )
        style.configure(
            "TLabelframe.Label",
            background="#1e293b",
            foreground="#38bdf8",
            font=("Segoe UI", 10, "bold"),
        )
        style.configure("TLabel", background="#0f172a", foreground="#cbd5e1")

        style.configure(
            "Cyber.TButton",
            background="#0284c7",
            foreground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
            padding=6,
        )
        style.map(
            "Cyber.TButton",
            background=[("active", "#0369a1"), ("disabled", "#334155")],
        )

        style.configure(
            "Danger.TButton",
            background="#e11d48",
            foreground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
            padding=6,
        )
        style.map("Danger.TButton", background=[("active", "#be123c")])

    def _setup_ui(self):
        ctrl_frame = ttk.Frame(self.root, padding=10)
        ctrl_frame.pack(fill=tk.X)

        ttk.Label(
            ctrl_frame,
            text="STRUCTURE:",
            font=("Segoe UI", 9, "bold"),
            foreground="#38bdf8",
        ).grid(row=0, column=0, padx=4)
        self.list_type = tk.StringVar(value="Singly")
        type_dropdown = ttk.Combobox(
            ctrl_frame,
            textvariable=self.list_type,
            values=["Singly", "Doubly", "Circular"],
            state="readonly",
            width=9,
        )
        type_dropdown.grid(row=0, column=1, padx=4)
        type_dropdown.bind("<<ComboboxSelected>>", self.clear_list)

        ttk.Label(
            ctrl_frame,
            text="MODEL:",
            font=("Segoe UI", 9, "bold"),
            foreground="#38bdf8",
        ).grid(row=0, column=2, padx=4)
        self.object_model = tk.StringVar(value="Nodes")
        model_dropdown = ttk.Combobox(
            ctrl_frame,
            textvariable=self.object_model,
            values=[
                "Nodes",
                "Train Cars 🚃",
                "Treasure Clues 🗺️",
                "Web Pages 🌐",
            ],
            state="readonly",
            width=15,
        )
        model_dropdown.grid(row=0, column=3, padx=4)
        model_dropdown.bind("<<ComboboxSelected>>", lambda e: self.draw_list())

        ttk.Label(
            ctrl_frame,
            text="VAL:",
            font=("Segoe UI", 9, "bold"),
            foreground="#38bdf8",
        ).grid(row=0, column=4, padx=4)
        self.val_entry = tk.Entry(
            ctrl_frame,
            width=6,
            bg="#1e293b",
            fg="#f8fafc",
            insertbackground="#38bdf8",
            bd=1,
            relief="solid",
        )
        self.val_entry.grid(row=0, column=5, padx=4)

        ttk.Label(
            ctrl_frame,
            text="IDX:",
            font=("Segoe UI", 9, "bold"),
            foreground="#38bdf8",
        ).grid(row=0, column=6, padx=4)
        self.idx_entry = tk.Entry(
            ctrl_frame,
            width=5,
            bg="#1e293b",
            fg="#f8fafc",
            insertbackground="#38bdf8",
            bd=1,
            relief="solid",
        )
        self.idx_entry.grid(row=0, column=7, padx=4)

        ttk.Button(
            ctrl_frame,
            text="Insert Head",
            style="Cyber.TButton",
            command=self.action_insert_head,
        ).grid(row=0, column=8, padx=3)
        ttk.Button(
            ctrl_frame,
            text="Insert Tail",
            style="Cyber.TButton",
            command=self.action_insert_tail,
        ).grid(row=0, column=9, padx=3)
        ttk.Button(
            ctrl_frame,
            text="Insert at Idx",
            style="Cyber.TButton",
            command=self.action_insert_idx,
        ).grid(row=0, column=10, padx=3)
        ttk.Button(
            ctrl_frame,
            text="Delete at Idx",
            style="Danger.TButton",
            command=self.action_delete_idx,
        ).grid(row=0, column=11, padx=3)
        ttk.Button(
            ctrl_frame,
            text="Purge",
            style="Danger.TButton",
            command=self.clear_list,
        ).grid(row=0, column=12, padx=3)

        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        canvas_frame = ttk.LabelFrame(
            paned, text=" VISUAL MEMORY MATRIX ", padding=5
        )
        self.canvas = tk.Canvas(
            canvas_frame,
            bg="#020617",
            highlightthickness=1,
            highlightbackground="#1e293b",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        paned.add(canvas_frame, weight=3)

        code_frame = ttk.LabelFrame(paned, text=" CODE INSPECTOR ", padding=5)
        self.code_box = tk.Text(
            code_frame,
            width=30,
            font=("Consolas", 9),
            bg="#020617",
            fg="#94a3b8",
            bd=0,
        )
        self.code_box.pack(fill=tk.BOTH, expand=True)
        self.code_box.tag_config(
            "highlight", background="#0369a1", foreground="#f8fafc"
        )
        paned.add(code_frame, weight=1)

        edu_frame = ttk.LabelFrame(
            self.root, text=" SYSTEM DIAGNOSTICS & ANALYTICS ", padding=8
        )
        edu_frame.pack(fill=tk.X, padx=10, pady=5)

        self.complexity_label = tk.Label(
            edu_frame,
            text="TIME: O(1) | SPACE: O(1)",
            font=("Consolas", 10, "bold"),
            bg="#1e293b",
            fg="#38bdf8",
        )
        self.complexity_label.pack(anchor=tk.W)

        self.explanation_label = tk.Label(
            edu_frame,
            text=(
                "Engine initialized. Choose an operation to begin execution"
                " trace."
            ),
            font=("Segoe UI", 9),
            bg="#1e293b",
            fg="#f8fafc",
            wraplength=1150,
            justify=tk.LEFT,
        )
        self.explanation_label.pack(anchor=tk.W, pady=(4, 0))

        self._update_code_panel(["// Ready for command execution"])

    def _update_code_panel(self, code_lines, active_line=None):
        self.code_box.config(state=tk.NORMAL)
        self.code_box.delete("1.0", tk.END)
        for i, line in enumerate(code_lines, 1):
            self.code_box.insert(tk.END, f"{line}\n")
            if active_line == i:
                self.code_box.tag_add("highlight", f"{i}.0", f"{i}.end")
        self.code_box.config(state=tk.DISABLED)

    def _enqueue_step(
            self,
            explanation,
            complexity,
            code_lines,
            active_line,
            highlight_idx=None,
            curr_idx=None,
            temp_node_val=None,
    ):
        self.animation_queue.append(
            {
                "explanation": explanation,
                "complexity": complexity,
                "code": code_lines,
                "line": active_line,
                "highlight": highlight_idx,
                "curr": curr_idx,
                "temp_val": temp_node_val,
            }
        )

    def _process_queue(self):
        if not self.animation_queue:
            self.is_animating = False
            return

        self.is_animating = True
        step = self.animation_queue.pop(0)

        self.explanation_label.config(text=step["explanation"])
        self.complexity_label.config(text=step["complexity"])
        self._update_code_panel(step["code"], step["line"])
        self.draw_list(
            highlight_idx=step["highlight"],
            curr_idx=step["curr"],
            temp_val=step["temp_val"],
        )

        self.root.after(850, self._process_queue)

    def action_insert_idx(self):
        if self.is_animating:
            return
        val = self.val_entry.get()
        idx_str = self.idx_entry.get()
        if not val or not idx_str.isdigit():
            messagebox.showwarning(
                "Input Error", "Enter both a Value and valid Index."
            )
            return

        idx = int(idx_str)
        self.animation_queue.clear()

        code_snippet = [
            "1. node = Node(val)",
            "2. curr = head",
            "3. for i in 0..idx-1:",
            "4.    curr = curr.next",
            "5. node.next = curr.next",
            "6. curr.next = node",
        ]

        new_addr = self._generate_addr()
        new_node = Node(val, new_addr)
        self._enqueue_step(
            f"Step 1: Allocate memory block at {new_addr} storing value"
            f" '{val}'.",
            "TIME: O(N) Traversal | SPACE: O(1)",
            code_snippet,
            1,
            temp_node_val=val,
        )

        if idx == 0 or not self.head:
            new_node.next = self.head
            self.head = new_node
            self._enqueue_step(
                "Step 2: Splice at Head. Re-route head pointer to new node"
                f" '{val}'.",
                "TIME: O(1) | SPACE: O(1)",
                code_snippet,
                5,
                highlight_idx=0,
            )
            self._process_queue()
            return

        curr = self.head
        count = 0
        self._enqueue_step(
            "Step 2: Position traversal pointer 'curr' at Head (Index 0).",
            "TIME: O(N) | SPACE: O(1)",
            code_snippet,
            2,
            curr_idx=0,
            temp_node_val=val,
        )

        while curr and count < idx - 1:
            curr = curr.next
            count += 1
            if curr == self.head and self.list_type.get() == "Circular":
                break
            self._enqueue_step(
                "Step 3: Advancing pointer across links... 'curr' is now at"
                f" Index {count}.",
                "TIME: O(N) | SPACE: O(1)",
                code_snippet,
                4,
                curr_idx=count,
                temp_node_val=val,
            )

        if not curr:
            messagebox.showerror("Error", "Index out of bounds.")
            self.animation_queue.clear()
            return

        new_node.next = curr.next
        if self.list_type.get() == "Doubly":
            if curr.next:
                curr.next.prev = new_node
            new_node.prev = curr
        curr.next = new_node

        self._enqueue_step(
            "Step 4: Update pointer links to splice"
            f" '{val}' between index {count} and {count+1}.",
            "TIME: O(1) Link Swap | SPACE: O(1)",
            code_snippet,
            6,
            highlight_idx=idx,
        )
        self._process_queue()

    def action_insert_head(self):
        self.idx_entry.delete(0, tk.END)
        self.idx_entry.insert(0, "0")
        self.action_insert_idx()

    def action_insert_tail(self):
        count = 0
        curr = self.head
        while curr:
            count += 1
            curr = curr.next
            if curr == self.head:
                break
        self.idx_entry.delete(0, tk.END)
        self.idx_entry.insert(0, str(count))
        self.action_insert_idx()

    def action_delete_idx(self):
        if self.is_animating or not self.head:
            return
        idx_str = self.idx_entry.get()
        if not idx_str.isdigit():
            messagebox.showwarning("Error", "Provide a valid numeric index.")
            return

        idx = int(idx_str)
        self.animation_queue.clear()

        code_snippet = [
            "1. curr = head",
            "2. for i in 0..idx-1:",
            "3.    curr = curr.next",
            "4. target = curr.next",
            "5. curr.next = target.next",
            "6. free(target)",
        ]

        if idx == 0:
            val = self.head.value
            self._enqueue_step(
                f"Step 1: Unlinking Head '{val}'. Advance Head pointer to next"
                " node.",
                "TIME: O(1) | SPACE: O(1)",
                code_snippet,
                5,
                highlight_idx=0,
            )
            self.head = self.head.next
            self._process_queue()
            return

        curr = self.head
        count = 0
        while curr and count < idx - 1:
            curr = curr.next
            count += 1
            self._enqueue_step(
                f"Step 1: Searching list... 'curr' pointer at index {count}.",
                "TIME: O(N) | SPACE: O(1)",
                code_snippet,
                3,
                curr_idx=count,
            )

        if not curr or not curr.next or curr.next == self.head:
            messagebox.showerror("Error", "Index out of bounds.")
            self.animation_queue.clear()
            return

        deleted_val = curr.next.value
        self._enqueue_step(
            f"Step 2: Bypass node '{deleted_val}' at index {idx}. Connect"
            f" index {count} directly to index {idx+1}.",
            "TIME: O(1) Link Swap | SPACE: O(1)",
            code_snippet,
            5,
            curr_idx=count,
            highlight_idx=idx,
        )

        curr.next = curr.next.next
        self._process_queue()

    def clear_list(self, event=None):
        self.head = None
        self.animation_queue.clear()
        self.canvas.delete("all")
        self.explanation_label.config(
            text="Memory matrix purged. Ready for new operations."
        )
        self._update_code_panel(["// Standby mode"])

    # --- Shape-Based Custom Model Drawing Engine ---

    def _draw_model_shape(
            self, x, y, box_w, box_h, model, value, bg_color, outline_color, dash=None
    ):
        """Renders specific geometric/object shapes depending on the selected model."""
        outline_kw = {"dash": dash} if dash else {}

        if "Train" in model:
            # Roof Cabin
            self.canvas.create_rectangle(
                x + 10,
                y - 12,
                x + box_w - 10,
                y,
                fill=bg_color,
                outline=outline_color,
                width=2,
                **outline_kw,
                )
            # Main Box Car Body
            self.canvas.create_rectangle(
                x,
                y,
                x + box_w,
                y + box_h,
                fill=bg_color,
                outline=outline_color,
                width=2,
                **outline_kw,
                )
            # Wheels
            self.canvas.create_oval(
                x + 12,
                y + box_h - 2,
                x + 28,
                y + box_h + 12,
                fill="#334155",
                outline=outline_color,
                width=2,
                )
            self.canvas.create_oval(
                x + box_w - 28,
                y + box_h - 2,
                x + box_w - 12,
                y + box_h + 12,
                fill="#334155",
                outline=outline_color,
                width=2,
                )
            # Text Inside Car
            self.canvas.create_text(
                x + box_w / 2,
                y + box_h / 2,
                text=f"CAR: {value}",
                fill="#f8fafc",
                font=("Consolas", 9, "bold"),
                )

        elif "Treasure" in model:
            # Map Scroll Body
            self.canvas.create_rectangle(
                x + 8,
                y,
                x + box_w - 8,
                y + box_h,
                fill=bg_color,
                outline=outline_color,
                width=2,
                **outline_kw,
                )
            # Left & Right Rolled Edges
            self.canvas.create_oval(
                x - 2,
                y,
                x + 12,
                y + box_h,
                fill="#854d0e",
                outline=outline_color,
                width=2,
                )
            self.canvas.create_oval(
                x + box_w - 12,
                y,
                x + box_w + 2,
                y + box_h,
                fill="#854d0e",
                outline=outline_color,
                width=2,
                )
            self.canvas.create_text(
                x + box_w / 2,
                y + box_h / 2,
                text=f"CLUE: {value}",
                fill="#fef08a",
                font=("Segoe UI", 9, "bold"),
                )

        elif "Web" in model:
            # Browser Window Body
            self.canvas.create_rectangle(
                x,
                y,
                x + box_w,
                y + box_h,
                fill=bg_color,
                outline=outline_color,
                width=2,
                **outline_kw,
                )
            # Top Window Titlebar
            self.canvas.create_rectangle(
                x,
                y,
                x + box_w,
                y + 16,
                fill="#1e293b",
                outline=outline_color,
                width=1,
                )
            # Window Controls (Red, Yellow, Green dots)
            self.canvas.create_oval(
                x + 4, y + 5, x + 9, y + 10, fill="#f43f5e", outline=""
            )
            self.canvas.create_oval(
                x + 12, y + 5, x + 17, y + 10, fill="#eab308", outline=""
            )
            self.canvas.create_oval(
                x + 20, y + 5, x + 25, y + 10, fill="#22c55e", outline=""
            )
            self.canvas.create_text(
                x + box_w / 2,
                y + (box_h + 16) / 2,
                text=f"{value}.com",
                fill="#38bdf8",
                font=("Segoe UI", 8, "bold"),
                )

        else:
            # Default Techy Rectangular Memory Block
            self.canvas.create_rectangle(
                x,
                y,
                x + box_w,
                y + box_h,
                fill=bg_color,
                outline=outline_color,
                width=2,
                **outline_kw,
                )
            self.canvas.create_text(
                x + box_w / 2,
                y + box_h / 2 - 5,
                text=f"VAL: {value}",
                fill="#f8fafc",
                font=("Consolas", 10, "bold"),
                )

    def draw_list(self, highlight_idx=None, curr_idx=None, temp_val=None):
        self.canvas.delete("all")

        nodes = []
        curr = self.head
        while curr:
            nodes.append(curr)
            curr = curr.next
            if curr == self.head:
                break

        start_x, start_y = 70, 200
        box_w, box_h = 95, 55
        gap = 60
        model = self.object_model.get()

        # Render floating unlinked new shape if preparing insertion
        if temp_val is not None:
            self._draw_model_shape(
                start_x,
                70,
                box_w,
                box_h,
                model,
                temp_val,
                "#312e81",
                "#a855f7",
                dash=(4, 2),
            )
            self.canvas.create_text(
                start_x + box_w / 2,
                52,
                text="NEW ELEMENT",
                fill="#a855f7",
                font=("Consolas", 8, "bold"),
                )

        for i, node in enumerate(nodes):
            x = start_x + i * (box_w + gap)
            y = start_y

            bg_color = "#0f172a"
            outline_color = "#38bdf8"

            if highlight_idx is not None and i == highlight_idx:
                bg_color = "#881337"
                outline_color = "#f43f5e"

            # Draw Model Shape
            self._draw_model_shape(
                x, y, box_w, box_h, model, node.value, bg_color, outline_color
            )

            # Hex Memory Address readout below shape
            self.canvas.create_text(
                x + box_w / 2,
                y + box_h + 16,
                text=node.address,
                fill="#64748b",
                font=("Consolas", 7),
                )

            # Index readout above shape
            self.canvas.create_text(
                x + box_w / 2,
                y - 18,
                text=f"INDEX [{i}]",
                fill="#64748b",
                font=("Consolas", 8),
                )

            # Active Pointer Traversal Marker
            if curr_idx is not None and i == curr_idx:
                self.canvas.create_text(
                    x + box_w / 2,
                    y - 32,
                    text="▼ curr",
                    fill="#f43f5e",
                    font=("Consolas", 10, "bold"),
                    )

            if i == 0:
                self.canvas.create_text(
                    x + box_w / 2,
                    y + box_h + 30,
                    text="HEAD",
                    fill="#22c55e",
                    font=("Consolas", 9, "bold"),
                    )

            # Forward Arrow (next)
            if i < len(nodes) - 1:
                self.canvas.create_line(
                    x + box_w + (12 if "Treasure" in model else 0),
                    y + 20,
                    x + box_w + gap - (12 if "Treasure" in model else 0),
                    y + 20,
                    arrow=tk.LAST,
                    width=2,
                    fill="#38bdf8",
                    )

            # Backward Arrow (prev - Doubly)
            if self.list_type.get() == "Doubly" and i > 0:
                self.canvas.create_line(
                    x - (12 if "Treasure" in model else 0),
                    y + 38,
                    x - gap + (12 if "Treasure" in model else 0),
                    y + 38,
                    arrow=tk.LAST,
                    width=2,
                    fill="#c084fc",
                    )

        # Circular Link
        if self.list_type.get() == "Circular" and len(nodes) > 0:
            last_x = start_x + (len(nodes) - 1) * (box_w + gap) + box_w / 2
            self.canvas.create_line(
                last_x,
                start_y + box_h + 10,
                last_x,
                start_y + 90,
                start_x + box_w / 2,
                start_y + 90,
                start_x + box_w / 2,
                start_y + box_h + 10,
                arrow=tk.LAST,
                width=2,
                fill="#fb923c",
                smooth=True,
                )


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernTechyLinkedListVisualizer(root)
    root.mainloop()