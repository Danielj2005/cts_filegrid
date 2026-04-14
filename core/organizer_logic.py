import os
import shutil
import hashlib
import time


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
        """Escanea y elimina duplicados basados en contenido."""
        seen_hashes = {}
        deleted_count = 0
        
        # Listar archivos
        files = [os.path.join(source_path, f) for f in os.listdir(source_path) 
                if os.path.isfile(os.path.join(source_path, f))]

        for file_path in files:
            file_hash = self.get_file_hash(file_path)
            
            if file_hash in seen_hashes:
                # Ya existe un archivo igual, este se borra
                os.remove(file_path)
                deleted_count += 1
            else:
                # Es la primera vez que vemos este contenido
                seen_hashes[file_hash] = file_path
                
        return f"Limpieza completada. Se eliminaron {deleted_count} archivos duplicados."
    
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
    
    
    