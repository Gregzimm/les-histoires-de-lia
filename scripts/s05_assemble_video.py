"""Étape 5 : Assemblage vidéo avec FFmpeg (image fixe + audio + sous-titres)."""

import subprocess
from pathlib import Path


def get_audio_duration(audio_path: str) -> float:
    """Récupère la durée d'un fichier audio en secondes."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            audio_path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def assemble_video(
    image_path: str,
    audio_path: str,
    subtitle_path: str,
    output_path: str,
    resolution: str = "1080x1920",
    ken_burns: bool = True,
) -> str:
    """Assemble une vidéo à partir d'une image fixe, audio et sous-titres.

    Args:
        image_path: Chemin vers l'image de couverture.
        audio_path: Chemin vers la narration audio.
        subtitle_path: Chemin vers le fichier SRT.
        output_path: Chemin de sortie de la vidéo.
        resolution: Résolution cible (ex: "1080x1920" ou "1920x1080").
        ken_burns: Appliquer un léger effet de zoom lent (Ken Burns).
    """
    duration = get_audio_duration(audio_path)
    width, height = resolution.split("x")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Construire le filtre vidéo
    if ken_burns:
        # Zoom lent de 100% à 110% sur toute la durée
        video_filter = (
            f"scale={int(width)*2}:{int(height)*2},"
            f"zoompan=z='min(zoom+0.0002,1.1)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={int(duration*25)}:s={width}x{height}:fps=25"
        )
    else:
        video_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"

    # Sous-titres style gros texte pour les shorts
    subtitle_style = (
        "FontName=Arial Black,"
        "FontSize=22,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "Outline=3,"
        "Shadow=1,"
        "Alignment=2,"
        "MarginV=80"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-vf", f"{video_filter},subtitles={subtitle_path}:force_style='{subtitle_style}'",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-t", str(duration + 1),
        output_path,
    ]

    print(f"Assemblage vidéo : {output_path}")
    subprocess.run(cmd, check=True)
    print(f"Vidéo créée : {output_path}")
    return output_path


def assemble_both_versions(
    images: dict,
    audio_paths: dict,
    subtitle_paths: dict,
    output_dir: str,
) -> dict:
    """Assemble les vidéos pour les versions courte et longue."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    short_video = assemble_video(
        image_path=images["portrait"],
        audio_path=audio_paths["court"],
        subtitle_path=subtitle_paths["court"],
        output_path=str(output_dir / "video_court_9x16.mp4"),
        resolution="1080x1920",
    )

    long_video = assemble_video(
        image_path=images["landscape"],
        audio_path=audio_paths["long"],
        subtitle_path=subtitle_paths["long"],
        output_path=str(output_dir / "video_long_16x9.mp4"),
        resolution="1920x1080",
    )

    return {"court": short_video, "long": long_video}


if __name__ == "__main__":
    assemble_video(
        "output/test_cover.png",
        "output/test_audio.mp3",
        "output/test_subtitles.srt",
        "output/test_video.mp4",
    )
