# Projeto Verao Nokia 5110

Monitor de hardware (CPU/GPU/RAM/VRAM) com ESP32 e display Nokia 5110 (PCD8544), usando FreeRTOS.

## Visao Geral

Versao aprimorada do Projeto Verao com display Nokia 5110, exibindo mais metricas:

1. **Firmware ESP32** (`ProjetoVeraoNokia.ino`) - Le dados via serial JSON e exibe no Nokia 5110
2. **Python Monitor** (`monitor.pyw`) - Le sensores via LibreHardwareMonitor (.NET) e envia via serial

## Hardware

- ESP32
- Display Nokia 5110 (PCD8544, SPI)
- Potenciometro para contraste (conectado ao ADC)

## Pinos ESP32

| Sinal   | GPIO |
|---------|------|
| LCD_CLK | 14   |
| LCD_DIN | 25   |
| LCD_DC  | 26   |
| LCD_CE  | 13   |
| LCD_RST | 27   |
| ADC_PIN | 34   |

## Firmware

### Tarecas FreeRTOS

- `lcdTask` - Atualiza display a cada 1s com CPU, GPU, RAM e VRAM
- `serialReadTask` - Parse JSON recebido via serial

### Display

```
CPU  45%  62C
RAM  8192MB
--------------------
GPU  80%  71C
VRAM 4096MB
```

### Protocolo JSON

Recebe via Serial (115200 baud):

```json
{"CT":62,"CU":45,"GT":71,"GU":80,"RM":8192,"VM":4096}
```

| Campo | Descricao |
|-------|-----------|
| CT    | CPU Temperature (C) |
| CU    | CPU Usage (%) |
| GT    | GPU Temperature (C) |
| GU    | GPU Usage (%) |
| RM    | RAM Used (MB) |
| VM    | VRAM Used (MB) |

### Build

1. Abra `ProjetoVeraoNokia.ino` no Arduino IDE
2. Instale as bibliotecas: `Adafruit_GFX`, `Adafruit_PCD8544`, `ArduinoJson`
3. Selecione a board ESP32
4. Faca upload via USB

## Python Monitor

Le sensores de hardware usando LibreHardwareMonitor (.NET via pythonnet) e envia via serial.

### Requisitos

- Windows
- Python 3.x (64-bit para compatibilidade com .NET)

### Instalacao

```bash
pip install pyserial pythonnet
```

### Uso

```bash
python monitor.pyw
```

O script detecta automaticamente o ESP32 pela porta serial (CH340, CP210x, UART).

> **Nota:** Execute como Administrador para acesso completo aos sensores de hardware.

## Dependencias

### Firmware
- `Adafruit_GFX`
- `Adafruit_PCD8544`
- `ArduinoJson`
- `Preferences` (ESP32 NVS)

### Python
- `pyserial>=3.5`
- `pythonnet` (para `clr` e LibreHardwareMonitor)
- LibreHardwareMonitor .NET DLLs (incluidas em `LibreHardwareMonitor.NET.10/`)
