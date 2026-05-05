import hashlib
import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk


class OrganizadorUltra:
    def __init__(self, root):
        self.root = root
        self.root.title("Create Tech Solutions - File Master ULTRA")
        self.root.geometry("800x700")
        self.root.configure(padx=20, pady=20)
        
        # Configuración de estilos
        self.style = ttk.Style()
        self.style.configure("Bold.TLabel", font=('Segoe UI', 10, 'bold'))
        self.style.configure("Accent.TButton", font=('Segoe UI', 10, 'bold'), foreground="white", background="#0078D7")

        # Categorías por defecto
        self.categorias = {
            "Video": [".mkv", ".mp4", ".avi", ".mov", ".flv", ".wmv"],
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
            "Documentos": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv", ".epub"],
            "Imágenes": [".jpg", ".png", ".gif", ".webp", ".svg", ".bmp"],
            "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Ejecutables": [".exe", ".msi", ".bat", ".sh"]
        }

        self.setup_ui()

    def setup_ui(self):
        # --- ENCABEZADO ---
        ttk.Label(self.root, text="Create Tech Solutions", font=('Segoe UI', 16, 'bold'), foreground="#0078D7").pack()
        ttk.Label(self.root, text="File Master ULTRA - Organizador Inteligente", font=('Segoe UI', 10, 'italic')).pack(pady=(0, 15))

        # --- SECCIÓN RUTA ---
        frame_ruta = ttk.LabelFrame(self.root, text=" Paso 1: Selecciona el Directorio ", padding=10)
        frame_ruta.pack(fill="x", pady=10)
        
        self.entry_ruta = ttk.Entry(frame_ruta, font=('Segoe UI', 9))
        self.entry_ruta.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(frame_ruta, text="Examinar...", command=self.seleccionar_carpeta).pack(side="right")

        # --- SECCIÓN CONFIGURACIÓN ---
        frame_config = ttk.LabelFrame(self.root, text=" Paso 2: Configura las Opciones ", padding=15)
        frame_config.pack(fill="x", pady=10)

        # Extensión y Categoría
        ttk.Label(frame_config, text="Extensiones a mover:", style="Bold.TLabel").grid(row=0, column=0, sticky="w", pady=5)
        
        # Frame para opciones de extensión
        frame_ext_opts = ttk.Frame(frame_config)
        frame_ext_opts.grid(row=0, column=1, sticky="w", padx=10)
        
        self.entry_ext = ttk.Entry(frame_ext_opts, width=20, font=('Consolas', 10))
        self.entry_ext.insert(0, ".mkv, .mp4")
        self.entry_ext.pack(side="left")
        ttk.Label(frame_ext_opts, text=" (ej: .mkv, .mp4 o * para todo)", foreground="gray").pack(side="left", padx=5)

        # Checks
        self.check_carpetas = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_config, text="Crear subcarpetas por tipo (Video, Audio, etc.)", variable=self.check_carpetas).grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 5))

        self.check_borrar = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame_config, text="ELIMINAR carpetas de origen (usar con precaución)", variable=self.check_borrar).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        self.check_simulacion = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_config, text="Modo SIMULACIÓN (no mueve ni borra nada, solo reporta)", variable=self.check_simulacion).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        self.check_pdf = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_config, text="Generar REPORTE PDF del proceso", variable=self.check_pdf).grid(row=4, column=0, columnspan=2, sticky="w", pady=5)

        # --- SECCIÓN PROGRESO Y BOTÓN ---
        frame_ops = ttk.Frame(self.root, padding=10)
        frame_ops.pack(fill="x")

        self.btn_ejecutar = ttk.Button(frame_ops, text="INICIAR PROCESO", command=self.confirmar_e_iniciar, style="Accent.TButton")
        self.btn_ejecutar.pack(fill="x", pady=(0, 10))

        self.progress = ttk.Progressbar(frame_ops, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x")
        self.label_progreso = ttk.Label(frame_ops, text="Esperando instrucciones...", foreground="gray")
        self.label_progreso.pack(pady=5)

        # --- SECCIÓN CONSOLA/LOG ---
        self.txt_log = tk.Text(self.root, height=12, state="disabled", font=('Consolas', 9), bg="#222", fg="#0f0", wrap="word")
        self.txt_log.pack(fill="both", expand=True)

    def seleccionar_carpeta(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_ruta.delete(0, tk.END)
            self.entry_ruta.insert(0, folder)

    def log(self, mensaje, tag=None):
        ahora = datetime.now().strftime("%H:%M:%S")
        formato = f"[{ahora}] {mensaje}\n"
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, formato)
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")
        self.root.update_idletasks()

    def obtener_categoria(self, ext):
        for cat, exts in self.categorias.items():
            if ext.lower() in exts: return cat
        return "Otros"

    def confirmar_e_iniciar(self):
        if self.check_simulacion.get():
            self.iniciar_hilo()
            return

        if self.check_borrar.get():
            resp = messagebox.askyesno("¡ATENCIÓN!", "Has activado la eliminación agresiva de carpetas.\n\nEsto borrará permanentemente las subcarpetas de origen aunque tengan otros archivos dentro.\n\n¿Estás completamente seguro de continuar?")
            if not resp: return
        
        self.iniciar_hilo()

    def iniciar_hilo(self):
        # Desactivar UI
        self.btn_ejecutar.config(state="disabled")
        self.progress['value'] = 0
        self.txt_log.config(state="normal")
        self.txt_log.delete('1.0', tk.END)
        self.txt_log.config(state="disabled")
        
        # Iniciar proceso en segundo plano
        thread = threading.Thread(target=self.procesar_logica)
        thread.start()

    def procesar_logica(self):
        ruta_base = self.entry_ruta.get()
        exts_raw = self.entry_ext.get()
        modo_sim = self.check_simulacion.get()
        
        if not os.path.exists(ruta_base):
            self.root.after(0, lambda: messagebox.showerror("Error", "Ruta base no válida"))
            self.root.after(0, lambda: self.btn_ejecutar.config(state="normal"))
            return

        # Procesar extensiones
        if exts_raw.strip() == "*":
            exts_buscadas = ["*"]
        else:
            exts_buscadas = [e.strip().lower() for e in exts_raw.split(',') if e.strip()]

        # Variables de reporte
        archivos_procesados = []
        carpetas_eliminadas = []
        errores = []
        carpetas_origen_potenciales = set()
        
        prefix = "[SIMULACIÓN] " if modo_sim else ""
        self.log(f"--- INICIANDO PROCESO {prefix}---")
        self.root.after(0, lambda: self.label_progreso.config(text="Escaneando archivos..."))

        # Paso 1: Conteo para la barra de progreso
        total_archivos = 0
        for root_dir, dirs, files in os.walk(ruta_base):
            if os.path.abspath(root_dir) == os.path.abspath(ruta_base): continue
            total_archivos += len(files)
        
        if total_archivos == 0:
            self.log("No se encontraron archivos en subcarpetas para procesar.")
            self.finalizar_proceso(0, prefix)
            return

        self.root.after(0, lambda: self.progress.config(maximum=total_archivos))
        
        # Paso 2: Procesar Archivos
        count = 0
        procesados_count = 0
        for root_dir, dirs, files in os.walk(ruta_base):
            # No procesar la raíz
            if os.path.abspath(root_dir) == os.path.abspath(ruta_base): continue

            for file in files:
                count += 1
                self.root.after(0, lambda v=count: self.progress.config(value=v))
                
                nombre, ext = os.path.splitext(file)
                ext_lc = ext.lower()

                # Verificar si coincide la extensión
                if "*" in exts_buscadas or ext_lc in exts_buscadas:
                    
                    # Definir destino
                    destino_final = ruta_base
                    if self.check_carpetas.get():
                        cat = self.obtener_categoria(ext_lc)
                        destino_final = os.path.join(ruta_base, cat)
                    
                    path_origen = os.path.join(root_dir, file)
                    path_destino = os.path.join(destino_final, file)

                    if os.path.exists(path_destino):
                        msg = f"Omitido (ya existe en destino): {file}"
                        self.log(msg)
                        archivos_procesados.append((file, "Omitido (Ya existe)", path_destino))
                        continue

                    # MOVER / SIMULAR
                    try:
                        if not modo_sim:
                            if self.check_carpetas.get(): os.makedirs(destino_final, exist_ok=True)
                            shutil.move(path_origen, path_destino)
                        
                        accion = "Simulado: Mover" if modo_sim else "Movido"
                        self.log(f"[{accion.upper()}] {file}")
                        archivos_procesados.append((file, accion, path_destino))
                        carpetas_origen_potenciales.add(root_dir)
                        procesados_count += 1
                    except Exception as e:
                        msg = f"Error moviendo {file}: {e}"
                        self.log(msg)
                        errores.append(msg)
                        archivos_procesados.append((file, "Error", str(e)))

                self.root.after(0, lambda c=count, t=total_archivos: self.label_progreso.config(text=f"Procesando: {c}/{t} archivos..."))

        # Paso 3: Limpieza de carpetas
        if self.check_borrar.get() and carpetas_origen_potenciales:
            self.log("\n--- INICIANDO LIMPIEZA DE CARPETAS ---")
            self.root.after(0, lambda: self.label_progreso.config(text="Limpiando carpetas..."))
            
            # Ordenar por profundidad inversa para borrar subcarpetas antes que padres
            for carpeta in sorted(list(carpetas_origen_potenciales), key=len, reverse=True):
                if os.path.exists(carpeta):
                    nombre_carpeta = os.path.basename(carpeta)
                    try:
                        if not modo_sim:
                            shutil.rmtree(carpeta)
                        accion = "Simulado: Borrar carpeta" if modo_sim else "Borrado"
                        self.log(f"[{accion.upper()}] {nombre_carpeta}")
                        carpetas_eliminadas.append((nombre_carpeta, accion))
                    except Exception as e:
                        msg = f"Error borrando carpeta {nombre_carpeta}: {e}"
                        self.log(msg)
                        errores.append(msg)
                        carpetas_eliminadas.append((nombre_carpeta, f"Error: {e}"))

        # Paso 4: Reporte PDF
        if self.check_pdf.get():
            self.root.after(0, lambda: self.label_progreso.config(text="Generando PDF..."))
            self.generar_reporte_pdf(ruta_base, modo_sim, archivos_procesados, carpetas_eliminadas, errores)

        self.finalizar_proceso(procesados_count, prefix)

    def generar_reporte_pdf(self, ruta, modo_sim, archivos, carpetas, errores):
        try:
            nombre_pdf = f"Reporte_FileMaster_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            path_pdf = os.path.join(ruta, nombre_pdf)
            c = canvas.Canvas(path_pdf, pagesize=letter)
            width, height = letter
            y = height - 1*inch

            # Encabezado
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, y, "Create Tech Solutions - File Master ULTRA")
            y -= 0.3*inch
            c.setFont("Helvetica", 12)
            c.drawString(1*inch, y, f"Reporte de Operación - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            y -= 0.5*inch

            # Detalles
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, f"Directorio Base: {ruta}")
            y -= 0.2*inch
            c.drawString(1*inch, y, f"Modo Simulación: {'SÍ' if modo_sim else 'NO'}")
            y -= 0.4*inch

            def check_space(current_y, needed=0.2*inch):
                if current_y < 1*inch:
                    c.showPage()
                    return height - 1*inch
                return current_y

            # Sección Archivos
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Archivos Procesados:")
            y -= 0.25*inch
            c.setFont("Helvetica", 9)
            
            for file, accion, dest in archivos:
                y = check_space(y)
                # Truncar textos largos
                file_txt = (file[:40] + '..') if len(file) > 40 else file
                dest_txt = (dest[:50] + '..') if len(dest) > 50 else dest
                c.drawString(1*inch, y, f"[{accion}] {file_txt} -> {dest_txt}")
                y -= 0.15*inch

            y -= 0.3*inch
            y = check_space(y)

            # Sección Carpetas
            if carpetas:
                c.setFont("Helvetica-Bold", 12)
                c.drawString(1*inch, y, "Limpieza de Carpetas:")
                y -= 0.25*inch
                c.setFont("Helvetica", 9)
                for carpeta, accion in carpetas:
                    y = check_space(y)
                    c.drawString(1*inch, y, f"[{accion}] {carpeta}")
                    y -= 0.15*inch
                y -= 0.3*inch

            # Sección Errores
            y = check_space(y, 0.5*inch)
            if errores:
                c.setFillColorRGB(1, 0, 0) # Rojo
                c.setFont("Helvetica-Bold", 12)
                c.drawString(1*inch, y, "Errores Encontrados:")
                y -= 0.25*inch
                c.setFont("Helvetica", 9)
                for err in errores:
                    y = check_space(y)
                    c.drawString(1*inch, y, f"!! {err}")
                    y -= 0.15*inch

            c.save()
            self.log(f"\n[REPORTE] PDF generado con éxito: {nombre_pdf}")
        except Exception as e:
            self.log(f"\n[ERROR PDF] No se pudo generar el reporte: {e}")

    def finalizar_proceso(self, count, prefix):
        final_msg = f"\n--- PROCESO FINALIZADO {prefix}---"
        self.log(final_msg)
        
        self.root.after(0, lambda: self.btn_ejecutar.config(state="normal"))
        self.root.after(0, lambda: self.label_progreso.config(text=f"Completado. {count} archivos organizados."))
        
        modo_sim = self.check_simulacion.get()
        title = "Simulación Completada" if modo_sim else "Proceso Exitoso"
        body = f"Se han procesado {count} archivos.\n"
        if modo_sim: body += "\nRECUERDA: Nada se movió realmente (Modo Simulación)."
        if self.check_pdf.get(): body += "\nSe generó un reporte PDF en la carpeta base."

        self.root.after(0, lambda: messagebox.showinfo(title, body))


class LicenciaManager:
    @staticmethod
    def obtener_hwid():
        """Obtiene el UUID único de la placa base en Windows."""
        try:
            cmd = 'wmic csproduct get uuid'
            uuid = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
            return uuid
        except:
            return "ID-GENERICO-CTS-2026"

    @staticmethod
    def validar_key(hwid, key_usuario):
        """Lógica de validación: La key debe coincidir con el hash MD5 del HWID."""
        
        salt_secreto = "CTS_PRO_2026_SECURITY_99"
        key_esperada = hashlib.md5((hwid + salt_secreto).encode()).hexdigest().upper()[:12]
        
        return key_usuario.upper() == key_esperada



def verificar_acceso():
    hwid = LicenciaManager.obtener_hwid()
    
    # Supongamos que guardamos la licencia en un archivo local .lic
    if os.path.exists("license.lic"):
        with open("license.lic", "r") as f:
            key_guardada = f.read().strip()
            if LicenciaManager.validar_key(hwid, key_guardada):
                return True

    # Si no hay licencia o es inválida, pedirla
    ventana_lic = tk.Tk()
    ventana_lic.title("Activación - Create Tech Solutions")
    ventana_lic.geometry("400x250")
    
    tk.Label(ventana_lic, text="Software no activado", font=('Arial', 12, 'bold')).pack(pady=10)
    tk.Label(ventana_lic, text=f"Tu ID de Hardware (HWID):\n{hwid}", fg="blue").pack()
    
    entry_key = tk.Entry(ventana_lic, width=30)
    entry_key.pack(pady=10)
    
    def activar():
        key = entry_key.get()
        if LicenciaManager.validar_key(hwid, key):
            with open("license.lic", "w") as f:
                f.write(key)
            messagebox.showinfo("Éxito", "Software activado correctamente.")
            ventana_lic.destroy()
            lanzar_app_principal()
        else:
            messagebox.showerror("Error", "Key de activación incorrecta.")

    tk.Button(ventana_lic, text="Activar Ahora", command=activar).pack(pady=10)
    ventana_lic.mainloop()
    return False

def lanzar_app_principal():
    root = tk.Tk()
    app = OrganizadorUltra(root)
    root.mainloop()

if __name__ == "__main__":
    # Primero verificamos la licencia antes de iniciar todo
    if verificar_acceso():
        lanzar_app_principal()