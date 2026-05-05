<?php
header('Content-Type: application/json; charset=utf-8');

function send_json($payload) {
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    exit;
}

$hwid = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!empty($_POST['hwid'])) {
        $hwid = trim($_POST['hwid']);
    } else {
        $data = json_decode(file_get_contents('php://input'), true);
        if (is_array($data) && isset($data['hwid'])) {
            $hwid = trim($data['hwid']);
        }
    }
}

if ($hwid === '') {
    send_json(['error' => 'Por favor envía un HWID válido.']);
}

$salt = 'CTS_PRO_2026_SECURITY_99';
$key = strtoupper(substr(md5($hwid . $salt), 0, 12));

send_json(['key' => $key]);
