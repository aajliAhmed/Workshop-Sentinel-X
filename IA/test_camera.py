import cv2

def find_camera():
    for index in range(5):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()

            if ret:
                print(f"[INFO] Caméra trouvée sur l'index {index}")
                return index

    return None

camera_index = find_camera()

if camera_index is None:
    print("[ERREUR] Aucune caméra trouvée.")
    exit()

cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("ERREUR : caméra impossible à ouvrir")
    exit()

print("Caméra ouverte.")
print("Appuie sur Q pour quitter.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("ERREUR : aucune image reçue")
        break

    cv2.imshow("TEST UGREEN", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()