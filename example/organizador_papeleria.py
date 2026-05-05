import os
import shutil
import hashlib
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

class OrganizadorPapeleria:
    def __init__(self, root):
        self.root = root
        self.root.title("Create Tech Solutions - Organizador de Papelería Pro")
        self.root.geometry("850x700")
        
        # Extensiones por categoría
        self.categorias = {
            "Documentos": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".doc"],
            "Imágenes": [".jpg", ".jpeg", ".png", ".webp", ".bmp"],
            "Comprimidos": [".zip", ".rar", ".7z"],
            "Otros": []
        }
        
        self.archivos_encontrados = []
        self.vars_check = {}
        self.setup_ui()

    def setup_ui(self):
        # --- PANEL SUPERIOR: SELECCIÓN ---
        frame_top = ttk.LabelFrame(self.root, text=" 1. Configuración de Escaneo ", padding=15)
        frame_top.pack(fill="x", padx=20, pady=10)

        # Ruta Origen
        ttk.Label(frame_top, text="Carpeta a limpiar (Origen):").grid(row=0, column=0, sticky="w")
        self.entry_origen = ttk.Entry(frame_top, width=50)
        self.entry_origen.grid(row=0, column=1, padx=5)
        ttk.Button(frame_top, text="Buscar", command=lambda: self.sel_dir(self.entry_origen)).grid(row=0, column=2)

        # Ruta Destino
        ttk.Label(frame_top, text="Carpeta de guardado (Destino):").grid(row=1, column=0, sticky="w", pady=10)
        self.entry_destino = ttk.Entry(frame_top, width=50)
        self.entry_destino.insert(0, str(Path.home() / "Documents")) # Por defecto Documentos de Windows
        self.entry_destino.grid(row=1, column=1, padx=5)
        ttk.Button(frame_top, text="Buscar", command=lambda: self.sel_dir(self.entry_destino)).grid(row=1, column=2)

        # Checkboxes de Tipos
        frame_types = ttk.Frame(frame_top)
        frame_types.grid(row=2, column=0, columnspan=3, pady=10)
        for cat in self.categorias.keys():
            var = tk.BooleanVar(value=True)
            self.vars_check[cat] = var
            ttk.Checkbutton(frame_types, text=cat, variable=var).pack(side="left", padx=15)

        # --- BOTÓN ESCANEAR ---
        self.btn_escanear = ttk.Button(self.root, text="🔍 ESCANEAR ARCHIVOS", command=self.iniciar_escaneo)
        self.btn_escanear.pack(pady=5)

        # --- TABLA DE PREVISUALIZACIÓN ---
        self.tree = ttk.Treeview(self.root, columns=("Nombre", "Tamaño", "Estado"), show="headings")
        self.tree.heading("Nombre", text="Nombre del Archivo")
        self.tree.heading("Tamaño", text="Tamaño")
        self.tree.heading("Estado", text="Detección de Duplicado")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # --- PANEL INFERIOR: ACCIONES ---
        frame_bot = ttk.Frame(self.root, padding=10)
        frame_bot.pack(fill="x", padx=20)

        self.check_renombrar = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame_bot, text="Renombrar automáticamente (Archivo_1, Archivo_2...)", 
                        variable=self.check_renombrar).pack(side="left")

        self.btn_organizar = ttk.Button(frame_bot, text="🚀 ORGANIZAR TODO", state="disabled", command=self.ejecutar_organizacion)
        self.btn_organizar.pack(side="right")

    def sel_dir(self, entry):
        dir = filedialog.askdirectory()
        if dir:
            entry.delete(0, tk.END)
            entry.insert(0, dir)

    def calcular_hash(self, ruta):
        """Genera un hash MD5 para comparar contenido, no nombres."""
        hash_md5 = hashlib.md5()
        with open(ruta, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def iniciar_escaneo(self):
        origen = self.entry_origen.get()
        if not os.path.exists(origen):
            messagebox.showerror("Error", "La ruta de origen no existe.")
            return

        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.archivos_encontrados = []

        # Extensiones permitidas según checks
        exts_permitidas = []
        for cat, var in self.vars_check.items():
            if var.get(): exts_permitidas.extend(self.categorias[cat])

        hashes_vistos = {}
        
        for root, dirs, files in os.walk(origen):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in exts_permitidas or self.vars_check["Otros"].get():
                    ruta_completa = os.path.join(root, f)
                    h = self.calcular_hash(ruta_completa)
                    
                    duplicado = "Original"
                    if h in hashes_vistos:
                        duplicado = f"DUPLICADO de {hashes_vistos[h]}"
                    else:
                        hashes_vistos[h] = f

                    size = f"{os.path.getsize(ruta_completa) // 1024} KB"
                    self.tree.insert("", "end", values=(f, size, duplicado))
                    self.archivos_encontrados.append({
                        "ruta": ruta_completa,
                        "nombre": f,
                        "ext": ext,
                        "duplicado": duplicado != "Original"
                    })

        self.btn_organizar.config(state="normal")
        messagebox.showinfo("Escaneo", f"Se encontraron {len(self.archivos_encontrados)} archivos.")

    def ejecutar_organizacion(self):
        destino_base = self.entry_destino.get()
        renombrar = self.check_renombrar.get()
        
        count = 0
        for i, info in enumerate(self.archivos_encontrados):
            if info["duplicado"]: continue # Saltar duplicados

            # Determinar carpeta por tipo
            for cat, exts in self.categorias.items():
                if info["ext"] in exts:
                    folder_dest = os.path.join(destino_base, cat)
                    break
            else:
                folder_dest = os.path.join(destino_base, "Otros")

            os.makedirs(folder_dest, exist_ok=True)

            # Lógica de renombrado
            nuevo_nombre = info["nombre"]
            if renombrar:
                nuevo_nombre = f"Cliente_Archivo_{i+1}{info['ext']}"

            path_final = os.path.join(folder_dest, nuevo_nombre)
            
            # Mover
            try:
                shutil.move(info["ruta"], path_final)
                count += 1
            except Exception as e:
                print(f"Error: {e}")

        messagebox.showinfo("Éxito", f"Se organizaron {count} archivos. Los duplicados fueron omitidos.")
        self.btn_organizar.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = OrganizadorPapeleria(root)
    root.mainloop()