import webview
import json
import os
import shutil
import threading
from core.organizer_logic import FileEngine
from core.license_validator import LicenseManager

class CTS_Bridge:
    """
    Bridge para conectar el JavaScript de la UI con el core Python.
    """
    def __init__(self):
        self.engine = FileEngine()

    def verificar_activacion(self):
        """Verifica si el software está activado y retorna el estado."""
        lic_file = "license.cts"
        if os.path.exists(lic_file):
            with open(lic_file, "r") as f:
                key = f.read().strip()
                if LicenseManager.validate_key(key):
                    return {"activado": True, "hwid": LicenseManager.get_hwid()}
        return {"activado": False, "hwid": LicenseManager.get_hwid()}

    def intentar_activacion(self, key):
        """Intenta activar el software con la key proporcionada."""
        if LicenseManager.validate_key(key):
            with open("license.cts", "w") as f:
                f.write(key)
            return {"exito": True, "mensaje": "Software activado correctamente"}
        return {"exito": False, "mensaje": "Key inválida"}

    def get_defaults(self):
        """Envía las categorías por defecto a la UI para que las muestre."""
        return json.dumps(self.engine.categories)

    def seleccionar_carpeta(self):
        """Abre el selector nativo de carpetas y retorna la ruta seleccionada."""
        window = webview.active_window()
        if window is None and hasattr(webview, 'windows') and webview.windows:
            window = webview.windows[0]

        if window is None:
            raise RuntimeError("No hay ventana activa de pywebview")

        resultado = window.create_file_dialog(webview.FileDialog.FOLDER)
        if resultado:
            return resultado[0]
        return None

    def ejecutar_accion(self, modulo, data):
        """
        Punto de entrada para cualquier acción de la UI.
        modulo: 'estandar', 'multimedia', 'avanzado'
        data: Diccionario con la configuración elegida en la web.
        """
        ruta = data.get('ruta')
        
        if modulo == "estandar":
            # Usa la configuración por defecto
            return self.engine.organize(data['ruta'], mode="folders")
        
        elif modulo == "inteligente":
            # Lógica específica para orden inteligente: organiza dentro de carpetas por tipo y fecha
            include_subfolders = data.get('includeSubfolders', True)
            sort_by_date = data.get('sortByDate', True)
            return self.engine.organize_inteligente(data['ruta'], include_subfolders, sort_by_date)
            
        elif modulo == "limpieza":
            # Lógica para limpieza de archivos duplicados - en segundo plano
            def limpieza_thread(source_path):
                window = webview.active_window()
                result = self.engine.remove_duplicates(source_path)
                # Cerrar modal y notificar al frontend
                window.evaluate_js("Swal.close();")
                window.evaluate_js(f"Toast.fire({{icon: 'success', title: {json.dumps(result)}}})")

            threading.Thread(target=limpieza_thread, args=(data['ruta'],)).start()
            return "Procesando limpieza de duplicados en segundo plano..."
            
        elif modulo == "avanzado":
            # Lógica que usa configuraciones personalizadas
            extensiones_raw = data.get('extensiones', "")
            folder_name = data.get('folderName', "Personalizado")
            sort_by_date = data.get('sortByDate', False)
            
            # Convertimos la cadena ".exe, .msi" en una lista limpia
            lista_exts = [e.strip().lower() for e in extensiones_raw.split(',') if e.strip()]
            
            if not lista_exts:
                return "Error: Debes especificar al menos una extensión en el modo avanzado."
                
            return self.engine.organize_advanced(data['ruta'], lista_exts, folder_name, sort_by_date)
            
        elif modulo == "extraccion":
            # Lógica para extracción selectiva
            extensiones_raw = data.get('extensiones', "")
            create_subfolders = data.get('create_carpet_type', True)
            delete_source = data.get('delete_carpet', False)
            simulation = data.get('mode_simulation', False)
            sort_by_date = data.get('sort_by_date', False)
            
            if not extensiones_raw:
                return "Error: Debes seleccionar al menos una categoría de extensiones para la extracción."
                
            return self.engine.extract_selective(data['ruta'], extensiones_raw, create_subfolders, delete_source, simulation, sort_by_date)
            
        elif modulo == "undo":
            # Deshacer última acción
            return self.engine.undo_last_action()
            
        return "Acción no reconocida."