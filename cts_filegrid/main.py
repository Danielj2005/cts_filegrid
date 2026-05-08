import webview
import os
from core.license_validator import LicenseManager
from bridge import CTS_Bridge  # Asegúrate de tener este archivo creado

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