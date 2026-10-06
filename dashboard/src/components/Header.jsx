import { ShieldCheck, Wifi } from "lucide-react";

export default function Header({ connected }) {
  return (
    <header className="dashboard-header">

      <div className="brand">
        <div className="brand-icon">
          <ShieldCheck size={30} />
        </div>

        <div>
          <h1>SENTINEL-X</h1>
          <p>AetherCorp Industrial Security</p>
        </div>
      </div>

      <div className="header-right">

        <div className="connection">
          <Wifi size={18} />

          <span className={connected ? "online" : "offline"}>
            {connected ? "CONNECTED" : "DISCONNECTED"}
          </span>
        </div>

        <div className="system-status">
          <span
            className={`status-dot ${
              connected ? "online-dot" : "offline-dot"
            }`}
          />

          {connected
            ? "SYSTEM OPERATIONAL"
            : "SYSTEM OFFLINE"}
        </div>

      </div>

    </header>
  );
}