from src.camera import open_camera, read_frame, release_camera


camera = open_camera()

try:
    frame = read_frame(camera)

    print("Caméra ouverte avec succès !")
    print(f"Taille de l'image : {frame.shape}")

finally:
    release_camera(camera)