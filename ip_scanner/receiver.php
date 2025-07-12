<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Archivo donde se guardarán los datos
$dataFile = 'devices.json';

// Log para debug
$logFile = 'debug.log';

function writeLog($message) {
    global $logFile;
    $timestamp = date('Y-m-d H:i:s');
    file_put_contents($logFile, "[$timestamp] $message\n", FILE_APPEND);
}

// Manejar solicitudes OPTIONS para CORS
if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    exit(0);
}

// Procesar datos POST del Python
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    writeLog("POST request recibido");
    
    $input = file_get_contents('php://input');
    writeLog("Raw input: " . $input);
    
    $data = json_decode($input, true);
    writeLog("JSON decoded: " . print_r($data, true));
    
    if ($data && isset($data['devices'])) {
        writeLog("Datos válidos encontrados, " . count($data['devices']) . " dispositivos");
        
        // Preparar datos para guardar
        $saveData = array(
            'devices' => $data['devices'],
            'last_scan' => $data['scan_time'],
            'updated_at' => date('Y-m-d H:i:s')
        );
        
        writeLog("Datos preparados para guardar");
        
        // Verificar permisos de directorio
        $dir = dirname($dataFile);
        if (!is_writable($dir)) {
            writeLog("ERROR: Directorio no escribible: $dir");
            echo json_encode(['status' => 'error', 'message' => 'Directorio no escribible', 'dir' => $dir]);
            exit;
        }
        
        // Guardar en archivo JSON
        $result = file_put_contents($dataFile, json_encode($saveData, JSON_PRETTY_PRINT));
        
        if ($result !== false) {
            writeLog("Archivo guardado exitosamente, $result bytes escritos");
            echo json_encode([
                'status' => 'success', 
                'message' => 'Datos guardados correctamente',
                'bytes_written' => $result,
                'devices_count' => count($data['devices']),
                'file_path' => realpath($dataFile)
            ]);
        } else {
            $error = error_get_last();
            writeLog("ERROR al guardar archivo: " . print_r($error, true));
            http_response_code(500);
            echo json_encode([
                'status' => 'error', 
                'message' => 'Error al guardar datos',
                'error' => $error,
                'file_path' => $dataFile,
                'dir_writable' => is_writable(dirname($dataFile))
            ]);
        }
    } else {
        writeLog("ERROR: Datos inválidos - " . ($data ? "falta campo devices" : "JSON inválido"));
        http_response_code(400);
        echo json_encode([
            'status' => 'error', 
            'message' => 'Datos inválidos',
            'received_data' => $data,
            'raw_input' => $input
        ]);
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