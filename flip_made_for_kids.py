"""Passe les vidéos existantes en 'non conçue pour les enfants' (selfDeclaredMadeForKids=False).

Usage :
  python3 flip_made_for_kids.py --ids ID1 ID2 ...   # vidéos précises
  python3 flip_made_for_kids.py --all               # toutes les vidéos encore marquées 'pour enfants'
  python3 flip_made_for_kids.py --all --limit 50    # limite (gestion du quota API : ~50 unités/vidéo)
"""
import argparse
import os

from dotenv import load_dotenv

load_dotenv()

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_client():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
    )
    return build("youtube", "v3", credentials=creds)


def all_video_ids(yt) -> list[str]:
    channel = yt.channels().list(part="contentDetails", mine=True).execute()
    uploads_id = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], None
    while True:
        r = yt.playlistItems().list(
            part="contentDetails", playlistId=uploads_id, maxResults=50, pageToken=page
        ).execute()
        ids.extend(i["contentDetails"]["videoId"] for i in r.get("items", []))
        page = r.get("nextPageToken")
        if not page:
            break
    return ids


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", nargs="*", help="IDs de vidéos à corriger")
    parser.add_argument("--all", action="store_true", help="Toutes les vidéos marquées 'pour enfants'")
    parser.add_argument("--limit", type=int, default=None, help="Nombre max de vidéos à corriger")
    args = parser.parse_args()

    yt = get_client()

    if args.ids:
        candidates = args.ids
    elif args.all:
        candidates = all_video_ids(yt)
    else:
        parser.error("--ids ou --all requis")

    # Statut actuel par lots de 50
    to_flip = []
    for i in range(0, len(candidates), 50):
        batch = candidates[i : i + 50]
        r = yt.videos().list(part="status,snippet", id=",".join(batch)).execute()
        for v in r.get("items", []):
            if v["status"].get("madeForKids"):
                to_flip.append((v["id"], v["snippet"]["title"], v["status"]))

    if args.limit:
        to_flip = to_flip[: args.limit]
    print(f"{len(to_flip)} vidéos à corriger")

    for vid, title, status in to_flip:
        yt.videos().update(
            part="status",
            body={
                "id": vid,
                "status": {
                    "privacyStatus": status.get("privacyStatus", "public"),
                    "selfDeclaredMadeForKids": False,
                    "embeddable": status.get("embeddable", True),
                    "license": status.get("license", "youtube"),
                    "publicStatsViewable": status.get("publicStatsViewable", True),
                },
            },
        ).execute()
        print(f"  ✓ {title}")

    print(f"\nTerminé : {len(to_flip)} vidéos passées en 'non conçue pour les enfants'")


if __name__ == "__main__":
    main()
