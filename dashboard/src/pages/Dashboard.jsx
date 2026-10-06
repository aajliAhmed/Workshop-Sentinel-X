import { useEffect, useState } from "react";

import Header from "../components/Header";
import SensorCard from "../components/SensorCard";
import SensorChart from "../components/SensorChart";
import SystemStatus from "../components/SystemStatus";
import AlertPanel from "../components/AlertPanel";
import CameraPanel from "../components/CameraPanel";
import ControlPanel from "../components/ControlPanel";

import {
  initialTelemetry,
  initialHistory,
  initialAlerts,
} from "../data/mockData";

export default function Dashboard() {

  const [telemetry, setTelemetry] =
    useState(initialTelemetry);

  const [history, setHistory] =
    useState(initialHistory);

  const [alerts, setAlerts] =
    useState(initialAlerts);

  /*
   * Simulation temporaire des données ESP32.
   *
   * Plus tard cette partie sera remplacée
   * par la réception WebSocket du backend.
   */

  useEffect(() => {

    const interval = setInterval(() => {

      setTelemetry((previous) => {

        const newTemperature =
          Number(
            (
              previous.temperature +
              (Math.random() - 0.5) * 0.6
            ).toFixed(1)
          );

        const newHumidity =
          Number(
            (
              previous.humidity +
              (Math.random() - 0.5) * 0.8
            ).toFixed(1)
          );

        const newGas =
          Math.max(
            0,
            Math.round(
              previous.gas +
              (Math.random() - 0.5) * 12
            )
          );

        const newMotion =
          Math.random() > 0.85;

        return {
          ...previous,

          temperature: newTemperature,
          humidity: newHumidity,
          gas: newGas,
          motion: newMotion,

          timestamp: Date.now(),
        };

      });

    }, 2000);

    return () => {
      clearInterval(interval);
    };

  }, []);


  /*
   * Mise à jour de l'historique
   */

  useEffect(() => {

    setHistory((previous) => {

      const now = new Date();

      const time =
        now.toLocaleTimeString(
          "fr-FR",
          {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
          }
        );

      const newPoint = {
        time,

        temperature:
          telemetry.temperature,

        humidity:
          telemetry.humidity,

        gas:
          telemetry.gas,
      };

      return [
        ...previous.slice(-11),
        newPoint,
      ];

    });

  }, [
    telemetry.temperature,
    telemetry.humidity,
    telemetry.gas,
  ]);


  /*
   * Commandes
   */

  const handleAlarm = () => {

    const newAlert = {
      id: Date.now(),

      type: "WARNING",

      title: "Manual alarm test",

      message:
        "Alarm command triggered from dashboard",

      time:
        new Date().toLocaleTimeString(
          "fr-FR"
        ),
    };

    setAlerts((previous) => [
      newAlert,
      ...previous,
    ]);

  };


  const handleLed = () => {

    const newAlert = {
      id: Date.now(),

      type: "INFO",

      title: "LED command",

      message:
        "LED command sent to ESP32",

      time:
        new Date().toLocaleTimeString(
          "fr-FR"
        ),
    };

    setAlerts((previous) => [
      newAlert,
      ...previous,
    ]);

  };


  const handleReset = () => {

    setAlerts([]);

  };


  return (

    <main className="dashboard">

      <Header
        connected={telemetry.esp32}
      />


      {/* SENSOR CARDS */}

      <section className="sensor-grid">

        <SensorCard
          type="temperature"
          title="Temperature"
          value={telemetry.temperature}
          unit="°C"
        />

        <SensorCard
          type="humidity"
          title="Humidity"
          value={telemetry.humidity}
          unit="%"
        />

        <SensorCard
          type="gas"
          title="Gas / Smoke"
          value={telemetry.gas}
          unit="ppm"
        />

        <SensorCard
          type="motion"
          title="Motion"
          value={
            telemetry.motion
              ? "YES"
              : "NO"
          }
          unit=""
          status={
            telemetry.motion
              ? "ALERT"
              : "NORMAL"
          }
        />

      </section>


      {/* CHARTS */}

      <section className="charts-grid">

        <div className="panel">

          <SensorChart
            title="Temperature"
            data={history}
            dataKey="temperature"
            unit="°C"
          />

        </div>

        <div className="panel">

          <SensorChart
            title="Gas / Smoke"
            data={history}
            dataKey="gas"
            unit="ppm"
          />

        </div>

      </section>


      {/* SECOND ROW */}

      <section className="content-grid">

        <SystemStatus
          esp32={telemetry.esp32}
          mqtt={telemetry.mqtt}
          server={telemetry.server}
        />

        <CameraPanel />

      </section>


      {/* THIRD ROW */}

      <section className="content-grid">

        <AlertPanel
          alerts={alerts}
        />

        <ControlPanel
          onAlarm={handleAlarm}
          onLed={handleLed}
          onReset={handleReset}
        />

      </section>

    </main>

  );
}