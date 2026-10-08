import {
  Cpu,
  Radio,
  Server,
} from "lucide-react";

function StatusRow({
  icon: Icon,
  name,
  online,
}) {

  return (
    <div className="status-row">

      <div className="status-name">

        <Icon size={20} />

        <span>
          {name}
        </span>

      </div>

      <span
        className={
          online
            ? "status-online"
            : "status-offline"
        }
      >
        ● {online ? "ONLINE" : "OFFLINE"}
      </span>

    </div>
  );
}

export default function SystemStatus({
  esp32,
  mqtt,
  server,
}) {

  return (
    <div className="panel">

      <div className="panel-header">

        <h2>System Status</h2>

        <span className="panel-subtitle">
          Infrastructure
        </span>

      </div>

      <div className="status-list">

        <StatusRow
          icon={Cpu}
          name="ESP32"
          online={true}
        />

        <StatusRow
          icon={Radio}
          name="MQTT Broker"
          online={mqtt}
        />

        <StatusRow
          icon={Server}
          name="Local Server"
          online={server}
        />

      </div>

    </div>
  );
}