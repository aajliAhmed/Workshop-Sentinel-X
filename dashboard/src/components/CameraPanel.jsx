import {
  Camera,
  ScanFace,
} from "lucide-react";

export default function CameraPanel() {

  return (
    <div className="panel camera-panel">

      <div className="panel-header">

        <h2>AI Vision</h2>

        <span className="ai-status">
          AI READY
        </span>

      </div>

      <div className="camera-view">

        <div className="camera-icon">
          <Camera size={42} />
        </div>

        <div className="camera-title">
          Webcam Feed
        </div>

        <div className="camera-subtitle">
          Waiting for video stream...
        </div>

        <div className="detection-badge">
          <ScanFace size={16} />
          No person detected
        </div>

      </div>

    </div>
  );
}