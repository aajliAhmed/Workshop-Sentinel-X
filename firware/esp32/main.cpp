#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "DHT.h"

// =========================
// OLED
// =========================
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

// =========================
// DHT22
// =========================
#define DHTPIN 4
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

// =========================
// PIR
// =========================
#define PIR_PIN 27

// Variables
float temperature = NAN;
float humidite = NAN;

unsigned long dernierDHT = 0;
unsigned long dernierAffichage = 0;

// Lecture DHT toutes les 2 secondes
const unsigned long INTERVALLE_DHT = 2000;


void setup() {

  Serial.begin(115200);

  // OLED
  Wire.begin(OLED_SDA, OLED_SCL);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED non detecte !");
    while (true);
  }

  // DHT
  dht.begin();

  // PIR
  pinMode(PIR_PIN, INPUT);

  // Message de démarrage
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  display.setTextSize(2);
  display.setCursor(18, 10);
  display.println("Bonjour");

  display.setTextSize(1);
  display.setCursor(20, 40);
  display.println("Demarrage...");

  display.display();

  Serial.println("ESP32 + DHT22 + OLED + PIR");

  // Petit temps de stabilisation
  delay(5000);

  Serial.println("PIR actif !");
}


void loop() {

  // =========================
  // PIR
  // =========================

  int mouvement = digitalRead(PIR_PIN);

  // Détection immédiate
  if (mouvement == HIGH) {
    Serial.println(">>> MOUVEMENT DETECTE !");
  }


  // =========================
  // DHT22
  // =========================

  if (millis() - dernierDHT >= INTERVALLE_DHT) {

    dernierDHT = millis();

    float nouvelleTemperature = dht.readTemperature();
    float nouvelleHumidite = dht.readHumidity();

    if (!isnan(nouvelleTemperature) && !isnan(nouvelleHumidite)) {

      temperature = nouvelleTemperature;
      humidite = nouvelleHumidite;

    } else {

      Serial.println("Erreur DHT22 !");
    }
  }


  // =========================
  // OLED
  // =========================

  if (millis() - dernierAffichage >= 200) {

    dernierAffichage = millis();

    display.clearDisplay();
    display.setTextColor(SSD1306_WHITE);

    // Titre
    display.setTextSize(1);
    display.setCursor(25, 0);
    display.println("STATION ESP32");

    // Temperature
    display.setTextSize(2);
    display.setCursor(0, 15);

    if (isnan(temperature)) {
      display.println("T: ERR");
    } else {
      display.print("T:");
      display.print(temperature, 1);
      display.println(" C");
    }

    // Humidité
    display.setTextSize(1);
    display.setCursor(0, 40);

    if (isnan(humidite)) {
      display.println("Humidite: ERR");
    } else {
      display.print("Humidite: ");
      display.print(humidite, 1);
      display.println(" %");
    }

    // Mouvement
    display.setCursor(0, 54);

    if (mouvement == HIGH) {
      display.println("MOUVEMENT: OUI");
    } else {
      display.println("MOUVEMENT: NON");
    }

    display.display();
  }
}
