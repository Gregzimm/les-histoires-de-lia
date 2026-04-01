"""Étape 3 : Génération de la narration audio via ElevenLabs."""

from pathlib import Path
from elevenlabs import ElevenLabs
from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


def generate_narration(
    text: str,
    output_path: str,
    voice_id: str | None = None,
) -> str:
    """Génère la narration audio d'une histoire.

    Args:
        text: Texte complet de l'histoire à narrer.
        output_path: Chemin de sauvegarde du fichier audio MP3.
        voice_id: ID de la voix ElevenLabs (utilise la config par défaut si None).
    """
    vid = voice_id or ELEVENLABS_VOICE_ID

    audio_generator = client.text_to_speech.convert(
        voice_id=vid,
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings={
            "stability": 0.6,
            "similarity_boost": 0.85,
            "style": 0.4,
            "use_speaker_boost": True,
        },
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)

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
