"""Configuration centrale du projet Les Histoires de LIA."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Chemins ---
ROOT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = ROOT_DIR / "output"
ASSETS_DIR = ROOT_DIR / "assets"
TEMPLATES_DIR = ROOT_DIR / "templates"

# --- APIs ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# YouTube
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")

# TikTok
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")

# Instagram
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

# --- Projet ---
PROJECT_CONFIG = {
    "nom": "Les Histoires de LIA",
    "tranche_age": "4-8 ans",
    "style_narratif": {
        "ton": "joyeux, enfantin, rassurant, poétique",
        "structure": "situation simple → élément magique → conflit émotionnel → compréhension → résolution douce",
        "langage": "simple mais imagé, accessible aux enfants",
        "emotions": ["peur", "jalousie", "timidité", "manque", "fierté", "amour"],
    },
    "direction_artistique": {
        "style": "illustration numérique 2D très détaillée, style livre jeunesse haut de gamme",
        "ambiance": "magique, lumineuse, douce",
        "palette": "pastel saturé, couleurs chaleureuses",
        "lumiere": "effets féériques, glow doux",
        "personnages": "doux, expressifs",
        "contraintes": [
            "aucun texte dans l'image",
            "composition immersive",
            "style cohérent entre toutes les images",
        ],
    },
    "formats": {
        "court": {
            "duree_cible_secondes": 90,
            "mots_cible": 200,
            "ratio": "9:16",
            "resolution": "1080x1920",
            "plateformes": ["tiktok", "instagram"],
        },
        "long": {
            "duree_cible_secondes": 300,
            "mots_cible": 700,
            "ratio": "16:9",
            "resolution": "1920x1080",
            "plateformes": ["youtube"],
        },
    },
}
