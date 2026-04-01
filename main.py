"""
Les Histoires de LIA - Pipeline principal
==========================================
Orchestre la génération quotidienne d'une histoire pour enfants :
1. Génère l'histoire (Claude API)
2. Génère les images de couverture (DALL-E 3)
3. Génère la narration audio (ElevenLabs)
4. Génère les sous-titres (Whisper)
5. Assemble les vidéos (FFmpeg)
6. Génère les métadonnées réseaux (Claude API)
7. Publie sur YouTube, TikTok, Instagram
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le dossier scripts au path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from scripts.config import OUTPUT_DIR
from scripts.s01_generate_story import generate_story, save_story
from scripts.s02_generate_image import generate_both_formats
from scripts.s03_generate_audio import generate_both_versions
from scripts.s04_generate_subtitles import generate_both_subtitles
from scripts.s05_assemble_video import assemble_both_versions
from scripts.s06_generate_metadata import generate_metadata, save_metadata
from scripts.s07_publish import publish_all


def run_pipeline(theme_hint: str | None = None, skip_publish: bool = False):
    """Exécute le pipeline complet de génération et publication."""

    # Dossier de sortie du jour
    today = datetime.now().strftime("%Y-%m-%d")
    day_dir = OUTPUT_DIR / today
    day_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Les Histoires de LIA - Pipeline du {today}")
    print(f"{'='*60}\n")

    # --- ÉTAPE 1 : Génération de l'histoire ---
    print("[1/7] Génération de l'histoire...")
    story = generate_story(theme_hint)
    story_path = save_story(story, str(day_dir / "story.json"))
    print(f"  → {story['titre']}\n")

    # --- ÉTAPE 2 : Génération des images ---
    print("[2/7] Génération des images de couverture...")
    images = generate_both_formats(
        story["illustration_prompt"],
        str(day_dir),
    )
    print(f"  → Portrait : {images['portrait']}")
    print(f"  → Paysage  : {images['landscape']}\n")

    # --- ÉTAPE 3 : Génération audio ---
    print("[3/7] Génération de la narration audio...")
    audio_paths = generate_both_versions(story, str(day_dir))
    print(f"  → Court : {audio_paths['court']}")
    print(f"  → Long  : {audio_paths['long']}\n")

    # --- ÉTAPE 4 : Génération des sous-titres ---
    print("[4/7] Génération des sous-titres...")
    subtitle_paths = generate_both_subtitles(audio_paths, str(day_dir))
    print(f"  → Court : {subtitle_paths['court']}")
    print(f"  → Long  : {subtitle_paths['long']}\n")

    # --- ÉTAPE 5 : Assemblage vidéo ---
    print("[5/7] Assemblage des vidéos...")
    videos = assemble_both_versions(images, audio_paths, subtitle_paths, str(day_dir))
    print(f"  → Court (9:16) : {videos['court']}")
    print(f"  → Long  (16:9) : {videos['long']}\n")

    # --- ÉTAPE 6 : Métadonnées ---
    print("[6/7] Génération des métadonnées...")
    metadata = generate_metadata(story)
    save_metadata(metadata, str(day_dir / "metadata.json"))
    print(f"  → YouTube : {metadata['youtube']['title']}")
    print(f"  → TikTok  : {metadata['tiktok']['title']}\n")

    # --- ÉTAPE 7 : Publication ---
    if skip_publish:
        print("[7/7] Publication IGNORÉE (mode test)\n")
        results = {"youtube": None, "tiktok": None, "instagram": None}
    else:
        print("[7/7] Publication sur les réseaux...")
        results = publish_all(videos, metadata)
        print()

    # --- Résumé ---
    summary = {
        "date": today,
        "titre": story["titre"],
        "theme": story["theme"],
        "fichiers": {
            "story": story_path,
            "images": images,
            "audio": audio_paths,
            "subtitles": subtitle_paths,
            "videos": videos,
        },
        "publication": results,
    }

    summary_path = day_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"{'='*60}")
    print(f"  Pipeline terminé !")
    print(f"  Histoire : {story['titre']}")
    print(f"  Fichiers : {day_dir}")
    print(f"{'='*60}\n")

    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Les Histoires de LIA - Pipeline")
    parser.add_argument("--theme", type=str, help="Thème suggéré pour l'histoire")
    parser.add_argument("--no-publish", action="store_true", help="Ne pas publier")
    args = parser.parse_args()

    run_pipeline(theme_hint=args.theme, skip_publish=args.no_publish)
