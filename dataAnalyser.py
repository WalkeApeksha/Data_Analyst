# ======================================
# FINAL DATA ANALYZER - FULL VERSION
# Animated UI + Professional Charts
# ======================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class DataAnalyzerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Data Analyzer")
        self.root.geometry("1300x780")
        self.root.configure(bg="#eef2f7")

        self.file_path = None
        self.df = None
        self.report_df = None
        self.figure = None
        self.canvas = None

        self.create_ui()

    # ================= Animated Button =================
    def create_animated_button(self, parent, text, command, bg="#3498db"):

        btn = tk.Label(
            parent,
            text=text,
            bg=bg,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=7,
            cursor="hand2"
        )

        def on_enter(e):
            btn.config(bg="#2980b9")

        def on_leave(e):
            btn.config(bg=bg)

        def on_click(e):
            btn.config(bg="#1c5d85")
            btn.after(100, lambda: btn.config(bg="#2980b9"))
            command()

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_click)

        return btn

    # ================= UI =================
    def create_ui(self):

        header = tk.Label(
            self.root,
            text="DATA ANALYZER",
            font=("Segoe UI", 30, "bold"),
            bg="#eef2f7",
            fg="#2c3e50"
        )
        header.pack(pady=15)

        file_frame = tk.Frame(self.root, bg="#eef2f7")
        file_frame.pack(fill="x", padx=20, pady=5)

        self.create_animated_button(file_frame, "Browse File", self.browse_file).pack(side="left", padx=5)
        self.create_animated_button(file_frame, "Read File", self.read_file, "#27ae60").pack(side="left", padx=5)

        self.file_label = tk.Label(file_frame, text="No file selected", bg="#eef2f7")
        self.file_label.pack(side="left", padx=10)

        self.info_text = tk.Text(self.root, height=3)
        self.info_text.pack(fill="x", padx=20, pady=5)

        control_frame = tk.Frame(self.root, bg="#eef2f7")
        control_frame.pack(fill="x", padx=20, pady=5)

        self.group_combo = ttk.Combobox(control_frame, width=20, state="readonly")
        self.group_combo.pack(side="left", padx=5)

        self.agg_combo = ttk.Combobox(
            control_frame,
            values=["sum", "mean", "average", "max", "min", "count", "median"],
            width=15,
            state="readonly"
        )
        self.agg_combo.pack(side="left", padx=5)

        self.value_combo = ttk.Combobox(control_frame, width=20, state="readonly")
        self.value_combo.pack(side="left", padx=5)

        self.create_animated_button(control_frame, "Preview Report", self.generate_report, "#8e44ad").pack(side="left", padx=5)

        chart_ctrl = tk.Frame(self.root, bg="#eef2f7")
        chart_ctrl.pack(fill="x", padx=20, pady=5)

        self.chart_combo = ttk.Combobox(
            chart_ctrl,
            values=["Bar Chart", "Column Chart", "Line Chart", "Pie Chart"],
            width=20,
            state="readonly"
        )
        self.chart_combo.pack(side="left", padx=5)

        self.create_animated_button(chart_ctrl, "Preview Chart", self.preview_chart, "#e67e22").pack(side="left", padx=5)
        self.create_animated_button(chart_ctrl, "Export Chart", self.export_chart, "#c0392b").pack(side="left", padx=5)

        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.tree = ttk.Treeview(table_frame)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.chart_area = tk.Frame(self.root, bg="white")
        self.chart_area.pack(fill="both", expand=True, padx=20, pady=10)

    # ================= File =================
    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Data Files", "*.csv *.xlsx *.xls")])
        if file:
            self.file_path = file
            self.file_label.config(text=os.path.basename(file))

    def read_file(self):

        if not self.file_path:
            messagebox.showerror("Error", "Select file first")
            return

        if self.file_path.endswith(".csv"):
            self.df = pd.read_csv(self.file_path)
        else:
            self.df = pd.read_excel(self.file_path)

        self.detect_columns()
        self.show_info()

    # ================= Detect =================
    def detect_columns(self):

        text_cols = []
        num_cols = []

        for col in self.df.columns:
            if self.df[col].dtype == "object":
                conv = pd.to_numeric(self.df[col], errors="coerce")
                if conv.notna().sum() > len(self.df) * 0.7:
                    num_cols.append(col)
                else:
                    text_cols.append(col)
            else:
                num_cols.append(col)

        self.group_combo["values"] = text_cols
        self.value_combo["values"] = num_cols

    def show_info(self):
        self.info_text.delete("1.0", tk.END)
        r, c = self.df.shape
        self.info_text.insert(tk.END, f"Rows: {r} | Columns: {c}")

    # ================= Report =================
    def generate_report(self):

        group = self.group_combo.get()
        agg = self.agg_combo.get()
        value = self.value_combo.get()

        if not group or not agg or not value:
            messagebox.showerror("Error", "Select all dropdowns")
            return

        if agg == "average":
            agg = "mean"

        self.report_df = (
            self.df.groupby(group)[value]
            .agg(agg)
            .sort_values(ascending=False)
            .reset_index()
        )

        self.show_table()

    def show_table(self):

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(self.report_df.columns)
        self.tree["show"] = "headings"

        for col in self.report_df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)

        for _, row in self.report_df.iterrows():
            self.tree.insert("", "end", values=list(row))

    # ================= ⭐ PROFESSIONAL CHART FUNCTION =================
    def preview_chart(self):

        if self.report_df is None:
            messagebox.showerror("Error", "Generate report first")
            return

        for widget in self.chart_area.winfo_children():
            widget.destroy()

        data = self.report_df.copy()

        # Limit rows for readability
        if len(data) > 30:
            data = data.head(30)

        x = data.iloc[:, 0].astype(str)
        y = data.iloc[:, 1]

        self.figure = plt.Figure(figsize=(12, 6), dpi=100)
        ax = self.figure.add_subplot(111)

        chart_type = self.chart_combo.get()

        if chart_type in ["Bar Chart", "Column Chart"]:
            ax.bar(x, y, width=0.6)

        elif chart_type == "Line Chart":
            ax.plot(x, y, marker="o", linewidth=2)

        elif chart_type == "Pie Chart":
            ax.pie(y, labels=x, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")

        if chart_type != "Pie Chart":
            total = len(x)

            if total > 20:
                step = max(1, total // 15)
                labels = [label if i % step == 0 else "" for i, label in enumerate(x)]
                ax.set_xticks(range(len(x)))
                ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
            else:
                ax.set_xticks(range(len(x)))
                ax.set_xticklabels(x, rotation=45, ha="right", fontsize=10)

        ax.set_title(chart_type, fontsize=16, pad=15)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        self.figure.subplots_adjust(left=0.08, right=0.97, top=0.90, bottom=0.28)

        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_area)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ================= Export Chart =================
    def export_chart(self):

        if self.figure is None:
            messagebox.showerror("Error", "Preview chart first")
            return

        folder = os.path.dirname(self.file_path)
        self.figure.savefig(os.path.join(folder, "chart.png"))
        messagebox.showinfo("Saved", "Chart Exported")


# ================= RUN =================
if __name__ == "__main__":
    root = tk.Tk()
    app = DataAnalyzerApp(root)
    root.mainloop()





    