import {
  Bell,
  Lightbulb,
  RotateCcw,
} from "lucide-react";

export default function ControlPanel({
  onAlarm,
  onLed,
  onReset,
}) {

  return (
    <div className="panel">

      <div className="panel-header">

        <h2>Remote Control</h2>

        <span className="panel-subtitle">
          ESP32
        </span>

      </div>

      <div className="controls">

        <button
          className="control-button alarm"
          onClick={onAlarm}
        >
          <Bell size={20} />
          Test Alarm
        </button>

        <button
          className="control-button led"
          onClick={onLed}
        >
          <Lightbulb size={20} />
          Toggle LED
        </button>

        <button
          className="control-button reset"
          onClick={onReset}
        >
          <RotateCcw size={20} />
          Reset
        </button>

      </div>

    </div>
  );
}