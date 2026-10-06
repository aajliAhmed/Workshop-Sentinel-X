import {
  Thermometer,
  Droplets,
  Wind,
  Activity,
} from "lucide-react";

const icons = {
  temperature: Thermometer,
  humidity: Droplets,
  gas: Wind,
  motion: Activity,
};

export default function SensorCard({
  type,
  title,
  value,
  unit,
  status = "NORMAL",
}) {

  const Icon = icons[type];

  const isAlert = status === "ALERT";

  return (
    <div className={`sensor-card ${isAlert ? "sensor-alert" : ""}`}>

      <div className="sensor-card-top">

        <div>

          <p className="sensor-title">
            {title}
          </p>

          <div className="sensor-value">

            {value}

            {unit && (
              <span className="sensor-unit">
                {unit}
              </span>
            )}

          </div>

        </div>

        <div className="sensor-icon">
          <Icon size={24} />
        </div>

      </div>

      <div
        className={`sensor-status ${
          isAlert ? "alert" : "normal"
        }`}
      >
        ● {status}
      </div>

    </div>
  );
}