File Master Pro: Enterprise Security Suite 📁🚀
File Master Pro es una solución robusta de automatización para la gestión de activos digitales, diseñada específicamente para entornos retail, administrativos y educativos. Desarrollada por Create Tech Solutions, esta herramienta optimiza flujos de trabajo mediante el procesamiento concurrente, la eliminación inteligente de duplicados y un sistema de licenciamiento basado en hardware (DRM).

🌟 Características Principales
Organización Inteligente: Clasificación automática de archivos por categorías (Documentos, Imágenes, Videos, etc.) con un solo clic.

Deduplicación por Hash (MD5): Identifica y elimina archivos duplicados basándose en su contenido binario, no solo en el nombre.

Procesamiento Concurrente: Arquitectura multihilo que mantiene la interfaz fluida durante operaciones intensivas de I/O.

Sistema de Licenciamiento (DRM): Protección de software mediante Hardware ID (HWID), vinculando la licencia a la placa base del usuario.

Reportística Profesional: Generación automática de auditorías en PDF con el resumen de archivos movidos y errores detectados.

UX/UI Intuitiva: Interfaz diseñada para usuarios finales (papelerías, colegios, oficinas) con selectores de categorías por checkboxes.

🏗️ Arquitectura del Ecosistema
El proyecto se divide en dos componentes independientes para garantizar la seguridad comercial:

Client Application: El binario ejecutable (.exe) que el usuario final utiliza. Contiene la lógica de validación de licencia, pero no la de generación.

KeyGen Master (Admin): Una utilidad privada (desplegada también en plataformas móviles como Flutter/Termux) que genera llaves de activación únicas basadas en el HWID del cliente + un Secret Salt propietario.

🛠️ Tecnologías Utilizadas
Lenguaje: Python 3.14

Interfaz Gráfica: Tkinter con estilización personalizada.

Criptografía: Librería hashlib para MD5 y Salting.

Generación de Reportes: ReportLab (PDF Engine).

Gestión de Sistemas: os, shutil y subprocess para interacción de bajo nivel con Windows.

Distribución: PyInstaller para empaquetamiento de binarios independientes.

🚀 Instalación y Uso
Requisitos previos
Bash
pip install reportlab
Ejecución
Bash
python main_organizer.py
Compilación a EXE
Para generar el ejecutable profesional:

Bash
pyinstaller --noconsole --onefile --name "FileMaster_Pro" --icon=assets/logo.ico main_organizer.py
💼 Caso de Uso: Sector Retail
Ideal para papelerías y centros de copiado en Venezuela que manejan volúmenes masivos de documentos de clientes. El software reduce el tiempo de búsqueda manual en un 80% y optimiza el almacenamiento al eliminar copias innecesarias.

🛡️ Seguridad y Propiedad Intelectual
Este software es propiedad de Create Tech Solutions. El sistema de licencias previene la distribución no autorizada mediante el binding de hardware. Si intentas ejecutar la aplicación en una máquina no autorizada, el sistema solicitará una llave única generada por el administrador.

👨‍💻 Sobre el Autor
Desarrollado por un Software Engineer apasionado por la arquitectura de sistemas y la seguridad.

Empresa: Create Tech Solutions

Ubicación: Venezuela 🇻🇪

Especialidad: Backend Architecture, API Design & Desktop Automation.
