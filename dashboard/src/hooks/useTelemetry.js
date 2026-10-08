import { useEffect, useState } from "react";

import {
  initialTelemetry,
} from "../data/mockData";

import {
  connectWebSocket,
} from "../services/websocket";


const USE_MOCK =
  import.meta.env.VITE_USE_MOCK !== "false";


export function useTelemetry() {

  const [telemetry, setTelemetry] =
    useState(initialTelemetry);

  const [connected, setConnected] =
    useState(initialTelemetry.esp32);

  const [securityAlert, setSecurityAlert] =
    useState(null);


  /*
   * =====================================================
   * MODE MOCK
   * =====================================================
   */

  useEffect(() => {

    if (!USE_MOCK) {
      return;
    }

    console.log("[Telemetry] MOCK MODE");

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

          esp32: true,
          mqtt: true,
          server: true,
        };
      });

    }, 2000);


    return () => {
      clearInterval(interval);
    };

  }, []);


  /*
   * =====================================================
   * MODE REAL
   * =====================================================
   */

  useEffect(() => {

    if (USE_MOCK) {
      return;
    }

    console.log("[Telemetry] REAL MODE");

    const socket =
      connectWebSocket(

        (data) => {

          /*
           * -------------------------
           * TELEMETRY
           * -------------------------
           */

          if (data.type === "telemetry") {

            setTelemetry(previous => ({
              ...previous,
              ...data.data,
              server: true,
              mqtt: true,
            }));

            return;
          }


          /*
           * -------------------------
           * SECURITY ALERT
           * -------------------------
           */

          if (data.type === "security_alert") {

            console.log(
              "[Telemetry] Security alert received:",
              data.data
            );

            setSecurityAlert(data.data);

            return;
          }

        },

        (status) => {

          setConnected(status);

        }

      );


    return () => {
      socket.close();
    };

  }, []);


  return {
    telemetry,
    connected,
    securityAlert,
    isMock: USE_MOCK,
  };
}