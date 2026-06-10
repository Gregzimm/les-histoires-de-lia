"""Script pour regénérer le refresh token YouTube."""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")

# Scope complet : upload + gestion des playlists
SCOPES = ["https://www.googleapis.com/auth/youtube"]

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

print("Ouverture du navigateur pour autoriser l'accès YouTube...")
flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=8080, open_browser=False)

print(f"\n✅ Nouveau YOUTUBE_REFRESH_TOKEN :\n")
print(creds.refresh_token)
print(f"\nCopiez cette valeur dans :")
print(f"  1. Le fichier .env (YOUTUBE_REFRESH_TOKEN=...)")
print(f"  2. GitHub Secrets → YOUTUBE_REFRESH_TOKEN")

# Sauvegarder dans un fichier pour récupération
with open("/tmp/youtube_refresh_token.txt", "w") as f:
    f.write(creds.refresh_token)
print(f"\n(Token aussi sauvegardé dans /tmp/youtube_refresh_token.txt)")
