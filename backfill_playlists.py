"""Backfill : ajoute les vidéos longues existantes à la playlist 'Toutes les histoires'.

Usage : python3 backfill_playlists.py
Les playlists thématiques se rempliront automatiquement au fil des publications.
"""
import os
import re

from dotenv import load_dotenv

load_dotenv()

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from scripts.s07_publish import PLAYLIST_DEFINITIONS

LONG_MIN_SECONDS = 120  # en dessous = Short


def _parse_duration(iso: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    h, mn, s = (int(g) if g else 0 for g in m.groups())
    return h * 3600 + mn * 60 + s


def main():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
    )
    yt = build("youtube", "v3", credentials=creds)

    # Playlist "Toutes les histoires" (même titre que le pipeline pour réutilisation)
    title = "Toutes les histoires | Les Histoires de LIA"
    playlist_id = None
    resp = yt.playlists().list(part="id,snippet", mine=True, maxResults=50).execute()
    for item in resp.get("items", []):
        if item["snippet"]["title"] == title:
            playlist_id = item["id"]
            print(f"Playlist existante : {playlist_id}")
    if not playlist_id:
        playlist = yt.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": PLAYLIST_DEFINITIONS["Toutes les histoires"],
                    "defaultLanguage": "fr",
                },
                "status": {"privacyStatus": "public"},
            },
        ).execute()
        playlist_id = playlist["id"]
        print(f"Playlist créée : {playlist_id}")

    # Vidéos déjà dans la playlist (pour pouvoir relancer sans doublons)
    existing = set()
    page = None
    while True:
        try:
            r = yt.playlistItems().list(
                part="contentDetails", playlistId=playlist_id, maxResults=50, pageToken=page
            ).execute()
        except Exception:
            # Une playlist vide fraîchement créée peut renvoyer 404
            break
        existing.update(i["contentDetails"]["videoId"] for i in r.get("items", []))
        page = r.get("nextPageToken")
        if not page:
            break

    # Toutes les vidéos de la chaîne via la playlist "uploads"
    channel = yt.channels().list(part="contentDetails", mine=True).execute()
    uploads_id = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    video_ids = []
    page = None
    while True:
        r = yt.playlistItems().list(
            part="contentDetails", playlistId=uploads_id, maxResults=50, pageToken=page
        ).execute()
        video_ids.extend(i["contentDetails"]["videoId"] for i in r.get("items", []))
        page = r.get("nextPageToken")
        if not page:
            break
    print(f"{len(video_ids)} vidéos sur la chaîne")

    # Durées + dates pour filtrer les longues et trier chronologiquement
    longs = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        r = yt.videos().list(part="contentDetails,snippet", id=",".join(batch)).execute()
        for v in r.get("items", []):
            seconds = _parse_duration(v["contentDetails"]["duration"])
            if seconds >= LONG_MIN_SECONDS:
                longs.append((v["snippet"]["publishedAt"], v["id"], v["snippet"]["title"]))

    longs.sort()  # plus anciennes d'abord
    print(f"{len(longs)} vidéos longues, {len(existing)} déjà dans la playlist")

    added = 0
    for published_at, vid, vtitle in longs:
        if vid in existing:
            continue
        yt.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": vid},
                }
            },
        ).execute()
        added += 1
        print(f"  + {vtitle}")

    print(f"\nTerminé : {added} vidéos ajoutées à '{title}'")


if __name__ == "__main__":
    main()
