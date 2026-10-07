#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

// Paramètres Wi-Fi de l'école / table
const char* ssid = "WIFI_SSID_DIAL_MD RASSA";
const char* password = "WIFI_PASSWORD_DIAL_MDRASSA";

// Adresse IP du PC Serveur Local et port MQTT TLS
const char* mqtt_server = "10.60.92.203";
const int mqtt_port = 8883;

// Identifiants MQTT
const char* mqtt_user = "sentinel";
const char* mqtt_pass = "Khalid130322";

WiFiClientSecure espClient;
PubSubClient client(espClient);

// Certificat de l'Autorité de Certification (CA) au format PEM
// (Remplace par le contenu de ton fichier ca.crt généré sur le serveur)
const char* root_ca = \
"-----BEGIN CERTIFICATE-----\n" \
"MIIDXzCCAkegAwIBAgIUGJ154lsmHA3Mb3iq8hPcdYit210wDQYJKoZIhvcNAQEL\n" \
"BQAwczELMAkGA1UEBhMCRlIxDDAKBgNVBAgMA05BUTERMA8GA1UEBwwITWVyaWdu\n" \
"YWMxEzARBgNVBAoMClNlbnRpbmVsLVgxFjAUBgNVBAsMDUN5YmVyc2VjdXJpdHkx\n" \
"FjAUBgNVBAMMDVNlbnRpbmVsLVgtQ0EwHhcNMjYxMDA2MTAxMDE3WhcNMjcxMDA2\n" \
"MTAxMDE3WjBzMQswCQYDVQQGEwJGUjEMMAoGA1UECAwDTkFRMREwDwYDVQQHDAhN\n" \
"ZXJpZ25hYzETMBEGA1UECgwKU2VudGluZWwtWDEWMBQGA1UECwwNQ3liZXJzZWN1\n" \
"cml0eTESMBAGA1UEAwwJU2VudGluZWwtWC1DQTCCASIwDQYJKoZIhvcNAQEBBQAD\n" \
"ggEPADCCAQOCggEBAL8wK3oM0tL3Z3N7H3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3\n" \
"G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3\n" \
"G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3\n" \
"G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3\n" \
"G3s6F2f3G3s6F2f3G3s6F2f3G3s6F2f3CAwEAAaNTMFEwHQYDVR0OBBYEFHaxHvOd\n" \
"elO/6bk5ZEhm5uhRT8hlMB8GA1UdIwQYMBaAFHaxHvOdelO/6bk5ZEhm5uhRT8hl\n" \
"MA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAE9H143... (remplacer par ca.crt)\n" \
"-----END CERTIFICATE-----\n";

void setup_wifi() {
  delay(10);
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP8266Client", mqtt_user, mqtt_pass)) {
      client.subscribe("sentinel/command");
    } else {
      delay(5000);
    }
  }
}

void setup() {
  setup_wifi();
  // Configurer le certificat CA pour sécuriser TLS sur ESP8266
  espClient.setTrustAnchors(new X509List(root_ca));
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
