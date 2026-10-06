export const initialTelemetry = {
  deviceId: "SENTINEL-X-01",

  temperature: 27.4,
  humidity: 51.2,
  gas: 312,
  motion: false,

  esp32: true,
  mqtt: true,
  server: true,

  timestamp: Date.now(),
};

export const initialHistory = [
  {
    time: "10:00",
    temperature: 25.1,
    humidity: 48,
    gas: 280,
  },
  {
    time: "10:05",
    temperature: 25.8,
    humidity: 49,
    gas: 291,
  },
  {
    time: "10:10",
    temperature: 26.2,
    humidity: 50,
    gas: 295,
  },
  {
    time: "10:15",
    temperature: 26.7,
    humidity: 50,
    gas: 301,
  },
  {
    time: "10:20",
    temperature: 27.1,
    humidity: 51,
    gas: 305,
  },
  {
    time: "10:25",
    temperature: 27.4,
    humidity: 51,
    gas: 312,
  },
];

export const initialAlerts = [
  {
    id: 1,
    type: "INFO",
    title: "System started",
    message: "SENTINEL-X is operational",
    time: "10:25:12",
  },
];