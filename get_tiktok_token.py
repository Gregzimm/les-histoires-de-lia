#!/usr/bin/env python3
"""
Script OAuth TikTok — récupère un access_token pour @histoires_de_lia
Utilise l'app lia-pipeline (ID: 7629390911427889172)

Usage : python3 get_tiktok_token.py
"""

import urllib.parse
import urllib.request
import json
import secrets
import webbrowser
import re
import os

CLIENT_KEY    = os.getenv("TIKTOK_CLIENT_KEY", "aw1hmuh9bxn1groo")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")
REDIRECT_URI  = "https://agencegz.com/tiktok/callback"
SCOPES        = "user.info.basic,video.publish,video.upload"

ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")


def build_auth_url(state: str) -> str:
    params = {
        "client_key":     CLIENT_KEY,
        "scope":          SCOPES,
        "response_type":  "code",
        "redirect_uri":   REDIRECT_URI,
        "state":          state,
    }
    return "https://www.tiktok.com/v2/auth/authorize?" + urllib.parse.urlencode(params)


def exchange_code(code: str) -> dict:
    url  = "https://open.tiktokapis.com/v2/oauth/token/"
    data = urllib.parse.urlencode({
        "client_key":     CLIENT_KEY,
        "client_secret":  CLIENT_SECRET,
        "code":           code,
        "grant_type":     "authorization_code",
        "redirect_uri":   REDIRECT_URI,
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def update_env(token: str, refresh_token: str = ""):
    """Met à jour TIKTOK_ACCESS_TOKEN dans le fichier .env"""
    with open(ENV_FILE, "r") as f:
        content = f.read()

    if "TIKTOK_ACCESS_TOKEN=" in content:
        content = re.sub(
            r"TIKTOK_ACCESS_TOKEN=.*",
            f"TIKTOK_ACCESS_TOKEN={token}",
            content
        )
    else:
        content += f"\nTIKTOK_ACCESS_TOKEN={token}\n"

    if refresh_token and "TIKTOK_REFRESH_TOKEN=" in content:
        content = re.sub(
            r"TIKTOK_REFRESH_TOKEN=.*",
            f"TIKTOK_REFRESH_TOKEN={refresh_token}",
            content
        )
    elif refresh_token:
        content += f"TIKTOK_REFRESH_TOKEN={refresh_token}\n"

    with open(ENV_FILE, "w") as f:
        f.write(content)
    print(f"✅  .env mis à jour : TIKTOK_ACCESS_TOKEN={token[:20]}...")


def main():
    state = secrets.token_hex(16)
    auth_url = build_auth_url(state)

    print("\n" + "="*60)
    print("  AUTHENTIFICATION TIKTOK — @histoires_de_lia")
    print("="*60)
    print(f"\n1. Ouverture du navigateur pour autoriser l'app…")
    print(f"\n   URL : {auth_url}\n")
    webbrowser.open(auth_url)

    print("2. Connecte-toi avec le compte @histoires_de_lia")
    print("   et autorise l'application 'lia-pipeline'.")
    print()
    print("3. Après l'autorisation, TikTok redirigera vers :")
    print(f"   {REDIRECT_URI}?code=XXXXXX&state={state}")
    print("   (la page affichera probablement une erreur 404 — c'est normal)")
    print()
    print("4. Copie l'URL COMPLÈTE depuis la barre d'adresse du navigateur")
    print("   et colle-la ici :")
    print()

    callback_url = input("→ URL complète de la redirection : ").strip()

    # Extraire le code
    parsed = urllib.parse.urlparse(callback_url)
    params = urllib.parse.parse_qs(parsed.query)

    if "code" not in params:
        print("\n❌  Paramètre 'code' introuvable dans l'URL.")
        print(f"   URL reçue : {callback_url}")
        return

    code = params["code"][0]
    returned_state = params.get("state", [""])[0]

    if returned_state != state:
        print(f"\n⚠️  State mismatch (attendu: {state}, reçu: {returned_state})")
        confirm = input("   Continuer quand même ? (o/N) : ").strip().lower()
        if confirm != "o":
            return

    print(f"\n   Code : {code[:20]}…")
    print("\n5. Échange du code contre un access_token…")

    try:
        result = exchange_code(code)
    except Exception as e:
        print(f"\n❌  Erreur lors de l'échange : {e}")
        return

    print(f"\n   Réponse TikTok : {json.dumps(result, indent=2)}")

    access_token  = result.get("access_token", "")
    refresh_token = result.get("refresh_token", "")

    if not access_token:
        print("\n❌  Pas d'access_token dans la réponse.")
        return

    print(f"\n✅  ACCESS TOKEN : {access_token}")
    if refresh_token:
        print(f"   REFRESH TOKEN : {refresh_token}")

    update_env(access_token, refresh_token)

    print("\n" + "="*60)
    print("  TOKEN SAUVEGARDÉ dans .env")
    print("="*60)
    print("\nProchaine étape :")
    print("  Ajouter TIKTOK_ACCESS_TOKEN dans les GitHub Secrets du repo.")
    print("  → https://github.com/[ton-repo]/settings/secrets/actions\n")


if __name__ == "__main__":
    main()
