<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Archivo donde se guardarán los datos
$dataFile = 'devices.json';

// Manejar solicitudes OPTIONS para CORS
if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    exit(0);
}

// Procesar datos POST del Python
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    
    if ($data && isset($data['devices'])) {
        // Preparar datos para guardar
        $saveData = array(
            'devices' => $data['devices'],
            'last_scan' => $data['scan_time'],
            'updated_at' => date('Y-m-d H:i:s')
        );
        
        // Guardar en archivo JSON
        if (file_put_contents($dataFile, json_encode($saveData, JSON_PRETTY_PRINT))) {
            echo json_encode(['status' => 'success', 'message' => 'Datos guardados correctamente']);
        } else {
            http_response_code(500);
            echo json_encode(['status' => 'error', 'message' => 'Error al guardar datos']);
        }
    } else {
        http_response_code(400);
        echo json_encode(['status' => 'error', 'message' => 'Datos inválidos']);
    }
}

// Procesar solicitudes GET para leer datos
elseif ($_SERVER['REQUEST_METHOD'] == 'GET') {
    if (file_exists($dataFile)) {
        $data = file_get_contents($dataFile);
        $jsonData = json_decode($data, true);
        
        if ($jsonData) {
            echo json_encode($jsonData);
        } else {
            echo json_encode(['devices' => [], 'last_scan' => null, 'updated_at' => null]);
        }
    } else {
        echo json_encode(['devices' => [], 'last_scan' => null, 'updated_at' => null]);
    }
}

else {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'Método no permitido']);
}
?>