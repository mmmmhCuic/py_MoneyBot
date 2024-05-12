import os
import json
import math
from pytube import YouTube
from tiktok_uploader.upload import upload_video

# Fonction pour vérifier si un dossier existe
def verifier_dossier(nom_dossier):
    return os.path.exists(nom_dossier)

# Fonction pour créer un dossier s'il n'existe pas
def creer_dossier_si_absent(nom_dossier):
    if not verifier_dossier(nom_dossier):
        os.makedirs(nom_dossier)
        print(f"Dossier '{nom_dossier}' créé avec succès !")

# Fonction pour demander une URL YouTube à l'utilisateur
def demander_url_youtube():
    return input("Veuillez entrer l'URL de la vidéo YouTube à télécharger : ")

def enregistrer_url_youtube(url, dossier):
    # Chemin d'accès au fichier JSON pour enregistrer l'URL
    chemin_json = os.path.join(dossier, "url_youtube.json")
    # Enregistrer l'URL dans le fichier JSON
    with open(chemin_json, "w") as f:
        json.dump({"url": url}, f)
    print("URL YouTube enregistrée.")

def mettre_a_jour_url_youtube(url, dossier):
    # Chemin d'accès au fichier JSON pour mettre à jour l'URL
    chemin_json = os.path.join(dossier, "url_youtube.json")
    # Vérifier si le fichier JSON existe
    if os.path.exists(chemin_json):
        # Mettre à jour l'URL dans le fichier JSON
        with open(chemin_json, "r+") as f:
            data = json.load(f)
            data["url"] = url
            f.seek(0)
            json.dump(data, f)
            f.truncate()
            print("URL YouTube mise à jour.")
    else:
        enregistrer_url_youtube(url, dossier)

def recuperer_url_youtube(dossier):
    # Chemin d'accès au fichier JSON pour récupérer l'URL
    chemin_json = os.path.join(dossier, "url_youtube.json")
    # Vérifier si le fichier JSON existe
    if os.path.exists(chemin_json):
        # Charger l'URL depuis le fichier JSON
        with open(chemin_json, "r") as f:
            data = json.load(f)
            return data.get("url")
    else:
        return None

def telecharger_video_youtube(url, dossier):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    total_duration_seconds = yt.length
    print("Durée totale de la vidéo:", total_duration_seconds)
    mettre_a_jour_url_youtube(url, dossier)

    if stream:
        print("Stream trouvé : ", stream)
        print("Téléchargement en cours...")
        
        # Téléchargement de la vidéo complète
        chemin_fichier = stream.download(output_path=dossier, filename="video.mp4")
        print("Téléchargement terminé !")
        
        # Découpage de la vidéo en parties
        parties = decouper_video(chemin_fichier, dossier, total_duration_seconds)
        
        # Suppression de la vidéo complète
        os.remove(chemin_fichier)
        print("Vidéo complète supprimée.")
        
        # Enregistrement des informations du projet dans le fichier JSON
        enregistrer_informations_projet(yt.title, total_duration_seconds, url, parties, dossier)
        
        # Publier la première partie
        publier_partie(url, dossier, 1)
    else:
        print("Aucun stream disponible pour le téléchargement.")

def decouper_video(chemin_fichier, dossier, total_duration_seconds):
    # Utiliser la fonction diviser_en_parties pour déterminer le nombre de parties souhaitées
    parties = diviser_en_parties(total_duration_seconds)
    
    # Créer un dossier pour les parties s'il n'existe pas
    dossier_parts = os.path.join(dossier, "part")
    creer_dossier_si_absent(dossier_parts)
    
    # Calculer la durée de chaque partie
    duree_partie = total_duration_seconds / parties
    
    # Découper la vidéo en parties
    print("Découpage de la vidéo en parties...")
    for i in range(parties):
        debut_time = i * duree_partie
        fin_time = min((i + 1) * duree_partie, total_duration_seconds)  # Assurer que la dernière partie ne dépasse pas la durée totale
        
        nom_partie = os.path.join(dossier_parts, f"part_{i + 1}.mp4")
        # Utilisation de ffmpeg pour découper la vidéo
        os.system(f'ffmpeg -i "{chemin_fichier}" -ss {debut_time} -to {fin_time} -c:v copy -c:a copy "{nom_partie}"')
        print(f"Partie {i + 1} découpée avec succès.")
    
    print("Découpage terminé !")
    return parties

def diviser_en_parties(duree):
    # Calcul du nombre maximal de parties compte tenu de la durée maximale de 3 minutes par partie
    parties_max = math.ceil(duree / 180)  # Durée maximale par partie: 3 minutes = 180 secondes

    # On veut au moins 2 parties
    parties = max(2, parties_max)

    # Calcul de la durée réelle de chaque partie
    duree_partie = duree / parties

    # Vérification si la durée de chaque partie respecte les contraintes
    while duree_partie > 180 or duree_partie < 60:
        parties += 1
        duree_partie = duree / parties

    # Ajustement pour cibler une durée d'environ 70 secondes par partie
    duree_partie = duree / parties

    # Affichage des résultats
    print("Nombre de parties:", parties)
    print("Durée de chaque partie:", duree_partie, "secondes")
    return parties

def enregistrer_informations_projet(titre, duree, url, parties, dossier):
    # Créer un objet représentant le projet
    projet = {
        "titre": titre,
        "duree": duree / 60,  # Convertir la durée en minutes
        "url": url,
        "parties": parties
    }
    
    # Chemin d'accès au fichier JSON dans le dossier des vidéos TikTok
    chemin_json = os.path.join(dossier, "projets.json")
    
    # Vérifier si le fichier JSON existe déjà
    if os.path.exists(chemin_json):
        # Charger les données existantes
        with open(chemin_json, "r") as f:
            data = json.load(f)
        
        # Ajouter le nouveau projet à la liste des projets
        data.append(projet)
        
        # Écrire les données mises à jour dans le fichier JSON
        with open(chemin_json, "w") as f:
            json.dump(data, f, indent=4)
    else:
        # Créer un nouveau fichier JSON et y écrire les données
        with open(chemin_json, "w") as f:
            json.dump([projet], f, indent=4)
    
    print("Informations du projet enregistrées dans le fichier JSON.")

def publier_partie(url, dossier, partie):
    yt = YouTube(url)
    # Chemin de la vidéo de la partie à publier
    chemin_partie = os.path.join(dossier, "part", f"part_{partie}.mp4")
    if os.path.exists(chemin_partie):
        # Récupérer l'URL YouTube enregistrée
        url_youtube = recuperer_url_youtube(dossier)
        if url_youtube:
            yt = YouTube(url_youtube)
            # Utiliser le titre de la vidéo YouTube pour la description
            description = f"Partie {partie} -- {yt.title} #fyp #pourtoi"        # Publier la vidéo
            upload_video(chemin_partie, description=description, cookies='cookies.txt')
            # Supprimer la vidéo de la partie publiée
            os.remove(chemin_partie)
            print(f"Partie {partie} publiée et supprimée.")
            # Compter le nombre de parties publiées
            parties_total = recuperer_informations_projet(dossier)["parties"]
            parties_publiees = compter_parties_publiees(dossier)
        else:
            print("Aucune URL YouTube enregistrée. Veuillez télécharger une vidéo YouTube d'abord.")
    else:
        print(f"La partie {partie} n'existe pas.")

def compter_parties_publiees(dossier):
    dossier_parts = os.path.join(dossier, "part")
    if not verifier_dossier(dossier_parts):
        return 0
    else:
        fichiers = os.listdir(dossier_parts)
        return sum(1 for f in fichiers if f.startswith("part_"))



def recuperer_informations_projet(dossier):
    # Chemin d'accès au fichier JSON pour les informations du projet
    chemin_json = os.path.join(dossier, "projets.json")
    # Vérifier si le fichier JSON existe
    if os.path.exists(chemin_json):
        # Charger les données depuis le fichier JSON
        with open(chemin_json, "r") as f:
            data = json.load(f)
            # Retourner les informations du premier projet
            return data[0]
    else:
        return None

def recuperer_partie_recente(dossier):
    fichiers = os.listdir(os.path.join(dossier, "part"))
    numeros_parties = [int(f.split("_")[1].split(".")[0]) for f in fichiers if f.startswith("part_")]
    if numeros_parties:
        return min(numeros_parties)
    else:
        return None

# Nom du dossier pour les vidéos TikTok
nom_dossier = "dos_vid_tiktok"

# Vérifier si le dossier existe
creer_dossier_si_absent(nom_dossier)

# Vérifier si des fichiers existent dans le dossier des parties
dossier_parts = os.path.join(nom_dossier, "part")

if not verifier_dossier(dossier_parts):
    url_youtube = demander_url_youtube()
    telecharger_video_youtube(url_youtube, nom_dossier)
else:
    print("Des fichiers existent déjà dans le dossier. Aucun téléchargement nécessaire.")
    partie_recente = recuperer_partie_recente(nom_dossier)
    
    if partie_recente:
        print(f"La partie la plus récente est la partie {partie_recente}.")
        publier_partie(recuperer_url_youtube(nom_dossier), nom_dossier, partie_recente)
    else:
        print("Aucune partie n'a été trouvée dans le dossier.")
        url_youtube = demander_url_youtube()
        telecharger_video_youtube(url_youtube, nom_dossier)
