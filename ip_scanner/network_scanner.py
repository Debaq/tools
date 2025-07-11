#!/usr/bin/env python3
import subprocess
import re
import requests
import json
import time
import sys
import argparse
import os
from datetime import datetime

# Variables globales
PHP_URL = None
REFRESH_INTERVAL = 10  # minutos por defecto
MAC_TO_NAME = {}  # Se cargará desde JSON

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

def load_devices_config(config_file):
    """Carga la configuración de dispositivos desde archivo JSON"""
    try:
        if not os.path.exists(config_file):
            print(f"❌ Error: Archivo de configuración no encontrado: {config_file}")
            sys.exit(1)
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'devices' not in config:
            print(f"❌ Error: El archivo {config_file} debe contener un objeto 'devices'")
            sys.exit(1)
        
        devices = config['devices']
        if not devices:
            print(f"❌ Error: No se encontraron dispositivos en {config_file}")
            sys.exit(1)
        
        # Convertir MACs a minúsculas para consistencia
        normalized_devices = {}
        for mac, name in devices.items():
            normalized_devices[mac.lower()] = name
        
        print(f"✅ Configuración cargada: {len(normalized_devices)} dispositivos desde {config_file}")
        for mac, name in normalized_devices.items():
            print(f"  📱 {name} - {mac}")
        
        return normalized_devices
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: JSON inválido en {config_file}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error leyendo {config_file}: {e}")
        sys.exit(1)
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
        
        print(f"Enviando datos: {json.dumps(data, indent=2)}")
        
        response = requests.post(PHP_URL, json=data, timeout=10)
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Datos enviados exitosamente:")
            print(f"   - Dispositivos: {response_data.get('devices_count', 'N/A')}")
            print(f"   - Bytes escritos: {response_data.get('bytes_written', 'N/A')}")
            print(f"   - Archivo: {response_data.get('file_path', 'N/A')}")
        else:
            print(f"❌ Error enviando datos: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado en send_to_php: {e}")

def main():
    """Función principal que ejecuta el escaneo según el intervalo especificado"""
    global PHP_URL, REFRESH_INTERVAL, MAC_TO_NAME
    
    # Configurar argumentos
    parser = argparse.ArgumentParser(
        description='Monitor de dispositivos de red que envía datos a PHP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Ejemplos:
  python3 network_scanner.py http://midominio.com/monitor/ devices.json
  python3 network_scanner.py http://192.168.1.100/php/ devices.json -t 5
  python3 network_scanner.py https://localhost/test/ devices.json -t 0.5'''
    )
    
    parser.add_argument('url', 
                       help='URL de la carpeta donde está receiver.php (ej: http://midominio.com/monitor/)')
    
    parser.add_argument('config', 
                       help='Archivo JSON con configuración de dispositivos (ej: devices.json)')
    
    parser.add_argument('-t', '--time', 
                       type=float, 
                       default=10,
                       help='Intervalo de refresco en minutos (default: 10, acepta decimales como 0.5)')
    
    args = parser.parse_args()
    
    # Validar intervalo
    if args.time <= 0:
        print("❌ Error: El tiempo debe ser mayor a 0")
        sys.exit(1)
    
    # Cargar configuración de dispositivos
    MAC_TO_NAME = load_devices_config(args.config)
    
    # Configurar variables globales
    base_url = args.url.rstrip('/')  # Quitar / final si existe
    PHP_URL = f"{base_url}/receiver.php"
    REFRESH_INTERVAL = args.time
    
    # Calcular segundos para sleep
    sleep_seconds = int(REFRESH_INTERVAL * 60)
    
    print("-" * 60)
    print("🚀 Iniciando monitor de red...")
    print(f"📡 Escaneando dispositivos cada {REFRESH_INTERVAL} minutos")
    print(f"🌐 Enviando datos a: {PHP_URL}")
    print(f"📱 Monitoreando {len(MAC_TO_NAME)} dispositivos configurados")
    print("-" * 60)
    
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Escaneando red...")
            devices = scan_network()
            
            if devices:
                print(f"✅ Dispositivos encontrados: {len(devices)}")
                for device in devices:
                    print(f"  📟 {device['name']} ({device['ip']}) - {device['mac']}")
                
                send_to_php(devices)
            else:
                print("⚠️  No se encontraron dispositivos conocidos")
                # Enviar lista vacía para actualizar timestamp
                send_to_php([])
            
            print(f"⏰ Esperando {REFRESH_INTERVAL} minutos para el próximo escaneo...")
            time.sleep(sleep_seconds)
            
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo monitor...")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            time.sleep(60)  # Esperar 1 minuto antes de reintentar

if __name__ == "__main__":
    main()