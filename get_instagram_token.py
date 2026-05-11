#!/usr/bin/env python3
"""
Script OAuth Meta/Instagram — récupère un token de page permanent pour @histoires_de_lia
Utilise l'app lia-pipeline (ID: 929298539850982)

Étapes :
1. Va sur https://developers.facebook.com/tools/explorer/?app_id=929298539850982
2. Sélectionne "lia-pipeline" dans "Application Meta"
3. Clique "Generate Access Token" avec les permissions :
   pages_show_list, business_management, instagram_basic,
   instagram_manage_comments, instagram_content_publish, pages_read_engagement
4. Copie le token généré
5. Lance ce script : python3 get_instagram_token.py

Usage : python3 get_instagram_token.py
"""

import urllib.parse
import urllib.request
import json
import re
import os

APP_ID     = "929298539850982"
PAGE_NAME  = "Histoires de Lia"
PAGE_ID    = "673902002465579"

ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")


def exchange_short_to_long(short_token: str, app_secret: str) -> dict:
    """Échange un token court (1h) contre un token long (60 jours)."""
    url = "https://graph.facebook.com/v21.0/oauth/access_token?" + urllib.parse.urlencode({
        "grant_type":        "fb_exchange_token",
        "client_id":         APP_ID,
        "client_secret":     app_secret,
        "fb_exchange_token": short_token,
    })
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_page_token(long_user_token: str) -> str:
    """Récupère le token de page permanent pour 'Histoires de Lia'."""
    url = f"https://graph.facebook.com/v21.0/{PAGE_ID}?fields=access_token&access_token={long_user_token}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data.get("access_token", "")


def debug_token(token: str, user_token: str) -> dict:
    """Affiche les infos du token (type, expiration, portées)."""
    url = f"https://graph.facebook.com/v21.0/debug_token?input_token={token}&access_token={user_token}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def update_env(token: str):
    """Met à jour INSTAGRAM_ACCESS_TOKEN dans le fichier .env."""
    with open(ENV_FILE, "r") as f:
        content = f.read()

    if "INSTAGRAM_ACCESS_TOKEN=" in content:
        content = re.sub(
            r"INSTAGRAM_ACCESS_TOKEN=.*",
            f"INSTAGRAM_ACCESS_TOKEN={token}",
            content
        )
    else:
        content += f"\nINSTAGRAM_ACCESS_TOKEN={token}\n"

    with open(ENV_FILE, "w") as f:
        f.write(content)
    print(f"✅  .env mis à jour : INSTAGRAM_ACCESS_TOKEN={token[:30]}...")


def main():
    print("\n" + "="*65)
    print("  TOKEN INSTAGRAM PERMANENT — @histoires_de_lia")
    print("="*65)

    print("""
Prérequis :
  1. Va sur : https://developers.facebook.com/tools/explorer/?app_id=929298539850982
  2. App : "lia-pipeline"
  3. Clique "Generate Access Token" avec ces 6 permissions :
       • pages_show_list
       • business_management
       • instagram_basic
       • instagram_manage_comments
       • instagram_content_publish
       • pages_read_engagement
  4. Copie le token affiché dans "Token d'accès"
""")

    short_token = input("→ Colle le token court ici : ").strip()
    if not short_token:
        print("❌  Token vide. Abandon.")
        return

    print("""
Ensuite, récupère le secret de l'app "lia-pipeline" :
  → https://developers.facebook.com/apps/929298539850982/settings/basic/
  → Clique "Afficher" à côté de "Clé secrète de l'app" et entre ton mot de passe Facebook
  → Copie la clé secrète
""")

    app_secret = input("→ Colle la clé secrète de l'app : ").strip()
    if not app_secret:
        print("❌  Clé secrète vide. Abandon.")
        return

    print("\n1. Échange du token court → token long (60 jours)…")
    try:
        result = exchange_short_to_long(short_token, app_secret)
    except Exception as e:
        print(f"\n❌  Erreur lors de l'échange : {e}")
        return

    long_user_token = result.get("access_token", "")
    if not long_user_token:
        print(f"\n❌  Pas de token dans la réponse : {result}")
        return

    expires_in = result.get("expires_in", "?")
    print(f"   ✅ Token long obtenu (expire dans {expires_in}s ≈ 60 jours)")

    print(f"\n2. Récupération du token de page permanent pour '{PAGE_NAME}'…")
    try:
        page_token = get_page_token(long_user_token)
    except Exception as e:
        print(f"\n❌  Erreur : {e}")
        return

    if not page_token:
        print("\n❌  Pas de token de page dans la réponse.")
        return

    print(f"   ✅ Token de page obtenu : {page_token[:40]}…")

    # Vérifier le token
    print("\n3. Vérification du token de page…")
    try:
        debug_info = debug_token(page_token, long_user_token)
        data = debug_info.get("data", {})
        expires = data.get("expires_at", 0)
        scopes = data.get("scopes", [])
        is_valid = data.get("is_valid", False)

        if expires == 0:
            print("   ✅ Token permanent (jamais expiré) !")
        else:
            from datetime import datetime
            dt = datetime.fromtimestamp(expires)
            print(f"   ℹ️  Expire le : {dt.strftime('%Y-%m-%d')}")

        if "instagram_basic" in scopes:
            print("   ✅ instagram_basic présent")
        if "instagram_content_publish" in scopes:
            print("   ✅ instagram_content_publish présent")
        print(f"   Valide : {is_valid}")
    except Exception as e:
        print(f"   ⚠️  Impossible de vérifier : {e}")

    # Mettre à jour .env
    print("\n4. Mise à jour du fichier .env…")
    update_env(page_token)

    print("\n" + "="*65)
    print("  TOKEN SAUVEGARDÉ")
    print("="*65)
    print("""
Prochaine étape : mettre à jour le secret GitHub
  gh secret set INSTAGRAM_ACCESS_TOKEN --body "{token}"

Ou lance :
  gh secret set INSTAGRAM_ACCESS_TOKEN < <(grep INSTAGRAM_ACCESS_TOKEN .env | cut -d= -f2)
""".format(token=page_token[:30] + "..."))


if __name__ == "__main__":
    main()
