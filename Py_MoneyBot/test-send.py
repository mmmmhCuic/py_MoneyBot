from tiktok_uploader.upload import upload_video
from tiktok_uploader.auth import AuthBackend

# Chemin de la vidéo que vous souhaitez publier
video_path = 'dos_vid_tiktok/part/part_1.mp4'

# Description de votre vidéo (optionnel)
description = 'Ceci est ma vidéo géniale !'

# Publier la vidéo

upload_video(video_path, description=description, cookies='cookies.txt')
