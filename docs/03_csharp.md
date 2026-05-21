# C# (.NET) — Práticas de Codificação

## 1. Formatação

- **Indentação:** 4 espaços, nunca tabs.
- **Chaves:** Estilo Allman (abre em linha própria).
- **Largura de linha:** 80 caracteres máximo.

```csharp
if (!isRunning)
{
    try
    {
        serialPort = new SerialPort(portName, 115200);
        serialPort.Open();
    }
    catch (Exception ex)
    {
        MessageBox.Show("Erro: " + ex.Message);
    }
}
```

## 2. Nomenclatura

| Elemento | Convenção | Exemplo |
|----------|-----------|---------|
| Namespaces | `PascalCase` | `MonitorESP32` |
| Classes | `PascalCase` | `SensorData` |
| Métodos | `PascalCase` | `ConfigurarInterface()` |
| Propriedades | `PascalCase` | `CpuUsage` |
| Parâmetros | `camelCase` | `cpuUsage` |
| Variáveis locais | `camelCase` | `dados` |
| Campos privados | `camelCase` | `serialPort` |

## 3. Using Statements

No topo, agrupados:

1. System / .NET
2. Third-party

```csharp
using System;
using System.IO.Ports;
using System.Text.Json;
using System.Threading;
using LibreHardwareMonitor.Hardware;
```

## 4. DTOs / Modelos

- Classes simples com auto-properties para serialização JSON.
- Usar `System.Text.Json`.

```csharp
public class SensorData
{
    public int CT { get; set; } // CPU Temp
    public int CU { get; set; } // CPU Usage
    public int GT { get; set; } // GPU Temp
    public int GU { get; set; } // GPU Usage
}
```

## 5. Tratamento de Recursos

- **Sempre** fechar recursos ao encerrar.
- Usar `OnFormClosing` ou `Dispose` para cleanup.

```csharp
protected override void OnFormClosing(FormClosingEventArgs e)
{
    PararMonitoramento();
    computer?.Close();
    base.OnFormClosing(e);
}
```

## 6. Comunicação Serial

- Baudrate padrão: **115200**.
- `SerialPort.WriteLine()` para enviar (adiciona `\n`).
- Detectar portas: `SerialPort.GetPortNames()`.
- Tratar desconexão com `try/catch`.

## 7. LibreHardwareMonitor

- Inicializar `Computer` com sensores habilitados.
- Chamar `hw.Update()` antes de ler cada hardware.
- Tratar `UnauthorizedAccessException` — requer admin.
- Fallback WMI para CPU temperature quando LHM falha.

```csharp
Computer computer = new Computer
{
    IsCpuEnabled = true,
    IsGpuEnabled = true,
    IsMemoryEnabled = true
};
computer.Open();
```

## 8. Tratamento de Erros

- `try/catch` em todas as operações de I/O.
- Mensagens claras ao usuário via `MessageBox`.
- Graceful shutdown em caso de erro crítico.
- Não silenciar exceções sem motivo.
