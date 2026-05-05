import hashlib
import subprocess
import os

class validador_licencia:
    SALT_SECRETO = "CTS_PRO_2026_SECURITY_99" # Debe ser igual al del KeyGen

    @staticmethod
    def obtener_hwid():
        try:
            cmd = 'wmic csproduct get uuid'
            return subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
        except:
            return "ERROR_HWID"

    @classmethod
    def validar(cls, key_usuario):
        hwid = cls.obtener_hwid()
        # El programa hace el mismo cálculo que el KeyGen
        key_correcta = hashlib.md5((hwid + cls.SALT_SECRETO).encode()).hexdigest().upper()[:12]
        return key_usuario.upper() == key_correcta

# --- En el arranque de tu App Principal ---
def verificar_al_iniciar():
    path_licencia = "config.cts" # Archivo donde se guarda la llave
    
    if os.path.exists(path_licencia):
        with open(path_licencia, "r") as f:
            key_guardada = f.read().strip()
            if validador_licencia.validar(key_guardada):
                return True # Acceso concedido
                
    # Si no hay licencia o es falsa, pedirla con la ventana de activación
    # (Aquí iría la ventana de activación que ya diseñamos anteriormente)