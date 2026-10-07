#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "DHT.h"

// =====================================================
// WIFI
// =====================================================

const char* WIFI_SSID = "DESKTOP-TQCKBGG 5736";
const char* WIFI_PASSWORD = "Cq0[8081";

// =====================================================
// MQTT
// =====================================================

const char* MQTT_SERVER = "10.99.175.39";
const int MQTT_PORT = 1883;

const char* MQTT_TOPIC = "sentinel-x/telemetry";

const char* DEVICE_ID = "SENTINEL-X-01";

// =====================================================
// OLED
// =====================================================

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

#define OLED_SDA 21
#define OLED_SCL 22

Adafruit_SSD1306 display(
  SCREEN_WIDTH,
  SCREEN_HEIGHT,
  &Wire,
  -1
);

// =====================================================
// DHT22
// =====================================================

#define DHT_PIN 4
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);

// =====================================================
// PIR HC-SR501
// =====================================================

#define PIR_PIN 27

// =====================================================
// MQTT / WIFI CLIENT
// =====================================================

WiFiClient espClient;

PubSubClient mqttClient(espClient);

// =====================================================
// VARIABLES
// =====================================================

float temperature = 0.0;
float humidity = 0.0;

bool motion = false;

// MQ-2 pas encore installé
int gas = 0;

unsigned long lastPublish = 0;

const unsigned long PUBLISH_INTERVAL = 2000;

// =====================================================
// CONNEXION WIFI
// =====================================================

void connectWiFi() {

  Serial.println();
  Serial.println("================================");
  Serial.println("CONNEXION WIFI");
  Serial.println("================================");

  Serial.print("[WiFi] Réseau : ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);

  WiFi.begin(
    WIFI_SSID,
    WIFI_PASSWORD
  );

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);

    Serial.print(".");

    attempts++;

    if (attempts >= 60) {

      Serial.println();
      Serial.println("[WiFi] Échec de connexion.");

      ESP.restart();
    }
  }

  Serial.println();
  Serial.println("[WiFi] Connecté !");
  
  Serial.print("[WiFi] Adresse IP ESP32 : ");
  Serial.println(WiFi.localIP());

  Serial.print("[WiFi] Passerelle : ");
  Serial.println(WiFi.gatewayIP());

  Serial.print("[WiFi] Masque : ");
  Serial.println(WiFi.subnetMask());

  Serial.println();
}

// =====================================================
// TEST TCP PORT 1883
// =====================================================

bool testMQTTPort() {

  Serial.println();
  Serial.println("================================");
  Serial.println("TEST TCP MQTT");
  Serial.println("================================");

  Serial.print("[TCP] Connexion vers ");
  Serial.print(MQTT_SERVER);
  Serial.print(":");
  Serial.println(MQTT_PORT);

  WiFiClient testClient;

  bool result = testClient.connect(
    MQTT_SERVER,
    MQTT_PORT
  );

  if (result) {

    Serial.println();
    Serial.println("[TCP] SUCCES !");
    Serial.println("[TCP] PORT 1883 ACCESSIBLE");

    testClient.stop();

    Serial.println("================================");
    Serial.println();

    return true;
  }

  Serial.println();
  Serial.println("[TCP] ECHEC !");
  Serial.println("[TCP] PORT 1883 INACCESSIBLE");

  testClient.stop();

  Serial.println("================================");
  Serial.println();

  return false;
}

// =====================================================
// CONNEXION MQTT
// =====================================================

void connectMQTT() {

  if (mqttClient.connected()) {
    return;
  }

  Serial.println();
  Serial.println("================================");
  Serial.println("CONNEXION MQTT");
  Serial.println("================================");

  Serial.print("[MQTT] Serveur : ");
  Serial.print(MQTT_SERVER);
  Serial.print(":");
  Serial.println(MQTT_PORT);

  while (!mqttClient.connected()) {

    Serial.println("[MQTT] Connexion au broker...");

    String clientId =
      String(DEVICE_ID) +
      "-" +
      String((uint32_t)ESP.getEfuseMac(), HEX);

    bool connected = mqttClient.connect(
      clientId.c_str()
    );

    if (connected) {

      Serial.println();
      Serial.println("[MQTT] CONNECTÉ !");
      Serial.print("[MQTT] Client ID : ");
      Serial.println(clientId);

      Serial.print("[MQTT] Topic : ");
      Serial.println(MQTT_TOPIC);

      Serial.println("================================");
      Serial.println();

      break;
    }

    Serial.print("[MQTT] Échec, code=");
    Serial.println(mqttClient.state());

    Serial.println("[MQTT] Nouvelle tentative dans 3 secondes...");

    delay(3000);
  }
}

// =====================================================
// LECTURE DES CAPTEURS
// =====================================================

void readSensors() {

  // ---------------------------------------------------
  // DHT22
  // ---------------------------------------------------

  float newTemperature = dht.readTemperature();

  float newHumidity = dht.readHumidity();

  if (!isnan(newTemperature)) {

    temperature = newTemperature;
  }

  if (!isnan(newHumidity)) {

    humidity = newHumidity;
  }

  // ---------------------------------------------------
  // PIR
  // ---------------------------------------------------

  motion = digitalRead(PIR_PIN) == HIGH;

  // ---------------------------------------------------
  // GAS
  // ---------------------------------------------------

  // MQ-2 pas encore installé.
  // On conserve volontairement 0.
  gas = 0;
}

// =====================================================
// AFFICHAGE OLED
// =====================================================

void updateOLED() {

  display.clearDisplay();

  display.setTextColor(SSD1306_WHITE);

  // ---------------------------------------------------
  // TITRE
  // ---------------------------------------------------

  display.setTextSize(1);

  display.setCursor(25, 0);

  display.println("SENTINEL-X");

  // ---------------------------------------------------
  // TEMPERATURE
  // ---------------------------------------------------

  display.setTextSize(2);

  display.setCursor(0, 15);

  display.print("T:");

  display.print(
    temperature,
    1
  );

  display.println(" C");

  // ---------------------------------------------------
  // HUMIDITE
  // ---------------------------------------------------

  display.setTextSize(1);

  display.setCursor(0, 39);

  display.print("Humidite: ");

  display.print(
    humidity,
    1
  );

  display.println(" %");

  // ---------------------------------------------------
  // MOUVEMENT
  // ---------------------------------------------------

  display.setCursor(0, 53);

  display.print("Mouvement: ");

  if (motion) {

    display.println("OUI");

  } else {

    display.println("NON");
  }

  display.display();
}

// =====================================================
// PUBLICATION MQTT
// =====================================================

void publishTelemetry() {

  if (!mqttClient.connected()) {

    Serial.println(
      "[MQTT] Non connecté, publication impossible."
    );

    return;
  }

  // ---------------------------------------------------
  // JSON
  // ---------------------------------------------------

  String payload = "{";

  payload += "\"device_id\":\"";
  payload += DEVICE_ID;
  payload += "\",";

  payload += "\"temperature\":";
  payload += String(
    temperature,
    1
  );

  payload += ",";

  payload += "\"humidity\":";
  payload += String(
    humidity,
    1
  );

  payload += ",";

  payload += "\"motion\":";

  if (motion) {
    payload += "true";
  } else {
    payload += "false";
  }

  payload += ",";

  payload += "\"gas\":";
  payload += String(gas);

  payload += "}";

  // ---------------------------------------------------
  // AFFICHAGE SERIAL
  // ---------------------------------------------------

  Serial.println();
  Serial.println("[MQTT] Publication telemetry");

  Serial.print("[MQTT] Topic : ");
  Serial.println(MQTT_TOPIC);

  Serial.print("[MQTT] Payload : ");
  Serial.println(payload);

  // ---------------------------------------------------
  // PUBLICATION
  // ---------------------------------------------------

  bool result = mqttClient.publish(
    MQTT_TOPIC,
    payload.c_str()
  );

  if (result) {

    Serial.println(
      "[MQTT] Publication réussie !"
    );

  } else {

    Serial.println(
      "[MQTT] ERREUR publication."
    );
  }
}

// =====================================================
// SETUP
// =====================================================

void setup() {

  Serial.begin(115200);

  delay(1000);

  Serial.println();
  Serial.println();
  Serial.println("================================");
  Serial.println("       SENTINEL-X ESP32");
  Serial.println("================================");
  Serial.println("DHT22 + PIR + OLED + MQTT");
  Serial.println("================================");

  // ===================================================
  // OLED
  // ===================================================

  Wire.begin(
    OLED_SDA,
    OLED_SCL
  );

  if (!display.begin(
        SSD1306_SWITCHCAPVCC,
        0x3C
      )) {

    Serial.println(
      "[OLED] OLED non détecté !"
    );

    while (true) {
      delay(1000);
    }
  }

  Serial.println(
    "[OLED] OLED détecté."
  );

  // ===================================================
  // DHT
  // ===================================================

  dht.begin();

  Serial.println(
    "[DHT] DHT22 initialisé."
  );

  // ===================================================
  // PIR
  // ===================================================

  pinMode(
    PIR_PIN,
    INPUT
  );

  Serial.println(
    "[PIR] PIR initialisé."
  );

  // ===================================================
  // OLED STARTUP
  // ===================================================

  display.clearDisplay();

  display.setTextColor(
    SSD1306_WHITE
  );

  display.setTextSize(2);

  display.setCursor(18, 10);

  display.println("SENTINEL");

  display.setTextSize(1);

  display.setCursor(35, 38);

  display.println("Initialisation");

  display.display();

  delay(2000);

  // ===================================================
  // WIFI
  // ===================================================

  connectWiFi();

  // ===================================================
  // CONFIG MQTT
  // ===================================================

  mqttClient.setServer(
    MQTT_SERVER,
    MQTT_PORT
  );

  Serial.println(
    "[MQTT] Configuration terminée."
  );

  // ===================================================
  // TEST TCP
  // ===================================================

  bool tcpOK = testMQTTPort();

  if (!tcpOK) {

    Serial.println();
    Serial.println(
      "[ERREUR] ESP32 ne peut pas atteindre"
    );

    Serial.println(
      "[ERREUR] le port MQTT 1883."
    );

    Serial.println(
      "[ERREUR] Vérifier réseau/firewall/broker."
    );

    Serial.println();
  }

  // ===================================================
  // MQTT
  // ===================================================

  connectMQTT();

  // ===================================================
  // LECTURE INITIALE
  // ===================================================

  readSensors();

  updateOLED();

  // ===================================================
  // MESSAGE FINAL
  // ===================================================

  Serial.println();
  Serial.println("================================");
  Serial.println("ESP32 SENTINEL-X PRET");
  Serial.println("================================");
  Serial.println();

}

// =====================================================
// LOOP
// =====================================================

void loop() {

  // ===================================================
  // WIFI
  // ===================================================

  if (WiFi.status() != WL_CONNECTED) {

    Serial.println(
      "[WiFi] Connexion perdue."
    );

    connectWiFi();
  }

  // ===================================================
  // MQTT
  // ===================================================

  if (!mqttClient.connected()) {

    connectMQTT();
  }

  mqttClient.loop();

  // ===================================================
  // LECTURE CAPTEURS
  // ===================================================

  readSensors();

  // ===================================================
  // OLED
  // ===================================================

  updateOLED();

  // ===================================================
  // MQTT TELEMETRY
  // ===================================================

  unsigned long now = millis();

  if (
    now - lastPublish >=
    PUBLISH_INTERVAL
  ) {

    lastPublish = now;

    publishTelemetry();
  }

  delay(100);
}