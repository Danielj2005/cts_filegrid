import os
import shutil
import hashlib
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from datetime import datetime
from send2trash import send2trash


class FileEngine:
    def __init__(self):
        self.categories = {
            "Documentos": [
                ".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".ppt",
                ".odt", ".ods", ".odp", ".rtf", ".csv", ".md", ".html", ".htm",
                ".xml", ".json", ".log",
            ],
            "Imágenes": [
                ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".tif",
                ".svg", ".heic", ".ico", ".psd",
            ],
            "Videos": [
                ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mpeg",
                ".mpg", ".m4v",
            ],
            "Audio": [
                ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma",
            ],
            "Comprimidos": [
                ".zip", ".rar", ".7z", ".tar", ".gz", ".tar.gz", ".tgz", ".bz2", ".xz", ".iso",
            ],
            "Otros": []
        }
        self.actions_log = []  # Lista de acciones para deshacer: [(action, src, dest), ...]
        
    def organize(self, source, mode="folders", rename=False):
        """
        MODOS:
        'simple': Mueve todo a una carpeta raíz 'Organizado'.
        'folders': Crea subcarpetas por tipo (PDF, Imágenes, etc).
        """
        dest_root = os.path.join(source, "CTS_Organizado")
        os.makedirs(dest_root, exist_ok=True)
        
        files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
        
        for i, filename in enumerate(files):
            ext = os.path.splitext(filename)[1].lower()
            src_path = os.path.join(source, filename)
            
            # 1. Determinar Carpeta Destino
            subfolder = ""
            if mode == "folders":
                for cat, exts in self.categories.items():
                    if ext in exts:
                        subfolder = cat
                        break
                else: subfolder = "Otros"
            
            final_dir = os.path.join(dest_root, subfolder)
            os.makedirs(final_dir, exist_ok=True)

            # 2. Lógica de Renombrado
            new_name = filename
            if rename:
                # Ejemplo: CTS_001_documento.pdf
                new_name = f"CTS_{str(i+1).zfill(3)}_{filename}"

            shutil.move(src_path, os.path.join(final_dir, new_name))
            
    def get_file_hash(self, path):
        """Calcula MD5 para detectar duplicados reales."""
        hasher = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def scan_directory(self, source, selected_cats):
        """Escanea y clasifica archivos."""
        results = []
        hashes_seen = {}
        
        # Filtrar extensiones basadas en selección de UI
        active_exts = []
        for cat in selected_cats:
            active_exts.extend(self.categories.get(cat, []))

        for root, _, files in os.walk(source):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in active_exts:
                    path = os.path.join(root, f)
                    f_hash = self.get_file_hash(path)
                    
                    is_duplicate = f_hash in hashes_seen
                    if not is_duplicate:
                        hashes_seen[f_hash] = f
                        
                    results.append({
                        "name": f,
                        "path": path,
                        "ext": ext,
                        "duplicate": is_duplicate
                    })
        return results
    
    def remove_duplicates(self, source_path):
        """Escanea y elimina duplicados basados en contenido en todo el árbol de carpetas."""
        seen_hashes = {}
        deleted_count = 0
        errors = []
        removed_items = []

        for root, _, files in os.walk(source_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    file_hash = self.get_file_hash(file_path)
                except Exception as e:
                    errors.append(f"Error leyendo {file_path}: {e}")
                    continue

                if file_hash in seen_hashes:
                    try:
                        send2trash(file_path)
                        deleted_count += 1
                        removed_items.append((file_path, seen_hashes[file_hash]))
                    except Exception as e:
                        errors.append(f"Error enviando a papelera {file_path}: {e}")
                else:
                    seen_hashes[file_hash] = file_path

        pdf_result = self.generar_reporte_pdf_limpieza(source_path, deleted_count, removed_items, errors)
        summary = f"Limpieza completada. Se enviaron {deleted_count} archivos duplicados a la papelera. {pdf_result}"

        if errors:
            summary += f" Errores: {len(errors)}"

        return summary

    def generar_reporte_pdf_limpieza(self, ruta, deleted_count, removed_items, errores):
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            reportes_dir = os.path.join(desktop, "reportes file master Pro")
            os.makedirs(reportes_dir, exist_ok=True)

            nombre_pdf = f"reporte{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            path_pdf = os.path.join(reportes_dir, nombre_pdf)
            c = canvas.Canvas(path_pdf, pagesize=letter)
            width, height = letter
            y = height - 1*inch

            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, y, "Create Tech Solutions - File Master Pro")
            y -= 0.3*inch
            c.setFont("Helvetica", 12)
            c.drawString(1*inch, y, f"Reporte de Limpieza de Duplicados - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            y -= 0.5*inch

            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, f"Directorio Analizado: {ruta}")
            y -= 0.25*inch
            c.drawString(1*inch, y, f"Archivos duplicados enviados a papelera: {deleted_count}")
            y -= 0.4*inch

            def check_space(current_y, needed=0.2*inch):
                if current_y < 1*inch:
                    c.showPage()
                    return height - 1*inch
                return current_y

            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Archivos Enviados a Papelera:")
            y -= 0.25*inch
            c.setFont("Helvetica", 9)

            if removed_items:
                for removed, original in removed_items:
                    y = check_space(y)
                    removed_text = (removed[:70] + '..') if len(removed) > 70 else removed
                    original_text = (original[:70] + '..') if len(original) > 70 else original
                    c.drawString(1*inch, y, f"{removed_text}")
                    y -= 0.15*inch
                    c.drawString(1.1*inch, y, f"Duplicado de: {original_text}")
                    y -= 0.25*inch
            else:
                c.drawString(1*inch, y, "No se detectaron archivos duplicados.")
                y -= 0.25*inch

            if errores:
                y = check_space(y, 0.4*inch)
                c.setFillColorRGB(1, 0, 0)
                c.setFont("Helvetica-Bold", 12)
                c.drawString(1*inch, y, "Errores Encontrados:")
                y -= 0.25*inch
                c.setFont("Helvetica", 9)
                for err in errores:
                    y = check_space(y)
                    c.drawString(1*inch, y, f"- {err}")
                    y -= 0.15*inch
                c.setFillColorRGB(0, 0, 0)

            c.save()
            return f"Reporte generado: {path_pdf}"
        except Exception as e:
            return f"Error generando PDF: {e}"
    
    def organize_inteligente(self, source_path, include_subfolders=True, sort_by_date=True):
        """
        Organiza archivos dentro de sus carpetas por tipo y opcionalmente por fecha.
        No mueve archivos fuera de sus carpetas; mantiene la jerarquía.
        """
        count = 0
        
        # Función recursiva para procesar carpetas
        def process_folder(folder_path):
            nonlocal count
            # Primero, procesar archivos en esta carpeta
            files_in_folder = []
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    files_in_folder.append((item, item_path))
            
            # Organizar archivos de esta carpeta
            for filename, file_path in files_in_folder:
                ext = os.path.splitext(filename)[1].lower()
                
                # Determinar categoría
                category = "Otros"
                for cat, exts in self.categories.items():
                    if ext in exts:
                        category = cat
                        break
                
                # Crear carpeta por tipo dentro de la carpeta actual
                category_dir = os.path.join(folder_path, category)
                if sort_by_date:
                    # Obtener fecha y crear subcarpetas Año/Mes
                    stats = os.stat(file_path)
                    fecha = time.localtime(stats.st_mtime)
                    year = str(fecha.tm_year)
                    month = time.strftime('%B', fecha)  # Nombre del mes
                    target_dir = os.path.join(category_dir, year, month)
                else:
                    target_dir = category_dir
                
                os.makedirs(target_dir, exist_ok=True)
                
                # Mover archivo
                shutil.move(file_path, os.path.join(target_dir, filename))
                count += 1
            
            # Si incluir subcarpetas, procesar recursivamente
            if include_subfolders:
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isdir(item_path) and item not in self.categories.keys() and not item.startswith('CTS_'):
                        process_folder(item_path)
        
        process_folder(source_path)
        return f"Se organizaron {count} archivos inteligentemente dentro de sus carpetas."
    
    
    def organize_advanced(self, source_path, extensions, folder_name, sort_by_date=False):
        """
        Mueve solo los archivos con las extensiones indicadas 
        a una carpeta con nombre personalizado.
        Si sort_by_date es True, organiza por Año/Mes.
        """
        import os
        import shutil
        
        target_dir = os.path.join(source_path, folder_name)
        if not sort_by_date:
            os.makedirs(target_dir, exist_ok=True)
        
        count = 0
        for filename in os.listdir(source_path):
            file_path = os.path.join(source_path, filename)
            
            if os.path.isfile(file_path):
                # Verificamos si la extensión del archivo está en la lista del usuario
                _, ext = os.path.splitext(filename)
                if ext.lower() in extensions:
                    if sort_by_date:
                        # Obtener fecha y crear subcarpetas
                        stats = os.stat(file_path)
                        fecha = time.localtime(stats.st_mtime)
                        year = str(fecha.tm_year)
                        month = time.strftime('%B', fecha)
                        final_dir = os.path.join(target_dir, year, month)
                        os.makedirs(final_dir, exist_ok=True)
                        shutil.move(file_path, os.path.join(final_dir, filename))
                    else:
                        shutil.move(file_path, os.path.join(target_dir, filename))
                    count += 1
        
        if count == 0:
            return f"No se encontraron archivos con las extensiones: {', '.join(extensions)}"
            
        return f"¡Éxito! Se movieron {count} archivos a la carpeta '{folder_name}'."

    def extract_selective(self, source_path, extensions, create_subfolders=True, delete_source_folders=False, simulation_mode=False, sort_by_date=False):
        """
        Extrae archivos con extensiones específicas de subcarpetas a la carpeta principal.
        Opciones:
        - create_subfolders: Crear subcarpetas por tipo de archivo
        - delete_source_folders: Eliminar carpetas de origen después de extraer
        - simulation_mode: Solo simular, no mover nada
        - sort_by_date: Ordenar archivos por fecha (no implementado aún)
        """
        import os
        import shutil
        from datetime import datetime

        archivos_procesados = []
        carpetas_eliminadas = []
        errores = []
        carpetas_origen_potenciales = set()

        # Procesar extensiones
        exts_buscadas = [e.strip().lower() for e in extensions.split(',') if e.strip()]

        # Paso 1: Conteo de archivos para progreso (simulado)
        total_archivos = 0
        for root_dir, dirs, files in os.walk(source_path):
            if os.path.abspath(root_dir) == os.path.abspath(source_path): continue
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in exts_buscadas:
                    total_archivos += 1

        if total_archivos == 0:
            return "No se encontraron archivos con las extensiones especificadas en subcarpetas."

        # Paso 2: Procesar archivos
        procesados_count = 0
        files_to_process = []
        for root_dir, dirs, files in os.walk(source_path):
            if os.path.abspath(root_dir) == os.path.abspath(source_path): continue
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in exts_buscadas:
                    path_origen = os.path.join(root_dir, file)
                    mtime = os.path.getmtime(path_origen)
                    files_to_process.append((path_origen, file, ext.lower(), root_dir, mtime))

        # Ordenar por fecha si se solicita
        if sort_by_date:
            files_to_process.sort(key=lambda x: x[4])  # sort by mtime

        for path_origen, file, ext_lc, root_dir, mtime in files_to_process:
            # Definir destino
            destino_final = source_path
            if create_subfolders:
                category = "Otros"
                for cat, exts in self.categories.items():
                    if ext_lc in exts:
                        category = cat
                        break
                destino_final = os.path.join(source_path, category)
            
            if sort_by_date:
                # Crear subcarpetas por año/mes
                fecha = time.localtime(mtime)
                year = str(fecha.tm_year)
                month = f"{fecha.tm_mon:02d}"  # Mes con cero
                destino_final = os.path.join(destino_final, year, month)

            path_destino = os.path.join(destino_final, file)

            if os.path.exists(path_destino):
                archivos_procesados.append((file, "Omitido (Ya existe)", path_destino))
                continue

            # MOVER / SIMULAR
            try:
                if not simulation_mode:
                    os.makedirs(destino_final, exist_ok=True)
                    shutil.move(path_origen, path_destino)
                    self.actions_log.append(("move", path_origen, path_destino))  # Registrar para deshacer

                accion = "Simulado: Mover" if simulation_mode else "Movido"
                archivos_procesados.append((file, accion, path_destino))
                carpetas_origen_potenciales.add(root_dir)
                procesados_count += 1
            except Exception as e:
                errores.append(f"Error moviendo {file}: {e}")
                archivos_procesados.append((file, "Error", str(e)))

        # Paso 3: Limpieza de carpetas
        if delete_source_folders and carpetas_origen_potenciales:
            for carpeta in sorted(list(carpetas_origen_potenciales), key=len, reverse=True):
                if os.path.exists(carpeta):
                    try:
                        if not simulation_mode:
                            send2trash(carpeta)
                        accion = "Simulado: Enviar carpeta a papelera" if simulation_mode else "Enviado a papelera"
                        carpetas_eliminadas.append((os.path.basename(carpeta), accion))
                    except Exception as e:
                        errores.append(f"Error enviando carpeta a papelera {os.path.basename(carpeta)}: {e}")
                        carpetas_eliminadas.append((os.path.basename(carpeta), f"Error: {e}"))

        # Generar PDF obligatorio
        pdf_result = self.generar_reporte_pdf(source_path, simulation_mode, archivos_procesados, carpetas_eliminadas, errores, sort_by_date, delete_source_folders)

        reporte = f"Extracción completada. {procesados_count} archivos procesados. {pdf_result}"
        if errores:
            reporte += f" Errores: {len(errores)}"
        if carpetas_eliminadas:
            reporte += f" Carpetas eliminadas: {len(carpetas_eliminadas)}"

        return reporte

    def delete_selective(self, source_path, extensions, include_subfolders=True, delete_source_folders=False):
        """
        Elimina archivos que coincidan con las extensiones seleccionadas.
        Envía los archivos a la papelera y opcionalmente elimina carpetas vacías.
        """
        exts_buscadas = [e.strip().lower() for e in extensions.split(',') if e.strip()]
        if not exts_buscadas:
            return "Error: No se especificaron extensiones para la eliminación selectiva."

        archivos_eliminados = []
        errores = []
        root_abs = os.path.abspath(source_path)

        for root, _, files in os.walk(source_path):
            if not include_subfolders and os.path.abspath(root) != root_abs:
                continue

            for filename in files:
                _, ext = os.path.splitext(filename)
                if ext.lower() in exts_buscadas:
                    file_path = os.path.join(root, filename)
                    try:
                        send2trash(file_path)
                        archivos_eliminados.append(file_path)
                    except Exception as e:
                        errores.append(f"Error enviando a papelera {file_path}: {e}")

        carpetas_eliminadas = []
        if delete_source_folders:
            for root, dirs, files in os.walk(source_path, topdown=False):
                if os.path.abspath(root) == root_abs:
                    continue
                try:
                    if not os.listdir(root):
                        send2trash(root)
                        carpetas_eliminadas.append(root)
                except Exception as e:
                    errores.append(f"Error enviando carpeta a papelera {root}: {e}")

        if not archivos_eliminados:
            return "No se encontraron archivos con las extensiones seleccionadas para eliminar."

        pdf_result = self.generar_reporte_pdf_eliminacion(
            source_path,
            archivos_eliminados,
            carpetas_eliminadas,
            errores,
            exts_buscadas,
            include_subfolders,
            delete_source_folders,
        )

        resumen = f"Eliminación completada. Se enviaron {len(archivos_eliminados)} archivos a la papelera."
        if carpetas_eliminadas:
            resumen += f" Se enviaron {len(carpetas_eliminadas)} carpetas vacías a la papelera."
        if errores:
            resumen += f" Errores: {len(errores)}"
        resumen += f" {pdf_result}"

        return resumen

    def generar_reporte_pdf_eliminacion(self, ruta, archivos_eliminados, carpetas_eliminadas, errores, extensiones, include_subfolders, delete_source_folders):
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            reportes_dir = os.path.join(desktop, "reportes file master Pro")
            os.makedirs(reportes_dir, exist_ok=True)

            nombre_pdf = f"reporte{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            path_pdf = os.path.join(reportes_dir, nombre_pdf)
            c = canvas.Canvas(path_pdf, pagesize=letter)
            width, height = letter
            y = height - 1*inch

            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, y, "Create Tech Solutions - File Master Pro")
            y -= 0.3*inch
            c.setFont("Helvetica", 12)
            c.drawString(1*inch, y, f"Reporte de Eliminación Selectiva - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            y -= 0.5*inch

            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, f"Directorio Analizado: {ruta}")
            y -= 0.2*inch
            c.drawString(1*inch, y, f"Extensiones: {', '.join(extensiones)}")
            y -= 0.2*inch
            c.drawString(1*inch, y, f"Incluir subcarpetas: {'SÍ' if include_subfolders else 'NO'}")
            y -= 0.2*inch
            c.drawString(1*inch, y, f"Eliminar carpetas vacías: {'SÍ' if delete_source_folders else 'NO'}")
            y -= 0.4*inch

            def check_space(current_y, needed=0.2*inch):
                if current_y < 1*inch:
                    c.showPage()
                    return height - 1*inch
                return current_y

            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Archivos Enviados a Papelera:")
            y -= 0.25*inch
            c.setFont("Helvetica", 9)

            for file_path in archivos_eliminados:
                y = check_space(y)
                display_path = (file_path[:80] + '..') if len(file_path) > 80 else file_path
                c.drawString(1*inch, y, f"- {display_path}")
                y -= 0.15*inch

            if carpetas_eliminadas:
                y -= 0.2*inch
                c = self._draw_section_title(c, y, "Carpetas Enviadas a Papelera:")

            if carpetas_eliminadas:
                y -= 0.25*inch
                c.setFont("Helvetica", 9)
                for folder_path in carpetas_eliminadas:
                    y = check_space(y)
                    display_path = (folder_path[:80] + '..') if len(folder_path) > 80 else folder_path
                    c.drawString(1*inch, y, f"- {display_path}")
                    y -= 0.15*inch

            if errores:
                y = check_space(y, 0.4*inch)
                c.setFillColorRGB(1, 0, 0)
                c.setFont("Helvetica-Bold", 12)
                c.drawString(1*inch, y, "Errores Encontrados:")
                y -= 0.25*inch
                c.setFont("Helvetica", 9)
                for err in errores:
                    y = check_space(y)
                    c.drawString(1*inch, y, f"- {err}")
                    y -= 0.15*inch
                c.setFillColorRGB(0, 0, 0)

            c.save()
            return f"Reporte generado: {path_pdf}"
        except Exception as e:
            return f"Error generando PDF: {e}"

    def _draw_section_title(self, c, y, title):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y, title)
        return c

    def undo_last_action(self):
        """
        Deshace la última acción realizada.
        """
        if not self.actions_log:
            return "No hay acciones para deshacer."

        # Revertir en orden inverso
        reversed_actions = self.actions_log[::-1]
        undone_count = 0
        for action, src, dest in reversed_actions:
            try:
                if action == "move":
                    shutil.move(dest, src)
                elif action == "delete_folder":
                    # No podemos recrear carpetas borradas fácilmente, así que omitir
                    pass
                undone_count += 1
            except Exception as e:
                return f"Error deshaciendo: {e}"

        self.actions_log = []  # Limpiar log después de deshacer
        return f"Se deshicieron {undone_count} acciones."

    def generar_reporte_pdf(self, ruta, modo_sim, archivos, carpetas, errores, sort_by_date, delete_source_folders):
        """
        Genera un reporte PDF con buen diseño.
        """
        try:
            # Crear carpeta en escritorio
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            reportes_dir = os.path.join(desktop, "reportes file master Pro")
            os.makedirs(reportes_dir, exist_ok=True)

            nombre_pdf = f"reporte{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            path_pdf = os.path.join(reportes_dir, nombre_pdf)
            c = canvas.Canvas(path_pdf, pagesize=letter)
            width, height = letter
            y = height - 1*inch

            # Encabezado
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, y, "Create Tech Solutions - File Master Pro")
            y -= 0.3*inch
            c.setFont("Helvetica", 12)
            c.drawString(1*inch, y, f"Reporte de Extracción Selectiva - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            y -= 0.5*inch

            # Detalles
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, f"Directorio Base: {ruta}")
            y -= 0.2*inch
            c.drawString(1*inch, y, f"Modo Simulación: {'SÍ' if modo_sim else 'NO'}")
            y -= 0.2*inch
            c.drawString(1*inch, y, f"Ordenar por Fecha: {'SÍ' if sort_by_date else 'NO'}")
            y -= 0.2*inch
            c.drawString(1*inch, y, f"Eliminar Carpetas Origen: {'SÍ' if delete_source_folders else 'NO'}")
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
                c.setFillColorRGB(1, 0, 0)  # Rojo
                c.setFont("Helvetica-Bold", 12)
                c.drawString(1*inch, y, "Errores Encontrados:")
                y -= 0.25*inch
                c.setFont("Helvetica", 9)
                for err in errores:
                    y = check_space(y)
                    c.drawString(1*inch, y, f"!! {err}")
                    y -= 0.15*inch

            c.save()
            return f"Reporte generado: {path_pdf}"
        except Exception as e:
            return f"Error generando PDF: {e}"
    
    
    