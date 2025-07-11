#!/usr/bin/env python3
import subprocess
import re
import requests
import json
import time
from datetime import datetime

# Mapeo de MACs a nombres clave
MAC_TO_NAME = {
    'fc:ee:28:03:34:e2': 'K1-01',
    'fc:ee:28:04:19:79': 'K1-02',
    'fc:ee:28:03:43:6a': 'K1-03',
    '14:ab:c5:bb:b1:47': 'server'
}

# URL del PHP receptor
PHP_URL = 'http://tu-dominio.com/receiver.php'  # Cambiar por tu URL real

def scan_network():
    """Escanea la red local usando arp-scan"""
    try:
        # Ejecutar arp-scan en la red local
        result = subprocess.run(['arp-scan', '-l'], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"Error ejecutando arp-scan: {result.stderr}")
            return []
        
        devices = []
        lines = result.stdout.split('\n')
        
        for line in lines:
            # Buscar líneas con formato IP MAC
            match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9:]{17})', line)
            if match:
                ip = match.group(1)
                mac = match.group(2).lower()
                
                # Verificar si la MAC está en nuestro mapeo
                if mac in MAC_TO_NAME:
                    devices.append({
                        'ip': ip,
                        'mac': mac,
                        'name': MAC_TO_NAME[mac],
                        'timestamp': datetime.now().isoformat()
                    })
        
        return devices
        
    except subprocess.TimeoutExpired:
        print("Timeout ejecutando arp-scan")
        return []
    except Exception as e:
        print(f"Error en scan_network: {e}")
        return []

def send_to_php(devices):
    """Envía los dispositivos encontrados al PHP"""
    try:
        data = {
            'devices': devices,
            'scan_time': datetime.now().isoformat()
        }
        
        response = requests.post(PHP_URL, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"Datos enviados exitosamente: {len(devices)} dispositivos")
        else:
            print(f"Error enviando datos: HTTP {response.status_code}")
            
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")

def main():
    """Función principal que ejecuta el escaneo cada 10 minutos"""
    print("Iniciando monitor de red...")
    print(f"Escaneando dispositivos cada 10 minutos...")
    print(f"Enviando datos a: {PHP_URL}")
    
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Escaneando red...")
            devices = scan_network()
            
            if devices:
                print(f"Dispositivos encontrados: {len(devices)}")
                for device in devices:
                    print(f"  - {device['name']} ({device['ip']}) - {device['mac']}")
                
                send_to_php(devices)
            else:
                print("No se encontraron dispositivos conocidos")
                # Enviar lista vacía para actualizar timestamp
                send_to_php([])
            
            print("Esperando 10 minutos para el próximo escaneo...")
            time.sleep(600)  # 10 minutos
            
        except KeyboardInterrupt:
            print("\nDeteniendo monitor...")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")
            time.sleep(60)  # Esperar 1 minuto antes de reintentar

if __name__ == "__main__":
    main()