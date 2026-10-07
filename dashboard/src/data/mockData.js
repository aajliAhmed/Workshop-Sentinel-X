export const initialTelemetry = {
  deviceId: "SENTINEL-X-01",

  temperature: null,
  humidity: null,

  // MQ-2 non installé pour le moment
  gas: 0,

  motion: false,

  esp32: false,
  mqtt: false,
  server: false,

  timestamp: null,
};

export const initialHistory = [];

export const initialAlerts = [
  {
    id: 1,
    type: "INFO",
    title: "System started",
    message: "SENTINEL-X is operational",
    time: "10:25:12",
  },
];