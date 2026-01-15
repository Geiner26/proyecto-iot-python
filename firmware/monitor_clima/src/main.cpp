#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

// ==========================================
//        CONFIGURACIÓN DE USUARIO
// ==========================================
// 1. ¿Tienes el sensor conectado? (true = NO, usa random | false = SÍ, usa DHT22)
#define MODO_SIMULACION true 

// 2. Datos de tu WiFi
const char* ssid = "HUAWEI-2.4G-R7aP"; 
const char* password = "cYn452Ep";

// 3. IP de tu computadora (mira ipconfig)
// Manten el puerto :5000 y la ruta /api/data
const char* serverUrl = "https://proyecto-iot-python.onrender.com/api/data";

// 4. Configuración del Sensor (Para cuando lo tengas)
#define DHTPIN 4     // Pin GPIO 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);
// ==========================================

void setup() {
  Serial.begin(115200);
  
  // Configuración de Hardware
  if (!MODO_SIMULACION) {
    dht.begin();
    Serial.println("Sensors DHT22 Iniciado.");
  } else {
    Serial.println("Modo SIMULACIÓN activado (Generando datos random).");
    randomSeed(analogRead(0));
  }

  // Conexión WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n¡WiFi Conectado!");
  Serial.print("IP del ESP32: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  float temperatura = 0.0;
  float humedad = 0.0;
  String modo = "";

  // --- PASO 1: OBTENER DATOS ---
  if (MODO_SIMULACION) {
    // Generar datos falsos pero realistas
    temperatura = random(2000, 3000) / 100.0; // Entre 20.00 y 30.00
    humedad = random(4000, 8000) / 100.0;     // Entre 40.00 y 80.00
    modo = "Simulado";
  } else {
    // Leer sensor real
    temperatura = dht.readTemperature();
    humedad = dht.readHumidity();
    modo = "Sensor Real";

    // Validar errores del sensor
    if (isnan(temperatura) || isnan(humedad)) {
      Serial.println("¡Error leyendo el sensor DHT!");
      return; // Intentar de nuevo
    }
  }

  // --- PASO 2: ENVIAR A PYTHON ---
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Crear JSON: {"temp": 25.5, "hum": 60.2, "modo": "Simulado"}
    String json = "{\"temp\":" + String(temperatura) + 
                  ",\"hum\":" + String(humedad) + 
                  ",\"modo\":\"" + modo + "\"}";

    int responseCode = http.POST(json);

    if (responseCode > 0) {
      Serial.printf("Enviado OK (Código %d) -> T:%.2f H:%.2f\n", responseCode, temperatura, humedad);
    } else {
      Serial.printf("Error enviando: %s\n", http.errorToString(responseCode).c_str());
    }
    http.end();
  } else {
    Serial.println("WiFi Desconectado...");
  }

  // Esperar 5 segundos
  delay(5000);
}