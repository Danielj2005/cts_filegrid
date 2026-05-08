

const Toast = Swal.mixin({
  toast: true,
  position: "top-end",
  showConfirmButton: false,
  timer: 3000,
  timerProgressBar: true,
  background: "#1f2937", // Color de tu cts-card (slate-800)
  color: "#f3f4f6",
  didOpen: (toast) => {
    const progressBar = toast.querySelector('.swal2-timer-progress-bar');
    if (progressBar) {
        progressBar.style.backgroundColor = '#10b981'; // Verde esmeralda
    }
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


const idSections = {
  delete: "view-eliminacion",
  extract: "view-extraccion",
  multimedia: "view-multimedia",
  dash: "view-dashboard",
  clean: "view-limpieza"
};

const idSectionsContainerCategories = {
  delete: `#containerCategoriesDelete`,
  extract: `#containerCategoriesExtract`,
  advanced: `#containerCategoriesAdvanced`,
  multimedia: ""
};

const idBadges = {
  delete: "eliminacion-",
  extract: "extraccion-",
  advanced: "extension-",
  multimedia: ""
};
const idContainerExtensions = {
  extract: "custom-extensions-extraccion",
  advanced: "custom-extensions",
  delete: "custom-eliminacion",
  multimedia: ""
};

function selectBadges (action, id) {

  const button = document.getElementById(idBadges[action] + id);
  const lista = ext_tag[id] || [];
  
  const updateSelectedDisplay = (key) => {
    const display = document.querySelector(idSectionsContainerCategories[key]);
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
    categoriasSeleccionadas.add(id);

    button.classList.add(`active-badge`);
    button.classList.remove('btn-outline-secondary');

    extensionesSeleccionadas = [...new Set([...extensionesSeleccionadas, ...lista.map((ext) => ext.toLowerCase())])];
    
    Toast.fire({ icon: 'success', title: `Filtro ${etiquetasExtensiones[id]} activado` });
    
  } else {
    categoriasSeleccionadas.delete(id);
    
    button.classList.remove(`active-badge`);
    button.classList.add('btn-outline-secondary');
    extensionesSeleccionadas = extensionesSeleccionadas.filter((ext) => !lista.includes(ext));
    Toast.fire({ icon: 'info', title: `Filtro ${etiquetasExtensiones[id]} desactivado` });

  }

  updateSelectedDisplay(action);
  document.getElementById(idContainerExtensions[action]).value = extensionesSeleccionadas.join(', ');
}

function limpiaTags (action) {
  categoriasSeleccionadas.clear();
  const display = document.querySelectorAll('div .display-selected');
  if (!display) return;

  display.forEach((d) => {
    d.innerText = 'Ninguna categoría seleccionada';
  });

  const limpiarInput = () => {
    const inputs1 = document.querySelectorAll('div .cleanInput');

    inputs1.forEach((input) => {
      if (input.type === "text"){
        input.value = '';
      }else{
        input.checked = false;
      }
    });
  };

  const limpiarButton = (btn) => {
    const buttons = document.querySelectorAll('div .ext-badge');

    buttons.forEach((btn) => {
      btn.classList.remove(`active-badge`);
      btn.classList.add('btn-outline-secondary');
    });
  };
  
  if (action) {
    limpiarInput();
    limpiarButton();
  }else{
    limpiarInput();
  }
}


document.addEventListener('DOMContentLoaded', () => {
  document.getElementById("input-ruta").addEventListener("click", seleccionarCarpetaUI);

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
    const extensiones = document.getElementById("custom-extensions").value.trim();
    let folderName = document.getElementById("custom-folder-name").value.trim();
    const includeSubfolders = document.getElementById("inteligente-include-subfolders").checked;
    const sortByDate = document.getElementById("sort-by-date2").checked;

    const categorias = Array.from(categoriasSeleccionadas);
    const usarOrdenAutomatico = extensiones.length === 0;

    if (!folderName) {
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
    config.sortByDate = document.getElementById("inteligente-sort-by-date").checked;
    config.includeSubfolders = includeSubfolders;
    config.useAutomaticCategories = usarOrdenAutomatico;
  }

  if (tipo === "eliminacion") {
    const extensiones = document.getElementById("custom-eliminacion").value;

    if (!extensiones) {
      notify(
        "¡Atención!",
        "Selecciona al menos una categoría antes de ejecutar la eliminación.",
        "warning",
      );
      return;
    }

    config.extensiones = extensiones;
    config.include_subfolders = document.getElementById("eliminacion-include-subfolders").checked;
    config.delete_source_folders = document.getElementById("eliminar-carpet").checked;
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
  document.querySelectorAll(".view").forEach((v) => v.style.display = "none" );
  
  if (viewId !== "dash" || viewId !== "clean" || viweId !== "multimedia") {
    limpiaTags(true);

  }else{
    limpiaTags(false);
  }

  // Mostrar la elegida
  document.getElementById(idSections[viewId]).style.display = "block";
  
  currentView = idSections[viewId];

  // Opcional: Cambiar estilo del botón activo en el sidebar
  // console.log("Navegando a:", viewId);
}


// Importante: Esperar a que el puente esté listo
window.addEventListener("pywebviewready", async function () {
  // console.log("Puente CTS establecido");
  
  // Initial State: Verificar activación al cargar
  try {
    const estado = await pywebview.api.verificar_activacion();
    document.getElementById("loader").classList.add("d-none");

    if (estado.activado) {
      // Mostrar dashboard
      document.getElementById("license-overlay").classList.add("d-none");
      document.getElementById("app").classList.remove("d-none");
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
      document.getElementById("license-overlay").classList.add("d-none");
      document.getElementById("app").classList.remove("d-none");
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
  document.getElementById("view-dashboard").style.display = "block";
}