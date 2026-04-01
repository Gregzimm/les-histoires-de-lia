"""Étape 4 : Génération des sous-titres via Whisper."""

from pathlib import Path
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_subtitles(audio_path: str, output_path: str) -> str:
    """Transcrit l'audio et génère un fichier SRT de sous-titres.

    Args:
        audio_path: Chemin vers le fichier audio MP3.
        output_path: Chemin de sauvegarde du fichier SRT.
    """
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="fr",
            response_format="srt",
        )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"Sous-titres sauvegardés : {output_path}")
    return output_path


def generate_both_subtitles(audio_paths: dict, output_dir: str) -> dict:
    """Génère les sous-titres pour les deux versions audio."""
    output_dir = Path(output_dir)

    short_srt = generate_subtitles(
        audio_paths["court"],
        str(output_dir / "subtitles_court.srt"),
    )

    long_srt = generate_subtitles(
        audio_paths["long"],
        str(output_dir / "subtitles_long.srt"),
    )

    return {"court": short_srt, "long": long_srt}


if __name__ == "__main__":
    generate_subtitles("output/test_audio.mp3", "output/test_subtitles.srt")
