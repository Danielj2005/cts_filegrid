

tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        cts: {
          bg: "#111827", // Fondo ultra oscuro (slate-900)
          card: "#1f2937", // Fondo de tarjeta (slate-800)
          accent: "#00ff9d", // Tu verde esmeralda neón
          text: "#f3f4f6", // Texto claro
        },
        danger: "#f87171",
      },
    },
  },
};

const Toast = Swal.mixin({
  toast: true,
  position: "top-end",
  showConfirmButton: false,
  timer: 3000,
  timerProgressBar: true,
  background: "#1f2937", // Color de tu cts-card (slate-800)
  color: "#f3f4f6",
  didOpen: (toast) => {
    toast.addEventListener("mouseenter", Swal.stopTimer);
    toast.addEventListener("mouseleave", Swal.resumeTimer);
  },
});

// Función para alertas grandes de éxito/error
function notify(titulo, mensaje, icono = "success") {
  Swal.fire({
    title: titulo,
    text: mensaje,
    icon: icono,
    background: "#1f2937",
    color: "#f3f4f6",
    confirmButtonColor: "#10b981", // Verde esmeralda
    confirmButtonText: "Entendido",
  });
}

function getWebviewApi() {
  if (window.pywebview && window.pywebview.api) {
    return window.pywebview.api;
  }
  if (typeof pywebview !== "undefined" && pywebview.api) {
    return pywebview.api;
  }
  return null;
}

// Variable global para las extensiones
let extensionesSeleccionadas = [];
let currentView = 'dashboard';
const categoriasSeleccionadas = new Set();

const etiquetasExtensiones = {
  docs: "Documentos",
  imgs: "Imágenes",
  videos: "Videos",
  audio: "Audio",
  compressed: "Comprimidos",
  prog: "Programas",
};

const ext_tag = {
  docs: ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.odt', '.ods', '.odp', '.rtf', '.csv', '.md', '.html', '.htm', '.xml', '.json', '.log'],
  imgs: ['.jpg', '.png', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.heic', '.ico', '.psd'],
  videos: ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', '.m4v'],
  audio: ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
  compressed: ['.zip', '.rar', '.7z', '.tar', '.gz', '.tar.gz', '.tgz', '.bz2', '.xz', '.iso'],
  prog: ['.exe', '.msi', '.bat', '.apk', '.jar'],
};

const stateExtBadge = {
  docs: false,  imgs: false,
  videos: false,  audio: false,
  compressed: false,  prog: false,
};



function selectBadgeExtraccion (id_section, id) {
  const button = document.getElementById(id);

  let id_ext_tag;
  let color_badge;

  if (id.includes('extraccion')) {

    id_ext_tag = id.replace('extraccion-', '');
    color_badge = "extraction";

  }else if (id.includes('extension')) {

    id_ext_tag = id.replace('extension-', '');
    color_badge = "extension";

  }else{  id_ext_tag = id; }

  const lista = ext_tag[id_ext_tag] || [];

  const bgColor = {
    extraction: "bg-purple-800",
    extension: "bg-indigo-800"
  };

  const borderColor = {
    extraction: "border-purple-400",
    extension: "border-indigo-400"
  };

  
  const updateSelectedDisplay = () => {
    const display = document.querySelector(`#${id_section} .display-selected`);
    if (!display) return;
    if (extensionesSeleccionadas.length === 0) {
      display.innerText = 'Ninguna categoría seleccionada';
    } else {
      display.innerText = 'Filtros activos: ' + Array.from(categoriasSeleccionadas)
        .map((cat) => etiquetasExtensiones[cat])
        .join(', ');
    }
  };


  if (button.classList.contains('btn-outline-secondary')) {
    categoriasSeleccionadas.add(id_ext_tag);

    button.classList.add(`active-badge`);
    button.classList.remove('btn-outline-secondary');    
    
    extensionesSeleccionadas = [...new Set([...extensionesSeleccionadas, ...lista.map((ext) => ext.toLowerCase())])];

    Toast.fire({ icon: 'success', title: `Filtro ${etiquetasExtensiones[id_ext_tag]} activado` });
    
  } else {
    categoriasSeleccionadas.delete(id_ext_tag);
    
    button.classList.remove(`active-badge`);
    button.classList.add('btn-outline-secondary');
    stateExtBadge.extraccion = false;
    extensionesSeleccionadas = extensionesSeleccionadas.filter((ext) => !lista.includes(ext));
    Toast.fire({ icon: 'info', title: `Filtro ${etiquetasExtensiones[id_ext_tag]} desactivado` });

  }

  updateSelectedDisplay();
  const input = id_section.includes('extraccion') ? 'custom-extensions-extraccion' : 'custom-extensions';
  document.getElementById(input).value = extensionesSeleccionadas.join(', ');
}

function limpiaTags (idSection) {

  categoriasSeleccionadas.clear();

  const display = document.querySelector(`#${idSection} .display-selected`);
  if (!display) return;
  display.innerText = 'Ninguna categoría seleccionada';
  
  const limpiarInput = (idSection) => {
    const inputs = document.querySelectorAll(`#${idSection} input`);
    inputs.forEach((input) => {
      if (input.type === "text"){
        input.value = '';
      }else{
        input.checked = false;
      }
    });

  };

  const limpiarButton = (idSection) => {
    const bgColor = idSection == "view-avanzado" ? "bg-indigo-800" : "bg-purple-800";
    const borderColor = idSection == "view-avanzado" ? "border-indigo-400" : "border-purple-400";
    
    const buttons = document.querySelectorAll(`#${idSection} .ext-badge`);
    buttons.forEach((btn) => {
      btn.classList.remove(`${bgColor}`, `${borderColor}`);
      btn.classList.add('bg-gray-800', 'border-gray-600');

    });
  };

  switch (idSection) {
    case "view-avanzado":
      limpiarInput("view-avanzado");
      limpiarButton("view-avanzado");
      break;
    case "view-extraccion":
      limpiarButton("view-extraccion");
      limpiarInput("view-extraccion");
      break;
    case "view-multimedia":
      limpiarInput("view-multimedia");
      break;
  }

}


function $$ready(fn) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fn);
  } else {
    fn();
  }
}

$$ready(() => {
  const inputRuta = document.getElementById("input-ruta");
  if (inputRuta) {
    inputRuta.addEventListener("focus", seleccionarCarpetaUI);
  }
});

async function seleccionarCarpetaUI() {
  const api = getWebviewApi();
  if (!api) {
    Toast.fire({
      icon: 'error',
      title: 'El puente Python no está disponible aún',
    });
    return;
  }

  try {
    const ruta = await api.seleccionar_carpeta();
    const inputRuta = document.getElementById("input-ruta");

    if (inputRuta && ruta) {
      inputRuta.value = ruta;
      Toast.fire({
        icon: "info",
        title: "Carpeta vinculada correctamente",
      });
    } else if (!ruta) {
      Toast.fire({
        icon: "warning",
        title: "No se seleccionó ninguna carpeta",
      });
    }
  } catch (err) {
    console.error("Error en seleccionarCarpetaUI:", err);
    Toast.fire({
      icon: 'error',
      title: 'No se pudo abrir el selector de carpetas',
    });
  }
}

// Función genérica para ejecutar módulos
async function ejecutarModulo(tipo) {
  const inputRuta = document.getElementById("input-ruta");

  if (!inputRuta || !inputRuta.value) {
    notify(
      "¡Atención!",
      "Por favor, selecciona una carpeta antes de continuar.",
      "warning",
    );
    return;
  }

  const ruta = inputRuta.value;
  let config = { ruta: ruta };

  if (tipo === "avanzado") {
    const extensiones = document.getElementById("custom-extensions").value;
    let folderName = document.getElementById("custom-folder-name").value.trim();

    if (!extensiones) {
      notify(
        "¡Atención!",
        "Selecciona al menos una categoría antes de ejecutar el modo avanzado.",
        "warning",
      );
      return;
    }

    if (!folderName) {
      const categorias = Array.from(categoriasSeleccionadas);
      if (categorias.length === 1) {
        folderName = etiquetasExtensiones[categorias[0]] || "Personalizado";
      } else if (categorias.length > 1) {
        folderName = categorias
          .map((cat) => etiquetasExtensiones[cat] || cat)
          .join("_");
      } else {
        folderName = "Personalizado";
      }
    }

    config.extensiones = extensiones;
    config.folderName = folderName;
    config.sortByDate = document.getElementById("sort-by-date2").checked;
  }

  if (tipo === "inteligente") {
    // Para orden inteligente, capturar las opciones de los checkboxes
    config.includeSubfolders = document.getElementById("inteligente-include-subfolders").checked;
    config.sortByDate = document.getElementById("inteligente-sort-by-date").checked;
  }

  if (tipo === "extraccion") {
    // Para orden de extraccion, capturar las opciones de los checkboxes
    let folderName = document.getElementById("custom-folder-name-ext").value.trim();
    const extensiones = document.getElementById("custom-extensions-extraccion").value;

    config.extensiones = extensiones;
    config.folderName = folderName;
    config.create_carpet_type = document.getElementById("create-carpet-type").checked;
    config.delete_carpet = document.getElementById("delete-carpet").checked;
    config.mode_simulation = document.getElementById("mode-simulation").checked;
    config.sort_by_date = document.getElementById("sort-by-date").checked;
  }


  // Modal de carga (Loader)
  let modalTitle = "Procesando archivos...";
  let modalText = "Por favor espera un momento.";
  if (tipo === "limpieza") {
    modalTitle = "Escaneando duplicados...";
    modalText = "Analizando archivos y eliminando duplicados. Esto puede tardar.";
  }
  Swal.fire({
    title: modalTitle,
    text: modalText,
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
    background: "#1f2937",
    color: "#f3f4f6",
  });

  try {
    const response = await pywebview.api.ejecutar_accion(tipo, config);

    if (tipo !== "limpieza") {
      // Cerramos el loader y mostramos el éxito
      Swal.close();
    }

    Toast.fire({
      icon: "success",
      title: response,
    });
  } catch (err) {
    Swal.close();
    notify(
      "Error de Motor",
      "Hubo un problema al ejecutar la acción en Python.",
      "error",
    );
  }
}

async function undoAction() {
  // Modal de carga
  Swal.fire({
    title: "Deshaciendo acciones...",
    text: "Por favor espera un momento.",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
    background: "#1f2937",
    color: "#f3f4f6",
  });

  try {
    const response = await pywebview.api.ejecutar_accion("undo", {});

    Swal.close();

    Toast.fire({
      icon: "info",
      title: response,
    });
  } catch (err) {
    Swal.close();
    notify(
      "Error al Deshacer",
      "No se pudo deshacer la acción.",
      "error",
    );
  }
}

// Función para cambiar de vista
function showView(viewId) {
  // Ocultar todas
  document.querySelectorAll(".view").forEach((v) => v.style.display = "none"  );
  
  switch (viewId) {
    case "view-avanzado":
      limpiaTags("view-avanzado");
      break;
    case "view-extraccion":
      limpiaTags("view-extraccion");
      break;
    case "view-multimedia":
      limpiaTags("view-multimedia");
      break;
  }
  // Mostrar la elegida
  document.getElementById(viewId).style.display = "block";
  
  currentView = viewId;

  // Opcional: Cambiar estilo del botón activo en el sidebar
  // console.log("Navegando a:", viewId);
}


// Importante: Esperar a que el puente esté listo
window.addEventListener("pywebviewready", async function () {
  console.log("Puente CTS establecido");
  
  // Initial State: Verificar activación al cargar
  try {
    const estado = await pywebview.api.verificar_activacion();
    if (estado.activado) {
      // Mostrar dashboard
      document.getElementById("license-overlay").classList.add("d-none");
      console.log("Software activado - Dashboard disponible");
    } else {
      // Mostrar overlay de activación
      document.getElementById("license-overlay").classList.remove("d-none");
      document.getElementById("hwid-display").value = estado.hwid;
      console.log("Software no activado - Mostrando overlay");
    }
  } catch (error) {
    console.error("Error verificando activación:", error);
    // En caso de error, mostrar overlay por seguridad
    document.getElementById("license-overlay").classList.remove("d-none");
  }
});

async function llamarPython() {
  // pywebview.api mapea directamente a la clase CTSBridge en Python
  try {
    const result = await pywebview.api.seleccionar_carpeta();
    if (result) {
      alert("Carpeta seleccionada: " + result);
    }
  } catch (err) {
    console.error("Error llamando a Python:", err);
  }
}

async function validarLicenciaUI() {
  const key = document.getElementById("input-key").value.trim();
  
  if (!key) {
    notify("Error", "Por favor ingresa una key válida", "error");
    return;
  }

  try {
    const resultado = await pywebview.api.intentar_activacion(key);
    
    if (resultado.exito) {
      notify("¡Éxito!", resultado.mensaje, "success");
      // Ocultar overlay y mostrar dashboard
      document.getElementById("license-overlay").classList.add("hidden");
    } else {
      notify("Error", resultado.mensaje, "error");
    }
  } catch (error) {
    console.error("Error activando:", error);
    notify("Error", "Hubo un problema al activar el software", "error");
  }
}

function copiarHWID() {
  const hwid = document.getElementById("hwid-display").value;
  navigator.clipboard.writeText(hwid).then(() => {
    Toast.fire({
      icon: "success",
      title: "HWID copiado al portapapeles"
    });
  }).catch(err => {
    console.error("Error copiando HWID:", err);
  });
}


function newTask() {
  document.getElementById('input-ruta').value = '';
  document.querySelectorAll(".view").forEach((v) => v.style.display = "none"  );
}