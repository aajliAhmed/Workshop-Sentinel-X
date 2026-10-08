import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("[ERREUR] Impossible d'ouvrir la caméra")
    exit()

print("[OK] Caméra ouverte")

# Demande une résolution classique
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Résolution demandée : 640x480")

while True:
    ret, frame = cap.read()

    print("ret =", ret, "frame =", frame.shape if ret else None)

    if not ret or frame is None:
        print("[ERREUR] Aucune image reçue")
        continue

    cv2.imshow("TEST UGREEN", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()