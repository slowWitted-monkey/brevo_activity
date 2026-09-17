import csv
import os
import tkinter as tk
from tkinter import messagebox, ttk


# ============================================================
# CONFIGURATION
# ============================================================

CSV_FILE = "ndmu_data.csv"


# ============================================================
# MAIN APPLICATION
# ============================================================

class CleanRedWoodyConsole(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("NDMU Grade Management System — Teacher & Student Panel")
        self.geometry("1100x700")
        self.minsize(1000, 650)

        # ----------------------------------------------------
        # COLOR PALETTE
        # ----------------------------------------------------
        self.COLOR_BROWN_DARK = "#2C1E16"
        self.COLOR_BROWN_LIGHT = "#3E2B20"
        self.COLOR_WHITE = "#FFFFFF"
        self.COLOR_WHITE_WARM = "#FAFAFA"
        self.COLOR_RED_PRIMARY = "#9E2A2B"
        self.COLOR_RED_HOVER = "#BD3A3C"
        self.COLOR_TEXT_DARK = "#2C1E16"

        self.configure(bg=self.COLOR_WHITE_WARM)

        self.selected_teacher = tk.StringVar(value="All Teachers")

        self._setup_styles()
        self._build_sidebar()
        self._build_workspace()

        self._init_csv()
        self.update_teacher_dropdown()
        self.load_data_from_csv()

    # ========================================================
    # GUI STYLING
    # ========================================================

    def _setup_styles(self):

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure(
            "Clean.Treeview",
            background=self.COLOR_WHITE,
            foreground=self.COLOR_TEXT_DARK,
            rowheight=30,
            fieldbackground=self.COLOR_WHITE,
            font=("Georgia", 9),
            borderwidth=1,
            relief="solid",
        )

        self.style.configure(
            "Clean.Treeview.Heading",
            background=self.COLOR_BROWN_DARK,
            foreground=self.COLOR_WHITE,
            font=("Georgia", 9, "bold"),
            relief="flat",
        )

        self.style.map(
            "Clean.Treeview",
            background=[
                ("selected", self.COLOR_RED_PRIMARY)
            ],
            foreground=[
                ("selected", self.COLOR_WHITE)
            ],
        )

    # ========================================================
    # BUTTON CREATOR
    # ========================================================

    def _create_btn(
            self,
            parent,
            text,
            bg_color,
            fg_color="#FFFFFF",
            command=None,
            pady=6
    ):

        return tk.Button(
            parent,
            text=text,
            font=("Georgia", 9, "bold"),
            bg=bg_color,
            fg=fg_color,
            activebackground=self.COLOR_RED_HOVER,
            activeforeground=self.COLOR_WHITE,
            relief="flat",
            bd=0,
            cursor="hand2",
            pady=pady,
            command=command,
        )

    # ========================================================
    # SIDEBAR
    # ========================================================

    def _build_sidebar(self):

        sidebar = tk.Frame(
            self,
            bg=self.COLOR_BROWN_DARK,
            width=240
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        sidebar.pack_propagate(False)

        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        brand_frame = tk.Frame(
            sidebar,
            bg=self.COLOR_BROWN_DARK
        )

        brand_frame.pack(
            fill="x",
            padx=18,
            pady=(25, 20)
        )

        tk.Label(
            brand_frame,
            text="NDMU CONSOLE",
            font=("Georgia", 14, "bold"),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_BROWN_DARK,
        ).pack(anchor="w")

        tk.Label(
            brand_frame,
            text="Teacher & Roster Console",
            font=("Georgia", 8, "italic"),
            fg=self.COLOR_RED_PRIMARY,
            bg=self.COLOR_BROWN_DARK,
        ).pack(anchor="w")

        tk.Frame(
            sidebar,
            bg=self.COLOR_RED_PRIMARY,
            height=2
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 20)
        )

        # ----------------------------------------------------
        # TEACHER & CLASS ACTIONS
        # ----------------------------------------------------

        tk.Label(
            sidebar,
            text="TEACHER & CLASS ACTIONS",
            font=("Georgia", 8, "bold"),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_BROWN_DARK,
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 8)
        )

        self._create_btn(
            sidebar,
            "+ Add Teacher / Course",
            self.COLOR_BROWN_LIGHT,
            self.COLOR_WHITE,
            self.open_add_teacher_dialog,
        ).pack(
            fill="x",
            padx=18,
            pady=3
        )

        self._create_btn(
            sidebar,
            "+ Enroll Student to Course",
            self.COLOR_RED_PRIMARY,
            self.COLOR_WHITE,
            self.open_add_student_to_course_dialog,
        ).pack(
            fill="x",
            padx=18,
            pady=3
        )

        self._create_btn(
            sidebar,
            " Update Student Grade",
            self.COLOR_BROWN_LIGHT,
            self.COLOR_WHITE,
            self.open_update_dialog,
        ).pack(
            fill="x",
            padx=18,
            pady=3
        )

        self._create_btn(
            sidebar,
            " Delete Selection",
            self.COLOR_RED_PRIMARY,
            self.COLOR_WHITE,
            self.delete_selected_row,
        ).pack(
            fill="x",
            padx=18,
            pady=3
        )

        tk.Frame(
            sidebar,
            bg=self.COLOR_BROWN_LIGHT,
            height=1
        ).pack(
            fill="x",
            padx=18,
            pady=15
        )

        # ----------------------------------------------------
        # MASTER VIEWS
        # ----------------------------------------------------

        tk.Label(
            sidebar,
            text="MASTER VIEWS",
            font=("Georgia", 8, "bold"),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_BROWN_DARK,
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 8)
        )

        self._create_btn(
            sidebar,
            "📋 View All Teachers",
            self.COLOR_BROWN_LIGHT,
            self.COLOR_WHITE,
            self.open_view_teachers_dialog,
        ).pack(
            fill="x",
            padx=18,
            pady=3
        )

        self._create_btn(
            sidebar,
            "🎓 View All Students",
            self.COLOR_BROWN_LIGHT,
            self.COLOR_WHITE,
            self.open_view_students_dialog,
        ).pack(
            fill="x",
            padx=18,
            pady=3
        )

        tk.Frame(
            sidebar,
            bg=self.COLOR_BROWN_LIGHT,
            height=1
        ).pack(
            fill="x",
            padx=18,
            pady=15
        )

        # ----------------------------------------------------
        # ANALYTICAL QUERIES
        # ----------------------------------------------------

        tk.Label(
            sidebar,
            text="ANALYTICAL QUERIES",
            font=("Georgia", 8, "bold"),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_BROWN_DARK,
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 8)
        )

        self._create_btn(
            sidebar,
            " Top Performing Student",
            self.COLOR_BROWN_LIGHT,
            self.COLOR_WHITE,
            lambda: self.run_query("top"),
        ).pack(
            fill="x",
            padx=18,
            pady=3
        )

        self._create_btn(
            sidebar,
            " Failures (Grade >= 3.0)",
            self.COLOR_RED_PRIMARY,
            self.COLOR_WHITE,
            lambda: self.run_query("failure"),
        ).pack(
            fill="x",
            padx=18,
            pady=3
        )

        self._create_btn(
            sidebar,
            " At-Risk (GWA 2.50 - 2.99)",
            self.COLOR_BROWN_LIGHT,
            self.COLOR_WHITE,
            lambda: self.run_query("risk"),
        ).pack(
            fill="x",
            padx=18,
            pady=3
        )

        self._create_btn(
            sidebar,
            "↻ Reset Record View",
            self.COLOR_BROWN_DARK,
            self.COLOR_WHITE,
            self.load_data_from_csv,
        ).pack(
            side="bottom",
            fill="x",
            padx=18,
            pady=20
        )

    # ========================================================
    # MAIN WORKSPACE
    # ========================================================

    def _build_workspace(self):

        workspace = tk.Frame(
            self,
            bg=self.COLOR_WHITE_WARM
        )

        workspace.pack(
            side="right",
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # ----------------------------------------------------
        # TOP BAR
        # ----------------------------------------------------

        top_bar = tk.Frame(
            workspace,
            bg=self.COLOR_WHITE_WARM
        )

        top_bar.pack(
            fill="x",
            pady=(0, 15)
        )

        # ----------------------------------------------------
        # SEARCH CARD
        # ----------------------------------------------------

        search_card = tk.Frame(
            top_bar,
            bg=self.COLOR_WHITE,
            bd=1,
            relief="solid",
            highlightbackground=self.COLOR_BROWN_DARK,
        )

        search_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        tk.Label(
            search_card,
            text="Search / Select Teacher:",
            font=("Georgia", 8, "bold"),
            fg=self.COLOR_RED_PRIMARY,
            bg=self.COLOR_WHITE,
        ).pack(
            anchor="w",
            padx=12,
            pady=(6, 2)
        )

        self.teacher_dropdown = ttk.Combobox(
            search_card,
            textvariable=self.selected_teacher
        )

        self.teacher_dropdown.pack(
            fill="x",
            padx=12,
            pady=(0, 4)
        )

        self.teacher_dropdown.bind(
            "<<ComboboxSelected>>",
            lambda e: self.load_data_from_csv()
        )

        self.teacher_dropdown.bind(
            "<KeyRelease>",
            lambda e: self.filter_teacher_search()
        )

        tk.Label(
            search_card,
            text="Filter Student Name / Course Code:",
            font=("Georgia", 8, "bold"),
            fg=self.COLOR_TEXT_DARK,
            bg=self.COLOR_WHITE,
        ).pack(
            anchor="w",
            padx=12,
            pady=(2, 2)
        )

        self.search_var = tk.StringVar()

        self.search_var.trace_add(
            "write",
            lambda *args: self.filter_table()
        )

        tk.Entry(
            search_card,
            textvariable=self.search_var,
            font=("Georgia", 9),
            bg=self.COLOR_WHITE_WARM,
            fg=self.COLOR_TEXT_DARK,
            relief="groove",
            bd=1,
        ).pack(
            fill="x",
            padx=12,
            pady=(0, 8)
        )

        # ----------------------------------------------------
        # STUDENT COUNT
        # ----------------------------------------------------

        students_count_card = tk.Frame(
            top_bar,
            bg=self.COLOR_BROWN_DARK,
            width=120,
            bd=0
        )

        students_count_card.pack(
            side="left",
            fill="y",
            padx=4
        )

        tk.Label(
            students_count_card,
            text="ENROLLED STUDENTS",
            font=("Georgia", 7, "bold"),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_BROWN_DARK,
        ).pack(
            padx=14,
            pady=(8, 0)
        )

        self.lbl_total_students = tk.Label(
            students_count_card,
            text="0",
            font=("Georgia", 15, "bold"),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_BROWN_DARK,
        )

        self.lbl_total_students.pack(
            padx=14,
            pady=(0, 8)
        )

        # ----------------------------------------------------
        # CLASS AVERAGE
        # ----------------------------------------------------

        gwa_card = tk.Frame(
            top_bar,
            bg=self.COLOR_RED_PRIMARY,
            width=120,
            bd=0
        )

        gwa_card.pack(
            side="left",
            fill="y",
            padx=(4, 0)
        )

        tk.Label(
            gwa_card,
            text="CLASS AVG GRADE",
            font=("Georgia", 7, "bold"),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_RED_PRIMARY,
        ).pack(
            padx=14,
            pady=(8, 0)
        )

        self.lbl_gwa = tk.Label(
            gwa_card,
            text="0.00",
            font=("Georgia", 15, "bold"),
            fg=self.COLOR_WHITE,
            bg=self.COLOR_RED_PRIMARY,
        )

        self.lbl_gwa.pack(
            padx=14,
            pady=(0, 8)
        )

        # ----------------------------------------------------
        # TABLE
        # ----------------------------------------------------

        table_frame = tk.Frame(
            workspace,
            bg=self.COLOR_WHITE,
            bd=1,
            relief="solid"
        )

        table_frame.pack(
            fill="both",
            expand=True,
            pady=(0, 15)
        )

        columns = (
            "student",
            "code",
            "title",
            "units",
            "grade",
            "teacher"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Clean.Treeview",
        )

        self.tree.heading(
            "student",
            text="Student Name",
            anchor="w"
        )

        self.tree.heading(
            "code",
            text="Course Code",
            anchor="w"
        )

        self.tree.heading(
            "title",
            text="Course Title",
            anchor="w"
        )

        self.tree.heading(
            "units",
            text="Units",
            anchor="center"
        )

        self.tree.heading(
            "grade",
            text="Grade",
            anchor="center"
        )

        self.tree.heading(
            "teacher",
            text="Assigned Teacher",
            anchor="w"
        )

        self.tree.column(
            "student",
            width=160,
            anchor="w"
        )

        self.tree.column(
            "code",
            width=80,
            anchor="w"
        )

        self.tree.column(
            "title",
            width=200,
            anchor="w"
        )

        self.tree.column(
            "units",
            width=60,
            anchor="center"
        )

        self.tree.column(
            "grade",
            width=70,
            anchor="center"
        )

        self.tree.column(
            "teacher",
            width=140,
            anchor="w"
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscroll=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # ----------------------------------------------------
        # ACTIVITY LOG
        # ----------------------------------------------------

        log_frame = tk.Frame(
            workspace,
            bg=self.COLOR_WHITE,
            bd=1,
            relief="solid"
        )

        log_frame.pack(
            fill="x",
            side="bottom"
        )

        tk.Label(
            log_frame,
            text="System Activity Log",
            font=("Georgia", 8, "bold"),
            fg=self.COLOR_RED_PRIMARY,
            bg=self.COLOR_WHITE,
        ).pack(
            anchor="w",
            padx=10,
            pady=(4, 1)
        )

        self.log_text = tk.Text(
            log_frame,
            height=3,
            font=("Consolas", 8),
            bg=self.COLOR_BROWN_DARK,
            fg=self.COLOR_WHITE,
            relief="flat",
        )

        self.log_text.pack(
            fill="x",
            padx=10,
            pady=(0, 6)
        )

        self.log_text.config(
            state="disabled"
        )

    # ========================================================
    # CSV INITIALIZATION
    # ========================================================

    def _init_csv(self):

        if not os.path.exists(CSV_FILE):

            with open(
                    CSV_FILE,
                    mode="w",
                    newline="",
                    encoding="utf-8"
            ) as f:
                pass

    # ========================================================
    # ACTIVITY LOG
    # ========================================================

    def log(self, message):

        self.log_text.config(
            state="normal"
        )

        self.log_text.insert(
            "end",
            message + "\n"
        )

        self.log_text.see(
            "end"
        )

        self.log_text.config(
            state="disabled"
        )

    # ========================================================
    # READ CSV
    # ========================================================

    def parse_single_csv(self):

        courses = []
        records = []

        if not os.path.exists(CSV_FILE):
            return courses, records

        current_course = None

        with open(
                CSV_FILE,
                mode="r",
                encoding="utf-8"
        ) as f:

            reader = csv.reader(f)

            for row in reader:

                if not row or not any(row):
                    continue

                # Course row
                if len(row) == 4:

                    current_course = {
                        "teacher": row[0].strip(),
                        "code": row[1].strip().upper(),
                        "title": row[2].strip(),
                        "units": row[3].strip(),
                    }

                    courses.append(
                        current_course
                    )

                # Student row
                elif len(row) == 2 and current_course:

                    records.append({
                        "teacher": current_course["teacher"],
                        "code": current_course["code"],
                        "title": current_course["title"],
                        "units": current_course["units"],
                        "student": row[0].strip(),
                        "grade": row[1].strip(),
                    })

        return courses, records

    # ========================================================
    # WRITE CSV
    # ========================================================

    def write_single_csv(
            self,
            courses,
            records
    ):

        with open(
                CSV_FILE,
                mode="w",
                newline="",
                encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            for c in courses:

                writer.writerow([
                    c["teacher"],
                    c["code"],
                    c["title"],
                    c["units"]
                ])

                c_students = [
                    r
                    for r in records
                    if (
                            r["teacher"].lower()
                            == c["teacher"].lower()
                            and
                            r["code"].upper()
                            == c["code"].upper()
                    )
                ]

                for s in c_students:

                    writer.writerow([
                        s["student"],
                        s["grade"]
                    ])

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate_grade(
            self,
            g_str
    ):

        try:

            val = float(g_str)

            if val == 0.0 or (
                    1.0 <= val <= 5.0
            ):
                return True, val

            return (
                False,
                "Grade must be 0.00 (No Credit) or between 1.00 and 5.00!"
            )

        except ValueError:

            return (
                False,
                "Grade must be a numeric value!"
            )

    def validate_units(
            self,
            u_str
    ):

        try:

            val = float(u_str)

            if 0.5 <= val <= 6.0:
                return True, val

            return (
                False,
                "Course units must be between 0.5 and 6.0!"
            )

        except ValueError:

            return (
                False,
                "Units must be a valid number!"
            )

    # ========================================================
    # TEACHER DROPDOWN
    # ========================================================

    def update_teacher_dropdown(self):

        courses, _ = self.parse_single_csv()

        teachers = sorted(
            list({
                c["teacher"]
                for c in courses
            })
        )

        self.all_teachers_list = [
                                     "All Teachers"
                                 ] + teachers

        self.teacher_dropdown["values"] = (
            self.all_teachers_list
        )

        if (
                self.selected_teacher.get()
                not in self.all_teachers_list
        ):

            self.selected_teacher.set(
                "All Teachers"
            )

    # ========================================================
    # TEACHER SEARCH
    # ========================================================

    def filter_teacher_search(self):

        typed_text = (
            self.teacher_dropdown
            .get()
            .lower()
        )

        if not typed_text:

            self.teacher_dropdown["values"] = (
                self.all_teachers_list
            )

        else:

            filtered = [
                t
                for t in self.all_teachers_list
                if typed_text in t.lower()
            ]

            self.teacher_dropdown["values"] = filtered

        self.load_data_from_csv()

    # ========================================================
    # LOAD DATA
    # ========================================================

    def load_data_from_csv(self):

        for item in self.tree.get_children():

            self.tree.delete(item)

        filter_teacher = (
            self.selected_teacher
            .get()
            .strip()
            .lower()
        )

        _, records = self.parse_single_csv()

        count = 0

        for r in records:

            if (
                    filter_teacher == "all teachers"
                    or filter_teacher == ""
                    or filter_teacher
                    in r["teacher"].lower()
            ):

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        r["student"],
                        r["code"],
                        r["title"],
                        r["units"],
                        r["grade"],
                        r["teacher"],
                    ),
                )

                count += 1

        self.recalculate_metrics()

        self.log(
            f"TEACHER PANEL -> Loaded {count} enrolled student record(s)."
        )

    # ========================================================
    # CALCULATE METRICS
    # ========================================================

    def recalculate_metrics(self):

        unique_students = set()

        total_points = 0.0
        total_count = 0

        for child in self.tree.get_children():

            v = self.tree.item(
                child,
                "values"
            )

            try:

                student = v[0]
                g = float(v[4])

                unique_students.add(
                    student
                )

                if g > 0.0:

                    total_points += g
                    total_count += 1

            except ValueError:

                continue

        avg_grade = (
            total_points / total_count
            if total_count > 0
            else 0.0
        )

        self.lbl_total_students.config(
            text=str(
                len(unique_students)
            )
        )

        self.lbl_gwa.config(
            text=f"{avg_grade:.2f}"
        )

    # ========================================================
    # TABLE FILTER
    # ========================================================

    def filter_table(self):

        q = (
            self.search_var
            .get()
            .lower()
        )

        self.load_data_from_csv()

        if q:

            for item in self.tree.get_children():

                val = self.tree.item(
                    item,
                    "values"
                )

                if not any(
                        q in str(x).lower()
                        for x in val
                ):

                    self.tree.delete(item)

    # ========================================================
    # VIEW ALL TEACHERS
    # ========================================================

    def open_view_teachers_dialog(self):

        dialog = tk.Toplevel(self)

        dialog.title(
            "Master List — Teachers & Handled Courses"
        )

        dialog.geometry(
            "520x300"
        )

        dialog.configure(
            bg=self.COLOR_WHITE
        )

        dialog.grab_set()

        cols = (
            "teacher",
            "code",
            "title",
            "units"
        )

        tree = ttk.Treeview(
            dialog,
            columns=cols,
            show="headings",
            style="Clean.Treeview"
        )

        tree.heading(
            "teacher",
            text="Teacher Name",
            anchor="w"
        )

        tree.heading(
            "code",
            text="Course Code",
            anchor="w"
        )

        tree.heading(
            "title",
            text="Course Title",
            anchor="w"
        )

        tree.heading(
            "units",
            text="Units",
            anchor="center"
        )

        tree.column(
            "teacher",
            width=140,
            anchor="w"
        )

        tree.column(
            "code",
            width=80,
            anchor="w"
        )

        tree.column(
            "title",
            width=200,
            anchor="w"
        )

        tree.column(
            "units",
            width=60,
            anchor="center"
        )

        sb = ttk.Scrollbar(
            dialog,
            orient="vertical",
            command=tree.yview
        )

        tree.configure(
            yscroll=sb.set
        )

        tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0),
            pady=10
        )

        sb.pack(
            side="right",
            fill="y",
            padx=(0, 10),
            pady=10
        )

        courses, _ = self.parse_single_csv()

        for c in courses:

            tree.insert(
                "",
                "end",
                values=(
                    c["teacher"],
                    c["code"],
                    c["title"],
                    c["units"]
                )
            )

    # ========================================================
    # VIEW ALL STUDENTS
    # ========================================================

    def open_view_students_dialog(self):

        dialog = tk.Toplevel(self)

        dialog.title(
            "Master List — Registered Students"
        )

        dialog.geometry(
            "450x300"
        )

        dialog.configure(
            bg=self.COLOR_WHITE
        )

        dialog.grab_set()

        cols = (
            "student",
            "courses",
            "gwa"
        )

        tree = ttk.Treeview(
            dialog,
            columns=cols,
            show="headings",
            style="Clean.Treeview"
        )

        tree.heading(
            "student",
            text="Student Name",
            anchor="w"
        )

        tree.heading(
            "courses",
            text="Enrolled Courses",
            anchor="center"
        )

        tree.heading(
            "gwa",
            text="Overall GWA",
            anchor="center"
        )

        tree.column(
            "student",
            width=200,
            anchor="w"
        )

        tree.column(
            "courses",
            width=110,
            anchor="center"
        )

        tree.column(
            "gwa",
            width=100,
            anchor="center"
        )

        sb = ttk.Scrollbar(
            dialog,
            orient="vertical",
            command=tree.yview
        )

        tree.configure(
            yscroll=sb.set
        )

        tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0),
            pady=10
        )

        sb.pack(
            side="right",
            fill="y",
            padx=(0, 10),
            pady=10
        )

        _, records = self.parse_single_csv()

        students_summary = {}

        for r in records:

            s = r["student"]
            u = float(r["units"])
            g = float(r["grade"])

            if s not in students_summary:

                students_summary[s] = {
                    "pts": 0.0,
                    "units": 0.0,
                    "count": 0
                }

            students_summary[s]["count"] += 1

            if g > 0.0:

                students_summary[s]["pts"] += (
                        u * g
                )

                students_summary[s]["units"] += u

        for student, data in sorted(
                students_summary.items()
        ):

            gwa = (
                data["pts"]
                / data["units"]
                if data["units"] > 0
                else 0.0
            )

            tree.insert(
                "",
                "end",
                values=(
                    student,
                    data["count"],
                    f"{gwa:.2f}"
                    if gwa > 0
                    else "N/A"
                )
            )

    # ========================================================
    # ANALYTICAL QUERIES
    # ========================================================

    def run_query(
            self,
            query_type
    ):

        for item in self.tree.get_children():

            self.tree.delete(item)

        _, records = self.parse_single_csv()

        student_gwas = {}

        for r in records:

            s = r["student"]
            u_val = float(r["units"])
            g_val = float(r["grade"])

            if g_val > 0.0:

                if s not in student_gwas:

                    student_gwas[s] = {
                        "pts": 0.0,
                        "units": 0.0
                    }

                student_gwas[s]["pts"] += (
                        u_val * g_val
                )

                student_gwas[s]["units"] += u_val

        gwa_scores = {
            s: (
                    d["pts"]
                    / d["units"]
            )
            for s, d in student_gwas.items()
            if d["units"] > 0
        }

        # ----------------------------------------------------
        # TOP STUDENT
        # ----------------------------------------------------

        if query_type == "top":

            if not gwa_scores:

                self.log(
                    "QUERY -> No records available to evaluate."
                )

                return

            best_student = min(
                gwa_scores,
                key=gwa_scores.get
            )

            for r in records:

                if r["student"] == best_student:

                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            r["student"],
                            r["code"],
                            r["title"],
                            r["units"],
                            r["grade"],
                            r["teacher"]
                        )
                    )

            self.log(
                f"QUERY TOP STUDENT -> '{best_student}' "
                f"with GWA: {gwa_scores[best_student]:.2f}"
            )

        # ----------------------------------------------------
        # FAILURES
        # ----------------------------------------------------

        elif query_type == "failure":

            count = 0

            for r in records:

                if (
                        float(r["grade"]) >= 3.0
                        or float(r["grade"]) == 0.0
                ):

                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            r["student"],
                            r["code"],
                            r["title"],
                            r["units"],
                            r["grade"],
                            r["teacher"]
                        )
                    )

                    count += 1

            self.log(
                f"QUERY FAILURES -> "
                f"Displaying {count} failing record(s)."
            )

        # ----------------------------------------------------
        # AT-RISK
        # ----------------------------------------------------

        elif query_type == "risk":

            count = 0

            for s, gwa in gwa_scores.items():

                if 2.50 <= gwa < 3.00:

                    for r in records:

                        if r["student"] == s:

                            self.tree.insert(
                                "",
                                "end",
                                values=(
                                    r["student"],
                                    r["code"],
                                    r["title"],
                                    r["units"],
                                    r["grade"],
                                    r["teacher"]
                                )
                            )

                            count += 1

            self.log(
                f"QUERY AT-RISK -> "
                f"Found {count} record(s) with "
                f"GWAs between 2.50 and 2.99."
            )

        self.recalculate_metrics()

    # ========================================================
    # ADD TEACHER / COURSE
    # ========================================================

    def open_add_teacher_dialog(self):

        dialog = tk.Toplevel(self)

        dialog.title(
            "Add Teacher & Assigned Course"
        )

        dialog.geometry(
            "360x350"
        )

        dialog.configure(
            bg=self.COLOR_WHITE
        )

        dialog.grab_set()

        # ----------------------------------------------------
        # TEACHER NAME
        # ----------------------------------------------------

        tk.Label(
            dialog,
            text="Teacher Name:",
            font=("Georgia", 9, "bold"),
            fg=self.COLOR_BROWN_DARK,
            bg=self.COLOR_WHITE,
        ).pack(
            anchor="w",
            padx=20,
            pady=(12, 1)
        )

        t_e = tk.Entry(
            dialog,
            font=("Georgia", 10),
            bg=self.COLOR_WHITE_WARM
        )

        t_e.pack(
            fill="x",
            padx=20
        )

        # ----------------------------------------------------
        # COURSE CODE
        # ----------------------------------------------------

        tk.Label(
            dialog,
            text="Course Code:",
            font=("Georgia", 9, "bold"),
            fg=self.COLOR_BROWN_DARK,
            bg=self.COLOR_WHITE,
        ).pack(
            anchor="w",
            padx=20,
            pady=(6, 1)
        )

        c_e = tk.Entry(
            dialog,
            font=("Georgia", 10),
            bg=self.COLOR_WHITE_WARM
        )

        c_e.pack(
            fill="x",
            padx=20
        )

        # ----------------------------------------------------
        # COURSE TITLE
        # ----------------------------------------------------

        tk.Label(
            dialog,
            text="Course Title:",
            font=("Georgia", 9, "bold"),
            fg=self.COLOR_BROWN_DARK,
            bg=self.COLOR_WHITE,
        ).pack(
            anchor="w",
            padx=20,
            pady=(6, 1)
        )

        title_e = tk.Entry(
            dialog,
            font=("Georgia", 10),
            bg=self.COLOR_WHITE_WARM
        )

        title_e.pack(
            fill="x",
            padx=20
        )

        # ----------------------------------------------------
        # UNITS
        # ----------------------------------------------------

        tk.Label(
            dialog,
            text="Units (0.5 - 6.0):",
            font=("Georgia", 9, "bold"),
            fg=self.COLOR_BROWN_DARK,
            bg=self.COLOR_WHITE,
        ).pack(
            anchor="w",
            padx=20,
            pady=(6, 1)
        )

        u_e = tk.Entry(
            dialog,
            font=("Georgia", 10),
            bg=self.COLOR_WHITE_WARM
        )

        u_e.pack(
            fill="x",
            padx=20
        )

        # ----------------------------------------------------
        # SAVE FUNCTION
        # ----------------------------------------------------

        def save():

            t = t_e.get().strip()
            c = c_e.get().strip().upper()
            title = title_e.get().strip()
            u = u_e.get().strip()

            # Required fields
            if not (
                    t
                    and c
                    and title
                    and u
            ):

                messagebox.showerror(
                    "Error",
                    "All fields are required!",
                    parent=dialog
                )

                return

            # Validate units
            valid_unit, u_val = (
                self.validate_units(u)
            )

            if not valid_unit:

                messagebox.showerror(
                    "Unit Error",
                    u_val,
                    parent=dialog
                )

                return

            courses, records = (
                self.parse_single_csv()
            )

            # Check duplicate
            for course in courses:

                if (
                        course["teacher"].lower()
                        == t.lower()
                        and
                        course["code"].upper()
                        == c
                ):

                    messagebox.showerror(
                        "Duplicate Course",
                        f"Teacher '{t}' already handles "
                        f"course '{c}'!",
                        parent=dialog
                    )

                    return

            # Add course
            courses.append({
                "teacher": t,
                "code": c,
                "title": title,
                "units": f"{u_val:.1f}",
            })

            # Save
            self.write_single_csv(
                courses,
                records
            )

            # Activity log
            self.log(
                f"ADDED TEACHER COURSE -> "
                f"'{t}' assigned to '{c}' "
                f"({title}, {u_val:.1f} Units)."
            )

            # Refresh GUI
            self.update_teacher_dropdown()
            self.load_data_from_csv()

            # ------------------------------------------------
            # SUCCESS CONFIRMATION
            # ------------------------------------------------

            messagebox.showinfo(
                "Teacher Successfully Added",
                "Teacher and course were successfully added!\n\n"
                "--------------------------------\n"
                f"Teacher Name: {t}\n"
                f"Course Code: {c}\n"
                f"Course Title: {title}\n"
                f"Units: {u_val:.1f}\n"
                "--------------------------------\n\n"
                "The information has been saved successfully.",
                parent=dialog
            )

            dialog.destroy()

        # ----------------------------------------------------
        # SAVE BUTTON
        # ----------------------------------------------------

        self._create_btn(
            dialog,
            "Save Teacher & Course",
            self.COLOR_RED_PRIMARY,
            command=save
        ).pack(
            pady=15
        )

    # ========================================================
    # ENROLL STUDENT
    # ========================================================

    def open_add_student_to_course_dialog(self):

        courses, records = (
            self.parse_single_csv()
        )

        if not courses:

            messagebox.showerror(
                "Assignment Error",
                "No courses registered yet. "
                "Please add a teacher/course first."
            )

            return

        dialog = tk.Toplevel(self)

        dialog.title(
            "Enroll Student to Teacher's Class"
        )

        dialog.geometry(
            "380x380"
        )

        dialog.configure(
            bg=self.COLOR_WHITE
        )

        dialog.grab_set()

        # ----------------------------------------------------
        # STUDENT NAME
        # ----------------------------------------------------

        tk.Label(
            dialog,
            text="Student Name:",
            font=("Georgia", 9, "bold"),
            fg=self.COLOR_BROWN_DARK,
            bg=self.COLOR_WHITE,
        ).pack(
            anchor="w",
            padx=20,
            pady=(12, 1)
        )

        student_e = tk.Entry(
            dialog,
            font=("Georgia", 10),
            bg=self.COLOR_WHITE_WARM
        )

        student_e.pack(
            fill="x",
            padx=20
        )

        # ----------------------------------------------------
        # COURSE SELECTION
        # ----------------------------------------------------

        tk.Label(
            dialog,
            text="Select Teacher & Course:",
            font=("Georgia", 9, "bold"),
            fg=self.COLOR_BROWN_DARK,
            bg=self.COLOR_WHITE,
        ).pack(
            anchor="w",
            padx=20,
            pady=(8, 1)
        )

        course_options = [
            f"{c['teacher']} | "
            f"{c['code']} - "
            f"{c['title']}"
            for c in courses
        ]

        course_cb = ttk.Combobox(
            dialog,
            values=course_options,
            state="readonly"
        )

        course_cb.pack(
            fill="x",
            padx=20
        )

        course_cb.current(0)

        # ----------------------------------------------------
        # GRADE
        # ----------------------------------------------------

        tk.Label(
            dialog,
            text="Grade (1.00 - 5.00 or 0.00):",
            font=("Georgia", 9, "bold"),
            fg=self.COLOR_BROWN_DARK,
            bg=self.COLOR_WHITE,
        ).pack(
            anchor="w",
            padx=20,
            pady=(8, 1)
        )

        grade_e = tk.Entry(
            dialog,
            font=("Georgia", 10),
            bg=self.COLOR_WHITE_WARM
        )

        grade_e.pack(
            fill="x",
            padx=20
        )

        # ----------------------------------------------------
        # SAVE FUNCTION
        # ----------------------------------------------------

        def save():

            s = student_e.get().strip()
            g = grade_e.get().strip()
            idx = course_cb.current()

            # Required fields
            if (
                    not s
                    or not g
                    or idx < 0
            ):

                messagebox.showerror(
                    "Error",
                    "All fields are required!",
                    parent=dialog
                )

                return

            selected_course = courses[idx]

            # ------------------------------------------------
            # VALIDATE GRADE
            # ------------------------------------------------

            valid_grade, g_msg = (
                self.validate_grade(g)
            )

            if not valid_grade:

                messagebox.showerror(
                    "Grade Error",
                    g_msg,
                    parent=dialog
                )

                return

            # ------------------------------------------------
            # CHECK DUPLICATE
            # ------------------------------------------------

            for r in records:

                if (
                        r["student"].lower()
                        == s.lower()
                        and
                        r["teacher"].lower()
                        ==
                        selected_course["teacher"].lower()
                        and
                        r["code"].upper()
                        ==
                        selected_course["code"].upper()
                ):

                    messagebox.showerror(
                        "Duplicate Record",
                        f"Student '{s}' is already enrolled "
                        f"in '{selected_course['code']}' "
                        f"under '{selected_course['teacher']}'!",
                        parent=dialog
                    )

                    return

            # ------------------------------------------------
            # ADD STUDENT
            # ------------------------------------------------

            records.append({

                "teacher":
                    selected_course["teacher"],

                "code":
                    selected_course["code"],

                "title":
                    selected_course["title"],

                "units":
                    selected_course["units"],

                "student":
                    s,

                "grade":
                    f"{float(g):.2f}",
            })

            # ------------------------------------------------
            # SAVE DATA
            # ------------------------------------------------

            self.write_single_csv(
                courses,
                records
            )

            # ------------------------------------------------
            # ACTIVITY LOG
            # ------------------------------------------------

            self.log(
                f"ENROLLED STUDENT -> "
                f"'{s}' in "
                f"'{selected_course['code']}' "
                f"under "
                f"'{selected_course['teacher']}' "
                f"| Grade: {float(g):.2f}"
            )

            # Refresh table
            self.load_data_from_csv()

            # ------------------------------------------------
            # SUCCESS CONFIRMATION
            # ------------------------------------------------

            messagebox.showinfo(
                "Student Successfully Added",
                "Student was successfully enrolled!\n\n"
                "--------------------------------\n"
                f"Student Name: {s}\n"
                f"Teacher: {selected_course['teacher']}\n"
                f"Course Code: {selected_course['code']}\n"
                f"Course Title: {selected_course['title']}\n"
                f"Units: {selected_course['units']}\n"
                f"Grade: {float(g):.2f}\n"
                "--------------------------------\n\n"
                "The student information has been saved successfully.",
                parent=dialog
            )

            dialog.destroy()

        # ----------------------------------------------------
        # ENROLL BUTTON
        # ----------------------------------------------------

        self._create_btn(
            dialog,
            "Enroll Student",
            self.COLOR_RED_PRIMARY,
            command=save
        ).pack(
            pady=20
        )

    # ========================================================
    # UPDATE STUDENT GRADE
    # ========================================================

    def open_update_dialog(self):

        sel = self.tree.selection()

        if not sel:

            messagebox.showwarning(
                "Warning",
                "Select a student record to update."
            )

            return

        old_vals = list(
            self.tree.item(
                sel[0],
                "values"
            )
        )

        dialog = tk.Toplevel(self)

        dialog.title(
            "Update Student Grade"
        )

        dialog.geometry(
            "340x220"
        )

        dialog.configure(
            bg=self.COLOR_WHITE
        )

        dialog.grab_set()

        tk.Label(
            dialog,
            text=(
                f"Student: {old_vals[0]} "
                f"({old_vals[1]})\n"
                f"Teacher: {old_vals[5]}"
            ),
            font=("Georgia", 8, "bold"),
            fg=self.COLOR_RED_PRIMARY,
            bg=self.COLOR_WHITE,
            justify="left",
        ).pack(
            pady=(12, 8),
            anchor="w",
            padx=20
        )

        tk.Label(
            dialog,
            text="Grade (1.00-5.00 or 0.00):",
            font=("Georgia", 8, "bold"),
            fg=self.COLOR_TEXT_DARK,
            bg=self.COLOR_WHITE,
        ).pack(
            anchor="w",
            padx=20
        )

        g_e = tk.Entry(
            dialog,
            font=("Georgia", 9),
            bg=self.COLOR_WHITE_WARM
        )

        g_e.pack(
            fill="x",
            padx=20,
            pady=(0, 5)
        )

        g_e.insert(
            0,
            old_vals[4]
        )

        def update():

            valid_g, g_msg = (
                self.validate_grade(
                    g_e.get().strip()
                )
            )

            if not valid_g:

                messagebox.showerror(
                    "Grade Error",
                    g_msg,
                    parent=dialog
                )

                return

            courses, records = (
                self.parse_single_csv()
            )

            for r in records:

                if (
                        r["student"].lower()
                        == old_vals[0].lower()
                        and
                        r["code"].upper()
                        == old_vals[1].upper()
                        and
                        r["teacher"].lower()
                        == old_vals[5].lower()
                ):

                    r["grade"] = (
                        f"{float(g_e.get()):.2f}"
                    )

                    break

            self.write_single_csv(
                courses,
                records
            )

            self.log(
                f"UPDATED GRADE -> "
                f"'{old_vals[0]}' "
                f"({old_vals[1]}) "
                f"Grade updated to "
                f"{float(g_e.get()):.2f}"
            )

            self.load_data_from_csv()

            dialog.destroy()

        self._create_btn(
            dialog,
            "Confirm Update",
            self.COLOR_RED_PRIMARY,
            command=update
        ).pack(
            pady=15
        )

    # ========================================================
    # DELETE RECORD
    # ========================================================

    def delete_selected_row(self):

        sel = self.tree.selection()

        if not sel:

            messagebox.showwarning(
                "Select Item",
                "Please select a row to delete."
            )

            return

        item_vals = list(
            self.tree.item(
                sel[0],
                "values"
            )
        )

        courses, records = (
            self.parse_single_csv()
        )

        updated_records = [
            r
            for r in records
            if not (
                    r["student"].lower()
                    == item_vals[0].lower()
                    and
                    r["code"].upper()
                    == item_vals[1].upper()
                    and
                    r["teacher"].lower()
                    == item_vals[5].lower()
            )
        ]

        self.write_single_csv(
            courses,
            updated_records
        )

        self.log(
            f"DELETED RECORD -> "
            f"Student '{item_vals[0]}' "
            f"from course '{item_vals[1]}' "
            f"({item_vals[5]})"
        )

        self.load_data_from_csv()


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    app = CleanRedWoodyConsole()

    app.mainloop()