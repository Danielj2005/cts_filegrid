import webview
import os
import tkinter as tk
from tkinter import messagebox
from core.license_validator import LicenseManager
from bridge import CTS_Bridge  # Asegúrate de tener este archivo creado

def check_activation():
    lic_file = "license.cts"
    hwid = LicenseManager.get_hwid()
    
    if os.path.exists(lic_file):
        with open(lic_file, "r") as f:
            key = f.read().strip()
            if LicenseManager.validate_key(key):
                return True
    
    # Mantendremos la activación en Tkinter por ahora porque es funcional
    # pero el éxito lanzará la ventana de PyWebView
    show_activation_ui(hwid)
    return False

def show_activation_ui(hwid):
    # (Tu código de activación de Tkinter se queda igual)
    # Solo asegúrate de que al final diga que reinicien para cargar la nueva UI
    act_win = tk.Tk()
    act_win.title("Activación Requerida - CTS")
    
    tk.Label(act_win, text="ID de Hardware (HWID):").pack(pady=5)
    entry_hwid = tk.Entry(act_win, width=40, justify="center")
    entry_hwid.insert(0, hwid)
    entry_hwid.config(state="readonly")
    entry_hwid.pack(padx=20)
    
    def copy():
        act_win.clipboard_clear()
        act_win.clipboard_append(hwid)
        messagebox.showinfo("CTS", "Copiado al portapapeles")
    
    tk.Button(act_win, text="Copiar HWID", command=copy).pack(pady=5)
    tk.Label(act_win, text="Ingrese su Key:").pack(pady=5)
    entry_key = tk.Entry(act_win, width=40)
    entry_key.pack()

    def activate():
        key = entry_key.get().strip()
        if LicenseManager.validate_key(key):
            with open("license.cts", "w") as f: f.write(key)
            messagebox.showinfo("Éxito", "Software Activado. Reinicie la aplicación.")
            act_win.destroy()
        else:
            messagebox.showerror("Error", "Key Inválida")

    tk.Button(act_win, text="Activar Ahora", command=activate).pack(pady=20)
    act_win.mainloop()

if __name__ == "__main__":
    # Siempre iniciar la aplicación web - la activación se maneja en el frontend
    api = CTS_Bridge()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, 'ui', 'index.html')
    
    window = webview.create_window(
        title='CTS FileGrid - Create Tech Solutions',
        url=html_path,
        js_api=api,
        width=1100,
        height=750,
        background_color='#111827',
    )

    webview.start(debug=False)