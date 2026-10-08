import cv2


CAMERA_INDEX = 2
FRAME_WIDTH = 640
FRAME_HEIGHT = 480


def open_camera():
    camera = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

    if not camera.isOpened():
        raise RuntimeError(
            f"Impossible d'ouvrir la caméra à l'index {CAMERA_INDEX}."
        )

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    return camera


def read_frame(camera):
    ret, frame = camera.read()

    if not ret:
        raise RuntimeError("Impossible de récupérer une image depuis la caméra.")

    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    return frame


def release_camera(camera):
    camera.release()
    cv2.destroyAllWindows()