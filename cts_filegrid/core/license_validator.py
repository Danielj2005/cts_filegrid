import hashlib
import subprocess

class LicenseManager:
    # Este SALT debe ser el mismo en tu KeyGen privado
    _SALT = "CTS_PRO_2026_SECURITY_99" 

    @staticmethod
    def get_hwid():
        """Obtiene el ID único de la placa base."""
        try:
            cmd = 'wmic csproduct get uuid'
            uuid = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
            return uuid
        except:
            return "ERROR-HWID-GENERIC"

    @classmethod
    def validate_key(cls, user_key):
        """Compara la llave del usuario con el hash esperado del HWID."""
        hwid = cls.get_hwid()
        expected_key = hashlib.md5((hwid + cls._SALT).encode()).hexdigest().upper()[:12]
        return user_key.upper() == expected_key