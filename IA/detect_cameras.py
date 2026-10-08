import cv2

for index in range(5):
    camera = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    if camera.isOpened():
        print(f"Caméra trouvée à l'index {index}")

        ret, frame = camera.read()

        if ret:
            print(f"  → Image récupérée : {frame.shape}")
        else:
            print("  → Caméra ouverte mais aucune image récupérée.")

        camera.release()
    else:
        print(f"Aucune caméra à l'index {index}")