import {
  AlertTriangle,
  Info,
  CheckCircle,
} from "lucide-react";

function getIcon(type) {

  if (type === "CRITICAL") {
    return AlertTriangle;
  }

  if (type === "WARNING") {
    return AlertTriangle;
  }

  if (type === "INFO") {
    return Info;
  }

  return CheckCircle;
}

export default function AlertPanel({ alerts }) {

  return (
    <div className="panel">

      <div className="panel-header">

        <h2>Security Alerts</h2>

        <span className="alert-count">
          {alerts.length}
        </span>

      </div>

      <div className="alerts-list">

        {alerts.length === 0 ? (

          <div className="no-alert">

            <CheckCircle size={22} />

            <span>
              No active alerts
            </span>

          </div>

        ) : (

          alerts.map((alert) => {

            const Icon = getIcon(alert.type);

            return (
              <div
                className={`alert-item ${alert.type.toLowerCase()}`}
                key={alert.id}
              >

                <div className="alert-icon">
                  <Icon size={20} />
                </div>

                <div className="alert-content">

                  <strong>
                    {alert.title}
                  </strong>

                  <p>
                    {alert.message}
                  </p>

                </div>

                <time>
                  {alert.time}
                </time>

              </div>
            );
          })

        )}

      </div>

    </div>
  );
}