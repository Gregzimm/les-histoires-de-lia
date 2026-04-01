"""Étape 4 : Génération des sous-titres depuis le texte + durée audio (100% fidèle)."""

import re
import subprocess
from pathlib import Path


# Corrections : français familier/oral → français écrit correct pour les sous-titres
_GRAMMAR_FIXES = [
    (r"\bJ'suis\b",       "Je suis"),
    (r"\bj'suis\b",       "je suis"),
    (r"\bT'es\b",         "Tu es"),
    (r"\bt'es\b",         "tu es"),
    (r"\bY'a\b",          "Il y a"),
    (r"\by'a\b",          "il y a"),
    (r"\bC'est-y\b",      "Est-ce que c'est"),
    (r"\bPas besoin\b",   "Je n'ai plus besoin"),
    (r"\bJ'ai plus\b",    "Je n'ai plus"),
    (r"\bj'ai plus\b",    "je n'ai plus"),
    (r"\bOn est\b",       "Nous sommes"),
    (r"\bC'est pas\b",    "Ce n'est pas"),
    (r"\bc'est pas\b",    "ce n'est pas"),
    (r"\bC'est\b",        "C'est"),   # garder c'est (déjà correct)
    (r"\bJ'vais\b",       "Je vais"),
    (r"\bj'vais\b",       "je vais"),
    (r"\bJ'peux\b",       "Je peux"),
    (r"\bj'peux\b",       "je peux"),
    (r"\bPis\b",          "Et puis"),
    (r"\bpis\b",          "et puis"),
    (r"\bBen\b",          "Eh bien"),
    (r"\bben\b",          "eh bien"),
]


def _normalize_for_subtitles(text: str) -> str:
    """Corrige la grammaire familière pour un affichage en sous-titres."""
    for pattern, replacement in _GRAMMAR_FIXES:
        text = re.sub(pattern, replacement, text)
    # Supprimer les guillemets qui gênent l'affichage
    text = text.replace('\"', '').replace('\u201c', '').replace('\u201d', '')
    return text


def _format_timestamp(seconds: float) -> str:
    """Convertit des secondes en format SRT (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _get_audio_duration(audio_path: str) -> float:
    """Récupère la durée d'un fichier audio en secondes via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", audio_path],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def _text_to_chunks(text: str, max_chars: int = 45) -> list[str]:
    """Découpe le texte en segments courts pour les sous-titres."""
    # Nettoyer le texte : retirer les doubles espaces, normaliser
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r' +', ' ', text).strip()

    # Découper par ponctuation forte d'abord
    sentences = re.split(r'(?<=[.!?…])\s+', text)

    chunks = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) <= max_chars:
            chunks.append(sentence)
        else:
            # Découper les longues phrases par virgule ou espace
            words = sentence.split()
            current = ""
            for word in words:
                if len(current) + len(word) + 1 <= max_chars:
                    current = (current + " " + word).strip()
                else:
                    if current:
                        chunks.append(current)
                    current = word
            if current:
                chunks.append(current)

    return [c for c in chunks if c.strip()]


def generate_subtitles_from_text(text: str, audio_path: str, output_path: str) -> str:
    """Génère un fichier SRT depuis le texte et la durée audio.

    Répartit les segments uniformément sur la durée de l'audio.
    100% fidèle au texte original, pas de transcription.

    Args:
        text: Texte complet de l'histoire.
        audio_path: Chemin vers l'audio (pour récupérer la durée).
        output_path: Chemin de sauvegarde du fichier SRT.
    """
    duration = _get_audio_duration(audio_path)
    clean_text = _normalize_for_subtitles(text)
    chunks = _text_to_chunks(clean_text)

    if not chunks:
        return output_path

    time_per_chunk = duration / len(chunks)

    srt_lines = []
    for i, chunk in enumerate(chunks):
        start = i * time_per_chunk
        # Légère pause entre segments (80% du temps alloué)
        end = start + (time_per_chunk * 0.9)
        srt_lines.append(
            f"{i + 1}\n{_format_timestamp(start)} --> {_format_timestamp(end)}\n{chunk}\n"
        )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

    print(f"Sous-titres sauvegardés : {output_path} ({len(chunks)} segments)")
    return output_path


def generate_both_subtitles(audio_paths: dict, output_dir: str, story: dict | None = None) -> dict:
    """Génère les sous-titres pour les deux versions audio.

    Si story est fourni, génère depuis le texte (recommandé).
    Sinon, fallback sur Whisper.
    """
    output_dir = Path(output_dir)

    if story:
        short_srt = generate_subtitles_from_text(
            story["version_courte"]["texte"],
            audio_paths["court"],
            str(output_dir / "subtitles_court.srt"),
        )
        long_srt = generate_subtitles_from_text(
            story["version_longue"]["texte"],
            audio_paths["long"],
            str(output_dir / "subtitles_long.srt"),
        )
    else:
        # Fallback Whisper si pas de texte disponible
        import whisper
        m = whisper.load_model("base")
        for key, out_name in [("court", "subtitles_court.srt"), ("long", "subtitles_long.srt")]:
            result = m.transcribe(audio_paths[key], language="fr")
            srt_lines = []
            for i, seg in enumerate(result["segments"], 1):
                s = _format_timestamp(seg["start"])
                e = _format_timestamp(seg["end"])
                srt_lines.append(f"{i}\n{s} --> {e}\n{seg['text'].strip()}\n")
            with open(output_dir / out_name, "w", encoding="utf-8") as f:
                f.write("\n".join(srt_lines))
        short_srt = str(output_dir / "subtitles_court.srt")
        long_srt = str(output_dir / "subtitles_long.srt")

    return {"court": short_srt, "long": long_srt}
