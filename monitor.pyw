import sys
import os
import time
import json
import serial
import serial.tools.list_ports
import clr # Biblioteca pythonnet

# ====================================================================
# CONFIGURAÇÃO DO CAMINHO DA DLL
script_dir = os.path.dirname(os.path.abspath(__file__))
dll_dir = os.path.join(script_dir, "LibreHardwareMonitor.NET.10")

# ESSENCIAL: Adiciona a pasta da DLL aos caminhos do sistema.
# Sem isso, a DLL principal não consegue carregar as outras DLLs auxiliares.
sys.path.append(dll_dir)

dll_path = os.path.join(dll_dir, "LibreHardwareMonitorLib.dll")

try:
    clr.AddReference(dll_path)
except Exception as e:
    print(f"Erro ao carregar a DLL no caminho: {dll_path}")
    print(f"Detalhe do erro: {e}")
    sys.exit(1)
# ====================================================================

# Agora o Python conseguirá ler o namespace corretamente!
from LibreHardwareMonitor import Hardware

def connect_esp32():
    """ Procura automaticamente a porta COM do ESP32 """
    print("Procurando ESP32...")
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Verifica descrições comuns de chips USB-Serial usados em ESP32
        if "CH340" in port.description or "CP210" in port.description or "UART" in port.description:
            print(f"ESP32 encontrado na porta: {port.device}")
            try:
                # O timeout ajuda a não travar o script se a porta falhar
                return serial.Serial(port.device, 115200, timeout=1)
            except serial.SerialException:
                pass
    
    print("ESP32 não encontrado. Tentando novamente em 5s...")
    return None

def main():
    # Inicializa o monitor de hardware
    computer = Hardware.Computer()
    computer.IsCpuEnabled = True
    computer.IsGpuEnabled = True
    computer.IsMemoryEnabled = True
    
    try:
        computer.Open()
    except Exception as e:
        print("Erro ao abrir os sensores. Você executou como Administrador?")
        sys.exit(1)

    esp_serial = None

    try:
        while True:
            # Tenta conectar ou reconectar se o cabo for desconectado
            if esp_serial is None or not esp_serial.is_open:
                esp_serial = connect_esp32()
                if esp_serial is None:
                    time.sleep(5)
                    continue

            # Dicionário com os dados que vão para o ESP32 (valores iniciais)
            data = {"CT": 0, "CU": 0, "GT": 0, "GU": 0, "RM": 0, "VM": 0}

            # Lê os sensores
            for hw in computer.Hardware:
                hw.Update()
                
                # --- CPU ---
                if hw.HardwareType == Hardware.HardwareType.Cpu:
                    for sensor in hw.Sensors:
                        # Pega a temperatura do encapsulamento (Package)
                        if sensor.SensorType == Hardware.SensorType.Temperature and "Package" in sensor.Name:
                            data["CT"] = int(sensor.Value) if sensor.Value else 0
                        # Pega o uso total
                        elif sensor.SensorType == Hardware.SensorType.Load and "Total" in sensor.Name:
                            data["CU"] = int(sensor.Value) if sensor.Value else 0

                # --- MEMÓRIA RAM ---
                elif hw.HardwareType == Hardware.HardwareType.Memory:
                    for sensor in hw.Sensors:
                        if sensor.SensorType == Hardware.SensorType.Data and "Memory Used" in sensor.Name:
                            # Converte GB para MB (multiplica por 1024) para bater com a tela do LCD
                            data["RM"] = int(sensor.Value * 1024) if sensor.Value else 0

                # --- GPU ---
                elif hw.HardwareType in [Hardware.HardwareType.GpuNvidia, Hardware.HardwareType.GpuAmd]:
                    for sensor in hw.Sensors:
                        if sensor.SensorType == Hardware.SensorType.Temperature and "Core" in sensor.Name:
                            data["GT"] = int(sensor.Value) if sensor.Value else 0
                        elif sensor.SensorType == Hardware.SensorType.Load and "Core" in sensor.Name:
                            data["GU"] = int(sensor.Value) if sensor.Value else 0
                        # VRAM costuma vir no SmallData e geralmente já em MB
                        elif sensor.SensorType == Hardware.SensorType.SmallData and "Memory Used" in sensor.Name:
                            data["VM"] = int(sensor.Value) if sensor.Value else 0

            # Prepara e envia o JSON via Serial
            try:
                json_string = json.dumps(data)
                # Envia com o \n no final para o readStringUntil('\n') do ESP32 funcionar
                esp_serial.write((json_string + '\n').encode('utf-8'))
                # print(f"Enviado: {json_string}") # Remova o '#' no início desta linha para debugar no terminal
            except serial.SerialException:
                print("Conexão perdida com o ESP32!")
                esp_serial.close()
                esp_serial = None

            # Espera 1 segundo para a próxima leitura (bate com o delay do ESP32)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nEncerrando monitoramento...")
    finally:
        computer.Close()
        if esp_serial and esp_serial.is_open:
            esp_serial.close()

if __name__ == "__main__":
    main()