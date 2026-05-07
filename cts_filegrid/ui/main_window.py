import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.organizer_logic import FileEngine

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.engine = FileEngine()
        self.setup_ui()

    def setup_ui(self):
        self.root.title("CTS FileGrid - Create Tech Solutions")
        self.root.geometry("800x600")

        # --- SELECCIÓN DE RUTAS ---
        frame_paths = ttk.LabelFrame(self.root, text=" 1. Directorios ", padding=10)
        frame_paths.pack(fill="x", padx=10, pady=5)

        self.path_src = tk.StringVar()
        ttk.Entry(frame_paths, textvariable=self.path_src, width=60).grid(row=0, column=0)
        ttk.Button(frame_paths, text="Origen", command=self.sel_src).grid(row=0, column=1)

        # --- CHECKBOXES ---
        frame_cats = ttk.LabelFrame(self.root, text=" 2. Categorías ", padding=10)
        frame_cats.pack(fill="x", padx=10, pady=5)
        
        self.cat_vars = {}
        for cat in self.engine.categories.keys():
            var = tk.BooleanVar(value=True)
            self.cat_vars[cat] = var
            ttk.Checkbutton(frame_cats, text=cat, variable=var).pack(side="left", padx=10)

        # --- TABLA Y BOTONES ---
        self.tree = ttk.Treeview(self.root, columns=("File", "Status"), show="headings")
        self.tree.heading("File", text="Archivo")
        self.tree.heading("Status", text="Estado")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Button(self.root, text="🔍 ESCANEAR", command=self.run_scan).pack(pady=5)
        self.btn_move = ttk.Button(self.root, text="🚀 ORGANIZAR", state="disabled", command=self.run_move)
        self.btn_move.pack(pady=5)

    def sel_src(self):
        d = filedialog.askdirectory()
        if d: self.path_src.set(d)

    def run_scan(self):
        # Lógica de escaneo conectada al Engine
        active = [c for c, v in self.cat_vars.items() if v.get()]
        self.found_files = self.engine.scan_directory(self.path_src.get(), active)
        
        for i in self.tree.get_children(): self.tree.delete(i)
        for f in self.found_files:
            status = "Duplicado (Se omitirá)" if f['duplicate'] else "Original"
            self.tree.insert("", "end", values=(f['name'], status))
        
        self.btn_move.config(state="normal")

    def run_move(self):
        # Aquí iría la lógica de shutil.move basada en los resultados del scan
        messagebox.showinfo("CTS", "Proceso completado con éxito.")