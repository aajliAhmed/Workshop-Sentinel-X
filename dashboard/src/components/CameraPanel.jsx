import {
  Camera,
  ScanFace,
  CircleAlert,
  ShieldCheck,
} from "lucide-react";

export default function CameraPanel({
  securityAlert = null,
}) {

  const cameraUrl =
    "http://localhost:8000/api/v1/camera/stream";

  const intrusionDetected =
    securityAlert?.event === "PERSON_DETECTED";

  return (
    <section className="camera-panel">

      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <div className="camera-panel-header">

        <div>
          <h2>AI Vision</h2>

          <div className="camera-subtitle">
            Local computer vision monitoring
          </div>
        </div>

        <div className="ai-ready">
          <span className="status-dot" />
          AI READY
        </div>

      </div>


      {/* ================================================= */}
      {/* CAMERA */}
      {/* ================================================= */}

      <div className="camera-container">

        <div className="camera-topbar">

          <div className="camera-name">

            <Camera size={17} />

            <span>
              UGREEN CAMERA
            </span>

          </div>


          <div className="yolo-status">

            <ScanFace size={16} />

            <span>
              YOLOv8n
            </span>

            <span className="active-label">
              ACTIVE
            </span>

          </div>

        </div>


        {/* ================================================= */}
        {/* VIDEO */}
        {/* ================================================= */}

        <div className="camera-video-wrapper">

          <img
            src={cameraUrl}
            alt="UGREEN camera with YOLOv8n detection"
            className="camera-stream"
          />


          {/* =============================================== */}
          {/* LIVE INDICATOR */}
          {/* =============================================== */}

          <div className="live-indicator">

            <span className="live-dot" />

            LIVE

          </div>


          {/* =============================================== */}
          {/* SECURITY STATUS */}
          {/* =============================================== */}

          <div
            className={
              intrusionDetected
                ? "detection-status danger"
                : "detection-status safe"
            }
          >

            {intrusionDetected ? (
              <>
                <CircleAlert size={18} />

                <span>
                  INTRUSION DETECTED
                </span>
              </>
            ) : (
              <>
                <ShieldCheck size={18} />

              </>
            )}

          </div>

        </div>


        {/* ================================================= */}
        {/* AI DATA BAR */}
        {/* ================================================= */}


      </div>

    </section>
  );
}