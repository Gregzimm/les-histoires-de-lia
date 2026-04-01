"""Étape 3 : Génération de la narration audio via edge-tts (Microsoft Neural, gratuit)."""

import asyncio
from pathlib import Path

VOICE = "fr-FR-EloiseNeural"  # Voix féminine, jeune et chaleureuse
RATE = "-5%"    # Légèrement plus lente pour les enfants
PITCH = "+3Hz"  # Légèrement plus aigu, plus enfantin


async def _generate(text: str, output_path: str) -> str:
    import edge_tts
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    communicator = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicator.save(output_path)
    return output_path


def generate_narration(text: str, output_path: str) -> str:
    """Génère la narration audio d'une histoire."""
    asyncio.run(_generate(text, output_path))
    print(f"Audio sauvegardé : {output_path}")
    return output_path


def generate_both_versions(story: dict, output_dir: str) -> dict:
    """Génère l'audio pour les versions courte et longue."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    short_path = generate_narration(
        story["version_courte"]["texte"],
        str(output_dir / "narration_courte.mp3"),
    )

    long_path = generate_narration(
        story["version_longue"]["texte"],
        str(output_dir / "narration_longue.mp3"),
    )

    return {"court": short_path, "long": long_path}


if __name__ == "__main__":
    test_text = "Il était une fois, dans un petit village, un enfant qui rêvait de toucher les étoiles."
    generate_narration(test_text, "output/test_audio.mp3")
