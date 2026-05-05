import hashlib
import os
import webview

class KeyGenBridge:
    SALT = "CTS_PRO_2026_SECURITY_99"

    def generar_key(self, hwid):
        hwid = (hwid or "").strip()
        if not hwid:
            return {"error": "Por favor ingresa un HWID válido."}

        key = hashlib.md5((hwid + self.SALT).encode()).hexdigest().upper()[:12]
        return {"key": key}


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.abspath(os.path.join(current_dir, 'ui', 'keygen.html'))
    user_data_dir = os.path.join(current_dir, 'webview_user_data')
    os.makedirs(user_data_dir, exist_ok=True)

    api = KeyGenBridge()
    window = webview.create_window(
        title='CTS - Generador de Licencias',
        url=html_path,
        js_api=api,
        width=720,
        height=620,
        resizable=False,
        background_color='#111827',
        user_data_dir=user_data_dir,
    )

    webview.start(debug=False, gui='edgechromium')
