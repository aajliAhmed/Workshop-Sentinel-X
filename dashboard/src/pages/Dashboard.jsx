import { useEffect, useState } from "react";

import Header from "../components/Header";
import SensorCard from "../components/SensorCard";
import SensorChart from "../components/SensorChart";
import SystemStatus from "../components/SystemStatus";
import AlertPanel from "../components/AlertPanel";
import CameraPanel from "../components/CameraPanel";
import ControlPanel from "../components/ControlPanel";

import {
  initialHistory,
  initialAlerts,
} from "../data/mockData";

import { useTelemetry } from "../hooks/useTelemetry";


export default function Dashboard() {

  // =========================================
  // TELEMETRY
  // =========================================

  const {
    telemetry,
    connected,
    isMock,
  } = useTelemetry();


  // =========================================
  // HISTORIQUE DES MESURES
  // =========================================

  const [history, setHistory] =
    useState(initialHistory);


  // =========================================
  // ALERTES
  // =========================================

  const [alerts, setAlerts] =
    useState(initialAlerts);


  // =========================================
  // AJOUT D'UN POINT AU GRAPHIQUE
  // =========================================

  useEffect(() => {

    if (
      telemetry.temperature === null ||
      telemetry.humidity === null ||
      telemetry.gas === null
    ) {
      return;
    }


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


  // =========================================
  // TEST ALARME
  // =========================================

  const handleAlarm = () => {

    const newAlert = {

      id: Date.now(),

      type: "WARNING",

      title: "Manual alarm test",

      message: isMock
        ? "Alarm simulated from dashboard"
        : "Alarm command sent to ESP32",

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


  // =========================================
  // TEST LED
  // =========================================

  const handleLed = () => {

    const newAlert = {

      id: Date.now(),

      type: "INFO",

      title: "LED command",

      message: isMock
        ? "LED command simulated"
        : "LED command sent to ESP32",

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


  // =========================================
  // RESET
  // =========================================

  const handleReset = () => {

    setAlerts([]);

  };


  // =========================================
  // INTERFACE
  // =========================================

  return (

    <main className="dashboard">


      {/* HEADER */}

      <Header
        connected={connected}
      />


      {/* ================================
          SENSOR CARDS
      ================================= */}

      <section className="sensor-grid">


        <SensorCard
          type="temperature"
          title="Temperature"
          value={
            telemetry.temperature
          }
          unit="°C"
        />


        <SensorCard
          type="humidity"
          title="Humidity"
          value={
            telemetry.humidity
          }
          unit="%"
        />


        <SensorCard
          type="gas"
          title="Gas / Smoke"
          value={
            telemetry.gas
          }
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


      {/* ================================
          GRAPHIQUES
      ================================= */}

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


      {/* ================================
          STATUS + CAMERA
      ================================= */}

      <section className="content-grid">


        <SystemStatus
          esp32={
            telemetry.esp32
          }

          mqtt={
            telemetry.mqtt
          }

          server={
            telemetry.server
          }
        />


        <CameraPanel />

      </section>


      {/* ================================
          ALERTS + COMMANDES
      ================================= */}

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