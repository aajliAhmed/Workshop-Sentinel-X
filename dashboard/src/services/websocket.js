export function connectWebSocket(
  onMessage,
  onStatusChange
) {
  const url =
    import.meta.env.VITE_WS_URL ||
    "ws://localhost:8000/ws/telemetry";

  console.log("[WebSocket] Connecting to:", url);

  const socket = new WebSocket(url);

  socket.onopen = () => {
    console.log("[WebSocket] Connected");
    onStatusChange(true);
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);

      console.log("[WebSocket] Telemetry:", data);

      onMessage(data);
    } catch (error) {
      console.error(
        "[WebSocket] Invalid JSON:",
        error
      );
    }
  };

  socket.onerror = (error) => {
    console.error(
      "[WebSocket] Error:",
      error
    );

    onStatusChange(false);
  };

  socket.onclose = () => {
    console.log("[WebSocket] Disconnected");
    onStatusChange(false);
  };

  return socket;
}