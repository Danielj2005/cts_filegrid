<!DOCTYPE html>
<html lang="es" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CTS Key Generator - Web Privado</title>
  <link rel="icon" type="image/x-icon" href="assets/img/logo.ico" />
  <link rel="stylesheet" href="assets/css/sweetalert2.min.css" />
  <link rel="stylesheet" href="assets/css/toastify.css" />
  <link rel="stylesheet" href="assets/css/app.css" />
  <script src="assets/js/sweetalert2.min.js"></script>
  <script src="assets/js/toastify.js"></script>
</head>
<body class="app-shell">
  <div class="app-container">
    <div class="card-stack">
      <section class="card card-primary">
        <div class="card-header">
          <img src="assets/img/logo.png" alt="CTS Logo" class="logo" />
          <div>
            <h1 class="title">Generador de Keys CTS</h1>
            <p class="subtitle">Interfaz web privada con generación de licencias en PHP.</p>
          </div>
        </div>

        <div class="form-grid">
          <div class="field">
            <label class="field-label">HWID del cliente</label>
            <input id="hwid-input" type="text" placeholder="Pega el HWID aquí" class="field-input" />
          </div>

          <button id="generate-button" class="button button-primary">GENERAR KEY</button>

          <div class="field">
            <label class="field-label">Key generada</label>
            <div class="output-row">
              <input id="key-output" type="text" readonly class="field-input output-input" placeholder="Aquí aparecerá la key" />
              <button id="copy-button" class="button button-secondary">
                <img style="margin-right: .4rem; " src="./assets/img/copy-plus.svg" alt="Copy icon" class="text-gray-400 group-hover:scale-110 transition-transform">
                &nbsp;COPIAR
              </button>
            </div>
          </div>

          <p class="hint">La key se genera usando el HWID + el salt privado de CTS. Úsala en el sistema de activación.</p>
        </div>
      </section>
    </div>
  </div>

  <script src="assets/js/keygen.js"></script>
</body>
</html>
