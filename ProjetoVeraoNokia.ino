#include "config.h"
#include <ArduinoJson.h>
#include <Preferences.h>
#include <Adafruit_GFX.h>
#include <Adafruit_PCD8544.h>

//==== Process Variables ====
volatile uint8_t cpuTemperature = 0u;
volatile uint8_t cpuUse = 0u;
volatile uint8_t gpuTemperature = 0u;
volatile uint8_t gpuUse = 0u;
volatile uint16_t ramUse = 0u;
volatile uint16_t vramUse = 0u;

//==== Program Tasks ====
void lcdTask(void *vParameters);
void serialReadTask(void *vParameters);

void 
setup()
{
    xTaskCreate(lcdTask, "lcd controller", 8192, NULL, 1, NULL);
    xTaskCreate(serialReadTask, "process serial commands", 8192, NULL, 1, NULL);
}

void 
loop()
{
}

// CLK, DIN, DC, CE, RST
Adafruit_PCD8544 lcd = Adafruit_PCD8544(LCD_CLK, LCD_DIN, LCD_DC, LCD_CE, LCD_RST);

void 
lcdTask(void *vParameters) 
{
    lcd.begin();
    lcd.setTextSize(1);
    lcd.setTextColor(BLACK);

    for (;;) 
    {
        lcd.setContrast(map(analogRead(ADC_PIN), 0, 4095, 0, 100));
        lcd.clearDisplay();
        // --- SEÇÃO CPU ---
        lcd.setCursor(0, 0);
        lcd.print("CPU "); 
        lcd.printf("%3d%% ", cpuUse);
        lcd.printf("%3dC ", cpuTemperature);

        // --- SEÇÃO RAM ---
        lcd.setCursor(0, 10);
        lcd.print("RAM ");
        lcd.printf("%5dMB ", ramUse);

        // Linha central decorativa
        lcd.drawFastHLine(0, 20, 84, BLACK);

        // --- SEÇÃO GPU ---
        lcd.setCursor(0, 24);
        lcd.print("GPU ");
        lcd.printf("%3d%% ", gpuUse);
        lcd.printf("%3dC ", gpuTemperature);

        // --- SEÇÃO VRAM ---
        lcd.setCursor(0, 34);
        lcd.print("VRAM ");
        lcd.printf("%5dMB ", vramUse);

        lcd.display();
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void
serialReadTask(void *vParameters)
{
    uint8_t serial_buf[SERIAL_BUF_SIZE];

    Serial.begin(115200);

    // Tamanho do documento JSON (pode ser pequeno para esses 4 valores)
    // Use https://arduinojson.org/v7/assistant/ para calcular se o JSON crescer
    JsonDocument doc;

    for (;;)
    {
        if (Serial.available() > 0) 
        {
            // Lê a string até o caractere de nova linha
            String input = Serial.readStringUntil('\n');

            // Tenta decodificar o JSON recebido
            DeserializationError error = deserializeJson(doc, input);

            if (!error)
            {
                // Sucesso! Atualiza as variáveis globais
                // O ArduinoJson faz o cast automático para uint8_t
                cpuTemperature = doc["CT"];
                cpuUse         = doc["CU"];
                gpuTemperature = doc["GT"];
                gpuUse         = doc["GU"];
                ramUse         = doc["RM"];
                vramUse        = doc["VM"];
            }
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

