from http.server import BaseHTTPRequestHandler, HTTPServer
import json


HOST = "localhost"
PORT = 8000


class FakeBackendHandler(BaseHTTPRequestHandler):

    def do_POST(self):

        # Vérifie que l'URL correspond à notre endpoint
        if self.path != "/api/v1/alerts":
            self.send_response(404)
            self.end_headers()
            return

        # Récupère la taille du contenu reçu
        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        # Lit le contenu JSON
        body = self.rfile.read(content_length)

        try:
            event = json.loads(body)

            print("\n========================================")
            print(" [BACKEND] EVENEMENT RECU")
            print("========================================")

            print(json.dumps(
                event,
                indent=4,
                ensure_ascii=False
            ))

            # Réponse HTTP 200
            response = {
                "status": "received"
            }

            response_bytes = json.dumps(response).encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json"
            )
            self.send_header(
                "Content-Length",
                str(len(response_bytes))
            )
            self.end_headers()

            self.wfile.write(response_bytes)

        except json.JSONDecodeError:

            print("[BACKEND] JSON invalide.")

            self.send_response(400)
            self.end_headers()


print("========================================")
print(" FAKE BACKEND SENTINEL-X")
print("========================================")
print(f"[BACKEND] Serveur démarré sur http://{HOST}:{PORT}")
print("[BACKEND] Endpoint : POST /api/v1/alerts")
print("[BACKEND] En attente d'événements...\n")


server = HTTPServer(
    (HOST, PORT),
    FakeBackendHandler
)

server.serve_forever()