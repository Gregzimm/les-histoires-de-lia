"""Étape 7 : Publication automatique sur YouTube, TikTok et Instagram."""

import json
import requests
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

try:
    from config import (
        YOUTUBE_CLIENT_ID,
        YOUTUBE_CLIENT_SECRET,
        YOUTUBE_REFRESH_TOKEN,
        TIKTOK_ACCESS_TOKEN,
        INSTAGRAM_ACCESS_TOKEN,
        INSTAGRAM_BUSINESS_ACCOUNT_ID,
    )
except ModuleNotFoundError:
    from scripts.config import (
        YOUTUBE_CLIENT_ID,
        YOUTUBE_CLIENT_SECRET,
        YOUTUBE_REFRESH_TOKEN,
        TIKTOK_ACCESS_TOKEN,
        INSTAGRAM_ACCESS_TOKEN,
        INSTAGRAM_BUSINESS_ACCOUNT_ID,
    )


# ========== YOUTUBE ==========

def _upload_youtube(youtube, video_path: str, title: str, description: str, tags: list, made_for_kids: bool = True) -> str:
    """Upload générique vers YouTube."""
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "24",  # Entertainment
            "defaultLanguage": "fr",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    return response["id"]


def publish_youtube(video_path: str, short_path: str, metadata: dict) -> dict:
    """Upload la vidéo longue + le Short sur YouTube."""
    creds = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET,
    )
    youtube = build("youtube", "v3", credentials=creds)

    # Vidéo longue 16:9
    long_id = _upload_youtube(
        youtube,
        video_path,
        title=metadata["youtube"]["title"],
        description=metadata["youtube"]["description"],
        tags=metadata["youtube"]["tags"],
    )
    print(f"YouTube (long) publié : https://youtube.com/watch?v={long_id}")

    # Short 9:16
    short_title = metadata["youtube"]["title"].replace(" | Histoire pour Enfants", "") + " #Shorts"
    short_description = f"#Shorts #HistoiresPourEnfants #LIA\n\n{metadata['youtube']['description']}"
    short_id = _upload_youtube(
        youtube,
        short_path,
        title=short_title,
        description=short_description,
        tags=metadata["youtube"]["tags"] + ["Shorts", "YouTubeShorts"],
    )
    print(f"YouTube Short publié : https://youtube.com/watch?v={short_id}")

    return {"long": long_id, "short": short_id}


# ========== TIKTOK ==========

def publish_tiktok(video_path: str, metadata: dict) -> str:
    """Upload et publie une vidéo sur TikTok via Content Posting API."""

    # Étape 1 : Initialiser l'upload
    init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    headers = {
        "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    file_size = Path(video_path).stat().st_size
    init_body = {
        "post_info": {
            "title": metadata["tiktok"]["title"],
            "description": metadata["tiktok"]["description"],
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": file_size,
            "total_chunk_count": 1,
        },
    }

    init_response = requests.post(init_url, headers=headers, json=init_body, timeout=30)
    init_data = init_response.json()

    if "data" not in init_data or "upload_url" not in init_data["data"]:
        print(f"Erreur TikTok init : {init_data}")
        return ""

    upload_url = init_data["data"]["upload_url"]
    publish_id = init_data["data"]["publish_id"]

    # Étape 2 : Upload du fichier
    with open(video_path, "rb") as video_file:
        upload_headers = {
            "Content-Type": "video/mp4",
            "Content-Range": f"bytes 0-{file_size - 1}/{file_size}",
        }
        requests.put(upload_url, headers=upload_headers, data=video_file, timeout=300)

    print(f"TikTok publié : publish_id={publish_id}")
    return publish_id


# ========== INSTAGRAM ==========

def _upload_video_for_instagram(video_path: str) -> str:
    """Upload la vidéo sur un hébergeur temporaire public pour Instagram.

    Instagram exige une URL publique accessible depuis ses serveurs.
    On utilise 0x0.st (gratuit, fiable, fichiers gardés 30+ jours).
    """
    if video_path.startswith("http"):
        return video_path  # Déjà une URL publique

    print(f"  Upload de la vidéo pour Instagram...")
    filename = Path(video_path).name
    with open(video_path, "rb") as f:
        resp = requests.post(
            "https://0x0.st",
            files={"file": (filename, f, "video/mp4")},
            timeout=300,
        )
    if resp.status_code == 200:
        url = resp.text.strip()
        print(f"  Vidéo hébergée : {url}")
        return url
    raise RuntimeError(f"Upload 0x0.st échoué (status {resp.status_code}): {resp.text}")


def publish_instagram(video_path: str, metadata: dict) -> str:
    """Publie un Reel Instagram via Meta Graph API."""
    graph_url = "https://graph.facebook.com/v21.0"

    # Upload vers hébergeur public (Instagram ne peut pas lire un fichier local)
    video_url = _upload_video_for_instagram(video_path)

    # Étape 1 : Créer le container media (upload asynchrone)
    container_url = f"{graph_url}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
    container_params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": metadata["instagram"]["caption"],
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }
    container_response = requests.post(container_url, params=container_params, timeout=60)
    data = container_response.json()
    container_id = data.get("id")

    if not container_id:
        print(f"Erreur Instagram container : {data}")
        return ""

    # Attendre que le processing soit terminé (statut FINISHED)
    print(f"  Container créé ({container_id}), attente processing...")
    for _ in range(20):
        time.sleep(10)
        status_resp = requests.get(
            f"{graph_url}/{container_id}",
            params={"fields": "status_code", "access_token": INSTAGRAM_ACCESS_TOKEN},
            timeout=30,
        )
        status = status_resp.json().get("status_code", "")
        print(f"  Statut : {status}")
        if status == "FINISHED":
            break
        if status == "ERROR":
            print(f"Erreur processing Instagram : {status_resp.json()}")
            return ""

    # Étape 2 : Publier
    publish_url = f"{graph_url}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"
    publish_params = {
        "creation_id": container_id,
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }
    publish_response = requests.post(publish_url, params=publish_params, timeout=60)
    media_id = publish_response.json().get("id", "")

    print(f"Instagram publié : media_id={media_id}")
    return media_id


# ========== PUBLICATION GLOBALE ==========

def publish_all(videos: dict, metadata: dict) -> dict:
    """Publie sur toutes les plateformes."""
    results = {}

    # YouTube (version longue 16:9 + Short 9:16)
    try:
        results["youtube"] = publish_youtube(videos["long"], videos["court"], metadata)
        print("YouTube OK")
    except Exception as e:
        print(f"Erreur YouTube : {e}")
        results["youtube"] = None

    # TikTok (version courte 9:16)
    try:
        results["tiktok"] = publish_tiktok(videos["court"], metadata)
        print("TikTok OK")
    except Exception as e:
        print(f"Erreur TikTok : {e}")
        results["tiktok"] = None

    # Instagram (version courte 9:16)
    try:
        results["instagram"] = publish_instagram(videos["court"], metadata)
        print("Instagram OK")
    except Exception as e:
        print(f"Erreur Instagram : {e}")
        results["instagram"] = None

    return results


if __name__ == "__main__":
    print("Module de publication chargé. Utilisez publish_all() depuis main.py.")
