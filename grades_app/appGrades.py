import os
import re
import json
import csv
import uuid
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# APPLICATION SETTINGS
# ============================================================

APP_TITLE = "NDMU Grade Report Console"

DEFAULT_SENDER_EMAIL = os.getenv(
    "BREVO_SENDER_EMAIL",
    "your-email@example.com"
)

BREVO_API_KEY = os.getenv(
    "BREVO_API_KEY",
    ""
).strip()

STUDENTS_FILE = "students.txt"
DEFAULT_GRADES_FILE = "grades.txt"


# ============================================================
# COLOR PALETTE
# ============================================================

BG_COLOR = "#121212"
CARD_COLOR = "#1E1E1E"
CHIP_COLOR = "#242424"
PRIMARY_COLOR = "#3B82F6"
PRIMARY_HOVER = "#2563EB"
TEXT_COLOR = "#E0E0E0"
SECONDARY_TEXT = "#9AA4B2"
BORDER_COLOR = "#2D2D2D"
SUCCESS_COLOR = "#22C55E"
DANGER_COLOR = "#EF4444"
DANGER_HOVER = "#DC2626"
ENTRY_COLOR = "#1E1E1E"
SELECTED_ROW = "#1E3A5F"
LOG_BG = "#0D1117"
LOG_TEXT = "#B9F6CA"


# ============================================================
# PURE DOMAIN / CALCULATION FUNCTIONS (DATA LAYER)
# ============================================================

def honors_status(average: float) -> str:
    """
    Pure function to determine honors status based on weighted average.
    Scale: 1.75 or better (lower is better) yields 'With Honors'.
    """
    if average > 0.0 and average <= 1.75:
        return "With Honors"
    return "Regular"


# ============================================================
# MAIN APPLICATION (PRESENTATION LAYER)
# ============================================================

class GradeReportApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("960x780")
        self.minsize(850, 720)
        self.center_window()
        self.configure(bg=BG_COLOR)
        self.resizable(True, True)

        # ----------------------------------------------------
        # Application data
        # ----------------------------------------------------

        self.grades_file = DEFAULT_GRADES_FILE
        self.students = []
        self.selected_student_id = None
        self.records = []
        self.student_name = ""
        self.program_year = ""

        self.setup_style()
        self.create_variables()
        self.build_ui()

        self.after(100, self.startup_load)

    # ========================================================
    # WINDOW
    # ========================================================

    def center_window(self):
        self.update_idletasks()

        width = 960
        height = 780

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")

    def center_dialog(self, dialog, width, height):
        self.update_idletasks()

        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_w = self.winfo_width()
        parent_h = self.winfo_height()

        x = parent_x + (parent_w - width) // 2
        y = parent_y + (parent_h - height) // 2

        dialog.geometry(
            f"{width}x{height}+{max(x, 0)}+{max(y, 0)}"
        )

    # ========================================================
    # STYLE
    # ========================================================

    def setup_style(self):
        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", font=("Segoe UI", 10))

        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            foreground="white",
            background=PRIMARY_COLOR,
            padding=(18, 9),
            borderwidth=0
        )

        style.map(
            "Primary.TButton",
            background=[
                ("active", PRIMARY_HOVER),
                ("pressed", PRIMARY_HOVER)
            ]
        )

        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 9),
            foreground=TEXT_COLOR,
            background=CHIP_COLOR,
            padding=(12, 7),
            borderwidth=0
        )

        style.map(
            "Secondary.TButton",
            background=[
                ("active", "#2E2E2E"),
                ("pressed", "#383838")
            ]
        )

        style.configure(
            "Danger.TButton",
            font=("Segoe UI", 9, "bold"),
            foreground="white",
            background=DANGER_COLOR,
            padding=(12, 7),
            borderwidth=0
        )

        style.map(
            "Danger.TButton",
            background=[
                ("active", DANGER_HOVER),
                ("pressed", DANGER_HOVER)
            ]
        )

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 20, "bold"),
            foreground=TEXT_COLOR,
            background=BG_COLOR
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 9),
            foreground=SECONDARY_TEXT,
            background=BG_COLOR
        )

        style.configure(
            "Treeview",
            background=CARD_COLOR,
            fieldbackground=CARD_COLOR,
            foreground=TEXT_COLOR,
            rowheight=34,
            font=("Segoe UI", 9),
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background="#2D2D2D",
            foreground=TEXT_COLOR,
            font=("Segoe UI", 9, "bold"),
            padding=8,
            borderwidth=0
        )

        style.map(
            "Treeview",
            background=[("selected", SELECTED_ROW)],
            foreground=[("selected", TEXT_COLOR)]
        )

        self.option_add("*TCombobox*Listbox.background", ENTRY_COLOR)
        self.option_add("*TCombobox*Listbox.foreground", TEXT_COLOR)
        self.option_add("*TCombobox*Listbox.selectBackground", SELECTED_ROW)
        self.option_add("*TCombobox*Listbox.selectForeground", TEXT_COLOR)

        style.configure(
            "Modern.TEntry",
            padding=8,
            font=("Segoe UI", 10),
            fieldbackground=ENTRY_COLOR,
            foreground=TEXT_COLOR,
            bordercolor=BORDER_COLOR,
            insertcolor=TEXT_COLOR
        )
        style.configure(
            "Modern.TCombobox",
            padding=7,
            font=("Segoe UI", 10),
            fieldbackground=ENTRY_COLOR,
            background=ENTRY_COLOR,
            foreground=TEXT_COLOR,
            arrowcolor=TEXT_COLOR,
            bordercolor=BORDER_COLOR
        )
        style.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", ENTRY_COLOR)],
            foreground=[("readonly", TEXT_COLOR)]
        )

        style.configure(
            "Vertical.TScrollbar",
            background=CHIP_COLOR,
            troughcolor=BG_COLOR,
            bordercolor=BG_COLOR,
            arrowcolor=TEXT_COLOR
        )
        style.map(
            "Vertical.TScrollbar",
            background=[("active", "#3D3D3D")]
        )

    # ========================================================
    # VARIABLES
    # ========================================================

    def create_variables(self):
        self.recipient_var = tk.StringVar()
        self.file_var = tk.StringVar(value=self.grades_file)
        self.total_units_var = tk.StringVar(value="0")
        self.average_var = tk.StringVar(value="0.00")
        self.honors_var = tk.StringVar(value="Regular")
        self.status_var = tk.StringVar(value="Ready")
        self.student_var = tk.StringVar(value="—")
        self.program_var = tk.StringVar(value="—")
        self.student_selector_var = tk.StringVar()

    # ========================================================
    # USER INTERFACE
    # ========================================================

    def build_ui(self):
        outer = tk.Frame(self, bg=BG_COLOR)
        outer.pack(fill="both", expand=True, padx=28, pady=22)

        # Header
        header = tk.Frame(outer, bg=BG_COLOR)
        header.pack(fill="x", pady=(0, 18))

        title_area = tk.Frame(header, bg=BG_COLOR)
        title_area.pack(side="left")

        tk.Label(
            title_area,
            text="NDMU Grade Report",
            font=("Segoe UI", 21, "bold"),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="University grade management and email delivery",
            font=("Segoe UI", 9),
            fg=SECONDARY_TEXT,
            bg=BG_COLOR
        ).pack(anchor="w", pady=(2, 0))

        status_frame = tk.Frame(header, bg=BG_COLOR)
        status_frame.pack(side="right", pady=6)

        self.status_dot = tk.Label(
            status_frame,
            text="●",
            font=("Segoe UI", 9),
            fg=SUCCESS_COLOR,
            bg=BG_COLOR
        )
        self.status_dot.pack(side="left", padx=(0, 5))

        tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            fg=SECONDARY_TEXT,
            bg=BG_COLOR
        ).pack(side="left")

        # Student Information Card
        student_card = self.create_card(outer)
        student_card.pack(fill="x", pady=(0, 14))

        student_header = tk.Frame(student_card, bg=CARD_COLOR)
        student_header.pack(fill="x", padx=18, pady=(14, 8))

        tk.Label(
            student_header,
            text="Student Information",
            font=("Segoe UI", 10, "bold"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR
        ).pack(side="left")

        selector_area = tk.Frame(student_header, bg=CARD_COLOR)
        selector_area.pack(side="right")

        tk.Label(
            selector_area,
            text="STUDENT:",
            font=("Segoe UI", 8, "bold"),
            fg=SECONDARY_TEXT,
            bg=CARD_COLOR
        ).pack(side="left", padx=(0, 6))

        self.student_combo = ttk.Combobox(
            selector_area,
            textvariable=self.student_selector_var,
            state="readonly",
            width=28,
            style="Modern.TCombobox"
        )
        self.student_combo.pack(side="left", padx=(0, 6))
        self.student_combo.bind("<<ComboboxSelected>>", self.on_student_selected)

        ttk.Button(
            selector_area,
            text="+ Add Student",
            style="Primary.TButton",
            command=self.open_add_student
        ).pack(side="left")

        info_row = tk.Frame(student_card, bg=CARD_COLOR)
        info_row.pack(fill="x", padx=18, pady=(0, 15))

        student_box = tk.Frame(info_row, bg=CARD_COLOR)
        student_box.pack(side="left", fill="x", expand=True)

        tk.Label(
            student_box,
            text="STUDENT",
            font=("Segoe UI", 8, "bold"),
            fg=SECONDARY_TEXT,
            bg=CARD_COLOR
        ).pack(anchor="w")

        tk.Label(
            student_box,
            textvariable=self.student_var,
            font=("Segoe UI", 11, "bold"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR
        ).pack(anchor="w", pady=(3, 0))

        program_box = tk.Frame(info_row, bg=CARD_COLOR)
        program_box.pack(side="left", fill="x", expand=True)

        tk.Label(
            program_box,
            text="PROGRAM & YEAR",
            font=("Segoe UI", 8, "bold"),
            fg=SECONDARY_TEXT,
            bg=CARD_COLOR
        ).pack(anchor="w")

        tk.Label(
            program_box,
            textvariable=self.program_var,
            font=("Segoe UI", 11, "bold"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR
        ).pack(anchor="w", pady=(3, 0))

        # Grades Card
        grades_card = self.create_card(outer)
        grades_card.pack(fill="x", pady=(0, 14))

        grades_header = tk.Frame(grades_card, bg=CARD_COLOR)
        grades_header.pack(fill="x", padx=18, pady=(14, 9))

        tk.Label(
            grades_header,
            text="Course Grades",
            font=("Segoe UI", 10, "bold"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR
        ).pack(side="left")

        action_frame = tk.Frame(grades_header, bg=CARD_COLOR)
        action_frame.pack(side="right")

        ttk.Button(
            action_frame,
            text="Edit Grade",
            style="Secondary.TButton",
            command=self.edit_grade
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            action_frame,
            text="Delete Grade",
            style="Danger.TButton",
            command=self.delete_grade
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            action_frame,
            text="↻  Reload from File",
            style="Secondary.TButton",
            command=self.reload_from_file
        ).pack(side="left")

        table_frame = tk.Frame(grades_card, bg=CARD_COLOR)
        table_frame.pack(fill="x", padx=18)

        columns = ("code", "title", "units", "grade")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=6
        )

        self.tree.heading("code", text="COURSE CODE")
        self.tree.heading("title", text="COURSE TITLE")
        self.tree.heading("units", text="UNITS")
        self.tree.heading("grade", text="GRADE")

        self.tree.column("code", width=130, anchor="w")
        self.tree.column("title", width=430, anchor="w")
        self.tree.column("units", width=70, anchor="center")
        self.tree.column("grade", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda event: self.edit_grade())

        summary = tk.Frame(grades_card, bg=CARD_COLOR)
        summary.pack(fill="x", padx=18, pady=(10, 15))

        units_summary = tk.Frame(summary, bg=CHIP_COLOR)
        units_summary.pack(side="left", padx=(0, 10))

        tk.Label(
            units_summary,
            text="TOTAL UNITS",
            font=("Segoe UI", 8, "bold"),
            fg=SECONDARY_TEXT,
            bg=CHIP_COLOR
        ).pack(side="left", padx=(12, 6), pady=9)

        tk.Label(
            units_summary,
            textvariable=self.total_units_var,
            font=("Segoe UI", 10, "bold"),
            fg=TEXT_COLOR,
            bg=CHIP_COLOR
        ).pack(side="left", padx=(0, 12))

        average_summary = tk.Frame(summary, bg=CHIP_COLOR)
        average_summary.pack(side="left", padx=(0, 10))

        tk.Label(
            average_summary,
            text="WEIGHTED AVERAGE",
            font=("Segoe UI", 8, "bold"),
            fg=SECONDARY_TEXT,
            bg=CHIP_COLOR
        ).pack(side="left", padx=(12, 6), pady=9)

        tk.Label(
            average_summary,
            textvariable=self.average_var,
            font=("Segoe UI", 10, "bold"),
            fg=PRIMARY_COLOR,
            bg=CHIP_COLOR
        ).pack(side="left", padx=(0, 12))

        honors_summary = tk.Frame(summary, bg=CHIP_COLOR)
        honors_summary.pack(side="left")

        tk.Label(
            honors_summary,
            text="HONORS STATUS",
            font=("Segoe UI", 8, "bold"),
            fg=SECONDARY_TEXT,
            bg=CHIP_COLOR
        ).pack(side="left", padx=(12, 6), pady=9)

        tk.Label(
            honors_summary,
            textvariable=self.honors_var,
            font=("Segoe UI", 10, "bold"),
            fg=SUCCESS_COLOR,
            bg=CHIP_COLOR
        ).pack(side="left", padx=(0, 12))

        # Email Card (Clean Inline Layout)
        email_card = self.create_card(outer)
        email_card.pack(fill="x", pady=(0, 14))

        email_content = tk.Frame(email_card, bg=CARD_COLOR)
        email_content.pack(fill="x", padx=18, pady=14)

        tk.Label(
            email_content,
            text="Send Grade Report",
            font=("Segoe UI", 10, "bold"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR
        ).pack(side="left", padx=(0, 20))

        tk.Label(
            email_content,
            text="Recipient Email:",
            font=("Segoe UI", 9),
            fg=SECONDARY_TEXT,
            bg=CARD_COLOR
        ).pack(side="left", padx=(0, 8))

        self.email_entry = ttk.Entry(
            email_content,
            textvariable=self.recipient_var,
            style="Modern.TEntry"
        )
        self.email_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        ttk.Button(
            email_content,
            text="Send Report",
            style="Primary.TButton",
            command=self.send_report
        ).pack(side="right")

        # Delivery Log
        log_header = tk.Frame(outer, bg=BG_COLOR)
        log_header.pack(fill="x", pady=(0, 5))

        tk.Label(
            log_header,
            text="Delivery Log",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(side="left")

        ttk.Button(
            log_header,
            text="Clear",
            style="Secondary.TButton",
            command=self.clear_log
        ).pack(side="right")

        self.log = tk.Text(
            outer,
            height=5,
            bg=LOG_BG,
            fg=LOG_TEXT,
            insertbackground="white",
            font=("Consolas", 9),
            relief="flat",
            bd=0,
            padx=12,
            pady=9
        )
        self.log.pack(fill="x")

    # ========================================================
    # CARD
    # ========================================================

    def create_card(self, parent):
        return tk.Frame(
            parent,
            bg=CARD_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightcolor=BORDER_COLOR,
            highlightthickness=1,
            bd=0
        )

    # ========================================================
    # LOGGING
    # ========================================================

    def log_message(self, message):
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.status_var.set(message)

    def clear_log(self):
        self.log.delete("1.0", "end")
        self.status_var.set("Log cleared")

    # ========================================================
    # PERSISTENT DATABASE
    # ========================================================

    def startup_load(self):
        if self.load_student_database():
            self.log_message(
                f"READY   -> {len(self.students)} student(s) loaded from students.txt."
            )
            return

        if os.path.exists(self.grades_file):
            try:
                records = self.parse_grades(self.grades_file)
                if records:
                    student = self.create_student_object(
                        self.student_name,
                        self.program_year,
                        records
                    )
                    self.students = [student]
                    self.selected_student_id = student["id"]
                    self.save_student_database()
                    self.refresh_student_selector()
                    self.display_selected_student()

                    self.log_message(
                        "IMPORTED -> Existing grades.txt was saved into students.txt."
                    )
                    return
            except Exception as exc:
                self.log_message(f"WARNING -> Could not import grades.txt: {exc}")

        self.load_sample_student()
        self.save_student_database()
        self.log_message("READY   -> New TXT student database created.")

    def create_student_object(self, name, program_year, records=None):
        return {
            "id": str(uuid.uuid4()),
            "name": name.strip(),
            "program_year": program_year.strip(),
            "courses": records or []
        }

    def save_student_database(self):
        temp_file = STUDENTS_FILE + ".tmp"
        try:
            with open(temp_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, lineterminator="\n")
                writer.writerow(["NDMU_STUDENT_DATABASE", "1"])
                writer.writerow(["SELECTED_STUDENT_ID", self.selected_student_id or ""])
                writer.writerow([])

                for student in self.students:
                    writer.writerow(["[STUDENT]"])
                    writer.writerow(["ID", student.get("id", str(uuid.uuid4()))])
                    writer.writerow(["NAME", student.get("name", "")])
                    writer.writerow(["PROGRAM_YEAR", student.get("program_year", "")])

                    for course in student.get("courses", []):
                        writer.writerow([
                            "COURSE",
                            course.get("code", ""),
                            course.get("title", ""),
                            f'{float(course.get("units", 0)):g}',
                            f'{float(course.get("grade", 0)):.2f}'
                        ])

                    writer.writerow(["[/STUDENT]"])
                    writer.writerow([])

            os.replace(temp_file, STUDENTS_FILE)
            return True

        except Exception as exc:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except OSError:
                pass

            messagebox.showerror(
                "Database Save Error",
                f"Could not save the student database.\n\n{exc}"
            )
            return False

    def load_student_database(self):
        if not os.path.exists(STUDENTS_FILE):
            return False

        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)

            if not rows or len(rows[0]) < 2 or rows[0][0].strip() != "NDMU_STUDENT_DATABASE":
                raise ValueError("Invalid students.txt format.")

            saved_selected_id = None
            valid_students = []
            current_student = None

            for row in rows[1:]:
                if not row:
                    continue

                key = row[0].strip()

                if key == "SELECTED_STUDENT_ID":
                    if len(row) > 1:
                        saved_selected_id = row[1].strip()

                elif key == "[STUDENT]":
                    current_student = {
                        "id": str(uuid.uuid4()),
                        "name": "",
                        "program_year": "",
                        "courses": []
                    }

                elif key == "[/STUDENT]":
                    if current_student and current_student["name"].strip():
                        valid_students.append(current_student)
                    current_student = None

                elif current_student is not None:
                    if key == "ID" and len(row) > 1:
                        current_student["id"] = row[1].strip() or str(uuid.uuid4())
                    elif key == "NAME" and len(row) > 1:
                        current_student["name"] = row[1].strip()
                    elif key == "PROGRAM_YEAR" and len(row) > 1:
                        current_student["program_year"] = row[1].strip()
                    elif key == "COURSE":
                        if len(row) >= 5:
                            try:
                                current_student["courses"].append({
                                    "code": row[1].strip(),
                                    "title": row[2].strip(),
                                    "units": float(row[3]),
                                    "grade": float(row[4])
                                })
                            except (ValueError, TypeError):
                                continue

            if current_student and current_student["name"].strip():
                valid_students.append(current_student)

            self.students = valid_students

            if saved_selected_id and any(s["id"] == saved_selected_id for s in self.students):
                self.selected_student_id = saved_selected_id
            elif self.students:
                self.selected_student_id = self.students[0]["id"]
            else:
                self.selected_student_id = None

            self.refresh_student_selector()

            if self.selected_student_id:
                self.display_selected_student()

            return bool(self.students)

        except Exception as exc:
            messagebox.showerror(
                "Database Error",
                f"The TXT student database could not be read.\n\n{exc}"
            )
            return False

    # ========================================================
    # STUDENT SELECTION
    # ========================================================

    def refresh_student_selector(self):
        names = [student["name"] for student in self.students]
        self.student_combo["values"] = names

        selected = self.get_selected_student()
        if selected:
            self.student_selector_var.set(selected["name"])
        else:
            self.student_selector_var.set("")

    def get_selected_student(self):
        if not self.selected_student_id:
            return None

        for student in self.students:
            if student["id"] == self.selected_student_id:
                return student

        return None

    def on_student_selected(self, event=None):
        selected_name = self.student_selector_var.get().strip()

        for student in self.students:
            if student["name"] == selected_name:
                self.selected_student_id = student["id"]
                self.save_student_database()
                self.display_selected_student()
                self.log_message(f"SELECTED -> {student['name']}")
                return

    def display_selected_student(self):
        student = self.get_selected_student()

        if not student:
            self.student_name = ""
            self.program_year = ""
            self.student_var.set("—")
            self.program_var.set("—")
            self.records = []
            self.display_records([])
            return

        self.student_name = student["name"]
        self.program_year = student["program_year"]
        self.student_var.set(self.student_name)
        self.program_var.set(self.program_year)
        self.records = [dict(course) for course in student.get("courses", [])]
        self.display_records(self.records)

    # ========================================================
    # ADD STUDENT
    # ========================================================

    def open_add_student(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New Student")
        dialog.geometry("700x650")
        dialog.minsize(680, 620)
        dialog.configure(bg=BG_COLOR)
        dialog.transient(self)
        dialog.grab_set()

        self.center_dialog(dialog, 700, 650)

        container = tk.Frame(
            dialog,
            bg=CARD_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        container.pack(fill="both", expand=True, padx=12, pady=12)

        header = tk.Frame(container, bg=CARD_COLOR)
        header.pack(fill="x", padx=22, pady=(18, 8))

        tk.Label(
            header,
            text="+  Add New Student",
            font=("Segoe UI", 12, "bold"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR
        ).pack(side="left")

        tk.Button(
            header,
            text="×",
            font=("Segoe UI", 16),
            fg=SECONDARY_TEXT,
            bg=CARD_COLOR,
            activebackground=CARD_COLOR,
            activeforeground=TEXT_COLOR,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=dialog.destroy
        ).pack(side="right")

        tk.Label(
            container,
            text="New Student",
            font=("Segoe UI", 18, "bold"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR
        ).pack(anchor="w", padx=22, pady=(2, 14))

        form = tk.Frame(container, bg=CARD_COLOR)
        form.pack(fill="x", padx=22)

        name_var = tk.StringVar()
        program_var = tk.StringVar()

        name_entry = self.create_form_field(form, "Full Name:", name_var, 0)
        self.create_form_field(form, "Program & Year:", program_var, 1)

        tk.Label(
            container,
            text="Add each course this student is taking, then click Create Student.",
            font=("Segoe UI", 9),
            fg=SECONDARY_TEXT,
            bg=CARD_COLOR
        ).pack(anchor="w", padx=22, pady=(18, 10))

        course_form = tk.Frame(container, bg=CARD_COLOR)
        course_form.pack(fill="x", padx=22)

        code_var = tk.StringVar()
        title_var = tk.StringVar()
        units_var = tk.StringVar()
        grade_var = tk.StringVar()

        for text, column in [("Code", 0), ("Title", 1), ("Units", 2), ("Grade", 3)]:
            tk.Label(
                course_form,
                text=text,
                font=("Segoe UI", 8, "bold"),
                fg=SECONDARY_TEXT,
                bg=CARD_COLOR
            ).grid(row=0, column=column, sticky="w", padx=(0, 8))

        code_entry = ttk.Entry(course_form, textvariable=code_var, style="Modern.TEntry")
        title_entry = ttk.Entry(course_form, textvariable=title_var, style="Modern.TEntry")
        units_entry = ttk.Entry(course_form, textvariable=units_var, style="Modern.TEntry")
        grade_entry = ttk.Entry(course_form, textvariable=grade_var, style="Modern.TEntry")

        code_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(2, 0))
        title_entry.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(2, 0))
        units_entry.grid(row=1, column=2, sticky="ew", padx=(0, 8), pady=(2, 0))
        grade_entry.grid(row=1, column=3, sticky="ew", pady=(2, 0))

        course_form.columnconfigure(0, weight=1)
        course_form.columnconfigure(1, weight=4)
        course_form.columnconfigure(2, weight=1)
        course_form.columnconfigure(3, weight=1)

        course_list_frame = tk.Frame(container, bg=CARD_COLOR)
        course_list_frame.pack(fill="both", expand=True, padx=22, pady=(14, 0))

        course_tree = ttk.Treeview(
            course_list_frame,
            columns=("code", "title", "units", "grade"),
            show="headings",
            selectmode="browse",
            height=8
        )

        course_tree.heading("code", text="CODE")
        course_tree.heading("title", text="TITLE")
        course_tree.heading("units", text="UNITS")
        course_tree.heading("grade", text="GRADE")

        course_tree.column("code", width=100, anchor="w")
        course_tree.column("title", width=280, anchor="w")
        course_tree.column("units", width=70, anchor="center")
        course_tree.column("grade", width=80, anchor="center")

        course_scroll = ttk.Scrollbar(
            course_list_frame,
            orient="vertical",
            command=course_tree.yview
        )

        course_tree.configure(yscrollcommand=course_scroll.set)
        course_tree.pack(side="left", fill="both", expand=True)
        course_scroll.pack(side="right", fill="y")

        course_buttons = tk.Frame(container, bg=CARD_COLOR)
        course_buttons.pack(fill="x", padx=22, pady=(8, 8))

        def clear_course_fields():
            code_var.set("")
            title_var.set("")
            units_var.set("")
            grade_var.set("")
            code_entry.focus_set()

        def add_course_to_list():
            code = code_var.get().strip()
            title = title_var.get().strip()
            units_text = units_var.get().strip()
            grade_text = grade_var.get().strip()

            if not code or not title:
                messagebox.showwarning("Incomplete Course", "Course code and title are required.", parent=dialog)
                return

            if not self.is_number(units_text):
                messagebox.showwarning("Invalid Units", "Units must be a number.", parent=dialog)
                return

            if not self.is_number(grade_text):
                messagebox.showwarning("Invalid Grade", "Grade must be a number such as 1.25 or 2.00.", parent=dialog)
                return

            units = float(units_text)
            grade = float(grade_text)

            if units <= 0:
                messagebox.showwarning("Invalid Units", "Units must be greater than zero.", parent=dialog)
                return

            if grade < 1 or grade > 5:
                messagebox.showwarning("Invalid Grade", "Please enter a grade from 1.00 to 5.00.", parent=dialog)
                return

            for item in course_tree.get_children():
                existing_code = course_tree.item(item, "values")[0]
                if existing_code.lower() == code.lower():
                    messagebox.showwarning("Duplicate Course", f"{code} is already in the course list.", parent=dialog)
                    return

            course_tree.insert("", "end", values=(code, title, f"{units:g}", f"{grade:.2f}"))
            clear_course_fields()

        def remove_selected_course():
            selected = course_tree.selection()
            if not selected:
                messagebox.showwarning("No Course Selected", "Select a course to remove.", parent=dialog)
                return
            course_tree.delete(selected[0])

        ttk.Button(course_buttons, text="+ Add Course to List", style="Secondary.TButton", command=add_course_to_list).pack(side="left")
        ttk.Button(course_buttons, text="Remove Selected", style="Secondary.TButton", command=remove_selected_course).pack(side="right")

        footer = tk.Frame(container, bg=CARD_COLOR)
        footer.pack(fill="x", padx=22, pady=(10, 20))

        def create_student():
            name = name_var.get().strip()
            program = program_var.get().strip()

            if not name:
                messagebox.showwarning("Missing Student Name", "Please enter the student's full name.", parent=dialog)
                return

            if not program:
                messagebox.showwarning("Missing Program", "Please enter the student's program and year.", parent=dialog)
                return

            items = course_tree.get_children()
            if not items:
                messagebox.showwarning("No Courses", "Add at least one course before creating the student.", parent=dialog)
                return

            for existing in self.students:
                if (existing["name"].casefold() == name.casefold() and existing["program_year"].casefold() == program.casefold()):
                    messagebox.showwarning("Student Already Exists", f"{name} ({program}) already exists.", parent=dialog)
                    return

            new_records = []
            for item in items:
                code, title, units, grade = course_tree.item(item, "values")
                new_records.append({
                    "code": code,
                    "title": title,
                    "units": float(units),
                    "grade": float(grade)
                })

            new_student = self.create_student_object(name, program, new_records)
            self.students.append(new_student)
            self.selected_student_id = new_student["id"]

            if not self.save_student_database():
                self.students.pop()
                return

            self.refresh_student_selector()
            self.display_selected_student()
            self.log_message(f"CREATED -> {name} with {len(new_records)} course(s).")

            dialog.destroy()
            messagebox.showinfo(
                "Student Created",
                f"{name} was created successfully.\n\nSaved permanently in students.txt.",
                parent=self
            )

        ttk.Button(footer, text="Create Student", style="Primary.TButton", command=create_student).pack(side="right", padx=(8, 0))
        ttk.Button(footer, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="right")

        dialog.bind("<Escape>", lambda event: dialog.destroy())
        grade_entry.bind("<Return>", lambda event: add_course_to_list())
        name_entry.focus_set()

    # ========================================================
    # FORM FIELD
    # ========================================================

    def create_form_field(self, parent, label_text, variable, row):
        tk.Label(
            parent,
            text=label_text,
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR
        ).grid(row=row, column=0, sticky="w", padx=(0, 16), pady=7)

        entry = ttk.Entry(parent, textvariable=variable, style="Modern.TEntry")
        entry.grid(row=row, column=1, sticky="ew", pady=7)
        parent.columnconfigure(1, weight=1)
        return entry

    # ========================================================
    # EDIT GRADE
    # ========================================================

    def edit_grade(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Grade Selected", "Select a course from the table first.")
            return

        student = self.get_selected_student()
        if not student:
            return

        item_id = selected[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return

        code, title, units, grade = values
        index = self.tree.index(item_id)

        dialog = tk.Toplevel(self)
        dialog.title("Edit Grade")
        dialog.geometry("500x430")
        dialog.resizable(False, False)
        dialog.configure(bg=BG_COLOR)
        dialog.transient(self)
        dialog.grab_set()

        self.center_dialog(dialog, 500, 430)

        card = tk.Frame(
            dialog,
            bg=CARD_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1
        )
        card.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(
            card,
            text="Edit Grade",
            font=("Segoe UI", 18, "bold"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR
        ).pack(anchor="w", padx=24, pady=(24, 4))

        tk.Label(
            card,
            text="Update the selected course information.",
            font=("Segoe UI", 9),
            fg=SECONDARY_TEXT,
            bg=CARD_COLOR
        ).pack(anchor="w", padx=24, pady=(0, 20))

        form = tk.Frame(card, bg=CARD_COLOR)
        form.pack(fill="x", padx=24)

        code_var = tk.StringVar(value=code)
        title_var = tk.StringVar(value=title)
        units_var = tk.StringVar(value=units)
        grade_var = tk.StringVar(value=grade)

        code_entry = self.create_form_field(form, "Course Code:", code_var, 0)
        self.create_form_field(form, "Course Title:", title_var, 1)
        self.create_form_field(form, "Units:", units_var, 2)
        grade_entry = self.create_form_field(form, "Grade:", grade_var, 3)

        footer = tk.Frame(card, bg=CARD_COLOR)
        footer.pack(fill="x", padx=24, pady=(28, 22))

        def update_course():
            new_code = code_var.get().strip()
            new_title = title_var.get().strip()
            units_text = units_var.get().strip()
            grade_text = grade_var.get().strip()

            if not new_code or not new_title:
                messagebox.showwarning("Incomplete Information", "Course code and title are required.", parent=dialog)
                return

            if not self.is_number(units_text) or not self.is_number(grade_text):
                messagebox.showwarning("Invalid Input", "Units and Grade must be numbers.", parent=dialog)
                return

            new_units = float(units_text)
            new_grade = float(grade_text)

            if new_units <= 0 or new_grade < 1 or new_grade > 5:
                messagebox.showwarning("Invalid Values", "Ensure Units > 0 and Grade is 1.00-5.00.", parent=dialog)
                return

            for course_index, existing in enumerate(student["courses"]):
                if course_index == index:
                    continue
                if existing["code"].casefold() == new_code.casefold():
                    messagebox.showwarning("Duplicate Course", f"{new_code} already exists.", parent=dialog)
                    return

            student["courses"][index] = {
                "code": new_code,
                "title": new_title,
                "units": new_units,
                "grade": new_grade
            }

            self.records = [dict(course) for course in student["courses"]]

            if not self.save_student_database():
                return

            self.display_selected_student()

            children = self.tree.get_children()
            if index < len(children):
                self.tree.selection_set(children[index])
                self.tree.focus(children[index])

            self.log_message(f"UPDATED -> {new_code} grade changed to {new_grade:.2f} for {student['name']}.")
            dialog.destroy()

        ttk.Button(footer, text="Update Grade", style="Primary.TButton", command=update_course).pack(side="right", padx=(8, 0))
        ttk.Button(footer, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="right")

        grade_entry.bind("<Return>", lambda event: update_course())
        code_entry.focus_set()

    # ========================================================
    # DELETE GRADE
    # ========================================================

    def delete_grade(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Grade Selected", "Select a course from the table first.")
            return

        student = self.get_selected_student()
        if not student:
            return

        item_id = selected[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return

        code, title, units, grade = values

        confirmed = messagebox.askyesno(
            "Delete Grade",
            f"Are you sure you want to delete this course?\n\n{code} - {title}\nUnits: {units}\nGrade: {grade}"
        )
        if not confirmed:
            return

        index = self.tree.index(item_id)
        if 0 <= index < len(student["courses"]):
            student["courses"].pop(index)

        self.records = [dict(course) for course in student["courses"]]

        if not self.save_student_database():
            return

        self.display_selected_student()
        self.log_message(f"DELETED -> {code} removed from {student['name']}'s grade report.")

    # ========================================================
    # RELOAD FROM FILE
    # ========================================================

    def reload_from_file(self):
        selected_student = self.get_selected_student()
        path = self.file_var.get().strip()

        if not path or not os.path.exists(path):
            path = filedialog.askopenfilename(
                title="Select grades.txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not path:
                return
            self.file_var.set(path)

        try:
            records = self.parse_grades(path)
            if not records:
                raise ValueError("No valid grade records were found.")

            if selected_student:
                selected_student["name"] = self.student_name
                selected_student["program_year"] = self.program_year
                selected_student["courses"] = records
                self.selected_student_id = selected_student["id"]

                self.save_student_database()
                self.refresh_student_selector()
                self.display_selected_student()
                self.log_message(f"RELOADED -> {len(records)} course(s) into {selected_student['name']}.")
            else:
                new_student = self.create_student_object(self.student_name, self.program_year, records)
                self.students.append(new_student)
                self.selected_student_id = new_student["id"]

                self.save_student_database()
                self.refresh_student_selector()
                self.display_selected_student()
                self.log_message("RELOADED -> File imported as a new student.")

        except Exception as exc:
            messagebox.showerror("Reload Error", str(exc))

    # ========================================================
    # PARSE grades.txt
    # ========================================================

    def parse_grades(self, path):
        records = []
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(line for line in f if line.strip() and not line.strip().startswith("#"))
            rows = list(reader)

        if not rows:
            return records

        student_info = [part.strip() for part in rows[0]]
        if len(student_info) < 2:
            raise ValueError("The first line must contain: Student Name, Program & Year")

        self.student_name = student_info[0]
        self.program_year = ",".join(student_info[1:]).strip()

        for row in rows[1:]:
            if len(row) < 4:
                continue

            code, title, units, grade = row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()

            if self.is_number(units) and self.is_number(grade) and code and title:
                records.append({
                    "code": code,
                    "title": title,
                    "units": float(units),
                    "grade": float(grade)
                })

        return records

    # ========================================================
    # SAMPLE STUDENT
    # ========================================================

    def load_sample_student(self):
        sample = self.create_student_object(
            "Andrae John V. Almodiente",
            "BSCS 2",
            [
                {"code": "CSCC 102", "title": "Fundamentals of Programming", "units": 3, "grade": 1.25},
                {"code": "CSMath 101", "title": "Trigonometric Mathematics", "units": 3, "grade": 2.00},
                {"code": "AH 111", "title": "Purposive Communication", "units": 3, "grade": 2.25}
            ]
        )
        self.students = [sample]
        self.selected_student_id = sample["id"]
        self.refresh_student_selector()
        self.display_selected_student()

    # ========================================================
    # DISPLAY GRADES
    # ========================================================

    def display_records(self, records):
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_units = 0
        weighted_points = 0

        for record in records:
            units = float(record["units"])
            grade = float(record["grade"])

            self.tree.insert(
                "",
                "end",
                values=(
                    record["code"],
                    record["title"],
                    f"{units:g}",
                    f"{grade:.2f}"
                )
            )

            total_units += units
            weighted_points += (units * grade)

        average = (weighted_points / total_units) if total_units else 0.0

        self.total_units_var.set(f"{total_units:g}")
        self.average_var.set(f"{average:.2f}")

        # Calculate and update Honors Status using the domain function
        self.honors_var.set(honors_status(average))

    # ========================================================
    # NUMBER CHECK
    # ========================================================

    @staticmethod
    def is_number(value):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    # ========================================================
    # SAVE CURRENT DATABASE TO grades.txt
    # ========================================================

    def save_current_student_to_grades_file(self):
        student = self.get_selected_student()
        if not student:
            return False

        path = self.file_var.get().strip() or DEFAULT_GRADES_FILE
        self.file_var.set(path)

        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, lineterminator="\n")
                writer.writerow([student["name"], student["program_year"]])

                for course in student["courses"]:
                    writer.writerow([
                        course["code"],
                        course["title"],
                        f'{float(course["units"]):g}',
                        f'{float(course["grade"]):.2f}'
                    ])
            return True
        except Exception as exc:
            messagebox.showerror("File Save Error", f"Could not save grades.txt.\n\n{exc}")
            return False

    # ========================================================
    # EMAIL BODY
    # ========================================================

    def create_email_body(self):
        rows = []
        for item in self.tree.get_children():
            code, title, units, grade = self.tree.item(item, "values")
            rows.append(f"<tr><td>{code}</td><td>{title}</td><td>{units}</td><td>{grade}</td></tr>")

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #172B4D; line-height: 1.5;">
            <h2>NDMU University Grade Report</h2>
            <p><b>Student:</b> {self.student_name}</p>
            <p><b>Program & Year:</b> {self.program_year}</p>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
                <tr><th>Course Code</th><th>Course Title</th><th>Units</th><th>Grade</th></tr>
                {''.join(rows)}
            </table>
            <p><b>Total Units:</b> {self.total_units_var.get()}</p>
            <p><b>Weighted Average:</b> {self.average_var.get()}</p>
            <p><b>Honors Status:</b> {self.honors_var.get()}</p>
        </body>
        </html>
        """

    # ========================================================
    # SEND REPORT THROUGH BREVO
    # ========================================================

    def send_report(self):
        recipient = self.recipient_var.get().strip()

        if not recipient:
            messagebox.showwarning("Missing Recipient", "Enter an email address.")
            return

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", recipient):
            messagebox.showwarning("Invalid Email", "Enter a valid email address.")
            return

        if not BREVO_API_KEY:
            messagebox.showinfo(
                "Brevo API Key Required",
                "BREVO_API_KEY is not configured.\n\nSet environment variable BREVO_API_KEY."
            )
            self.log_message("WAITING -> Brevo API key is not configured.")
            return

        self.log_message(f"SENDING -> Grade report to {recipient}...")

        payload = {
            "sender": {"name": "NDMU Grade Report Console", "email": DEFAULT_SENDER_EMAIL},
            "to": [{"email": recipient, "name": self.student_name}],
            "subject": f"Grade Report - {self.student_name}",
            "htmlContent": self.create_email_body()
        }

        request = urllib.request.Request(
            "https://api.brevo.com/v3/smtp/email",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "accept": "application/json",
                "api-key": BREVO_API_KEY,
                "content-type": "application/json"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                response.read()

            self.log_message(f"SENT    -> Successfully delivered to {recipient}")
            messagebox.showinfo("Report Sent", f"The grade report was successfully sent to:\n{recipient}")

        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            self.log_message(f"FAILED  -> Brevo HTTP {exc.code}: {details}")
            messagebox.showerror("Brevo Error", f"Brevo returned HTTP {exc.code}.\n\n{details}")

        except Exception as exc:
            self.log_message(f"FAILED  -> {exc}")
            messagebox.showerror("Sending Error", str(exc))


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":
    app = GradeReportApp()
    app.mainloop()