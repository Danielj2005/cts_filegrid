const Toast = Swal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
  timer: 2500,
  timerProgressBar: true,
  background: '#1f2937',
  color: '#f3f4f6',
  didOpen: (toast) => {
    toast.addEventListener('mouseenter', Swal.stopTimer);
    toast.addEventListener('mouseleave', Swal.resumeTimer);
  },
});

async function generarKey() {
  const hwid = document.getElementById('hwid-input').value.trim();
  if (!hwid) {
    Toast.fire({ icon: 'warning', title: 'Ingresa el HWID antes de generar.' });
    return;
  }

  try {
    const response = await fetch('generate.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hwid }),
    });

    const data = await response.json();

    if (data && data.key) {
      document.getElementById('key-output').value = data.key;
      Toast.fire({ icon: 'success', title: 'Key generada con éxito.' });
    } else {
      Toast.fire({ icon: 'error', title: data.error || 'Error generando la key.' });
    }
  } catch (error) {
    console.error('Error generando key:', error);
    Toast.fire({ icon: 'error', title: 'No se pudo conectar con el servidor PHP.' });
  }
}

function copiarKey() {
  const output = document.getElementById('key-output');
  const key = output.value.trim();
  if (!key) {
    Toast.fire({ icon: 'warning', title: 'No hay key para copiar.' });
    return;
  }

  navigator.clipboard.writeText(key)
    .then(() => {
      Toast.fire({ icon: 'success', title: 'Key copiada al portapapeles.' });
    })
    .catch((error) => {
      console.error('Error copiando key:', error);
      Toast.fire({ icon: 'error', title: 'No se pudo copiar la key.' });
    });
}

document.getElementById('generate-button').addEventListener('click', generarKey);
document.getElementById('copy-button').addEventListener('click', copiarKey);
