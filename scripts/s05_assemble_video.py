"""Étape 5 : Assemblage vidéo avec FFmpeg (image fixe + audio + sous-titres)."""

import subprocess
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


# ========== THUMBNAILS ==========

def _load_font(size: int):
    """Charge Montserrat Bold ou fallback DejaVu."""
    candidates = [
        "/usr/share/fonts/truetype/montserrat/Montserrat-Bold.ttf",
        "/usr/share/fonts/opentype/montserrat/Montserrat-Bold.ttf",
        "/usr/share/fonts/truetype/montserrat/Montserrat-ExtraBold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def create_thumbnail(image_path: str, title: str, output_path: str) -> str:
    """Génère une miniature stylisée avec le titre en overlay.

    Design :
    - Illustration originale en fond
    - Dégradé sombre en bas (60 % → transparent en haut, opaque en bas)
    - Titre centré en bas, blanc avec ombre portée
    - Petit badge "Les Histoires de LIA" en haut à gauche
    """
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size

    # --- Dégradé sombre bas ---
    gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_g = ImageDraw.Draw(gradient)
    grad_start = int(height * 0.52)
    for y in range(grad_start, height):
        progress = (y - grad_start) / (height - grad_start)
        alpha = int(210 * (progress ** 0.8))
        draw_g.line([(0, y), (width, y)], fill=(10, 5, 30, alpha))
    img = Image.alpha_composite(img, gradient)

    draw = ImageDraw.Draw(img)

    # --- Titre principal ---
    title_font_size = max(48, int(width * 0.066))
    title_font = _load_font(title_font_size)
    max_chars = max(12, int(width / (title_font_size * 0.58)))
    lines = textwrap.wrap(title, width=max_chars)[:2]

    line_h = int(title_font_size * 1.25)
    total_h = len(lines) * line_h
    y_text = height - int(height * 0.07) - total_h

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        x = (width - tw) // 2
        # Ombre portée
        for dx, dy in [(-2, 2), (2, 2), (0, 3)]:
            draw.text((x + dx, y_text + dy), line, font=title_font,
                      fill=(0, 0, 0, 180))
        # Texte blanc
        draw.text((x, y_text), line, font=title_font, fill=(255, 255, 255, 255))
        y_text += line_h

    # --- Badge branding haut-gauche ---
    badge_font_size = max(22, int(width * 0.026))
    badge_font = _load_font(badge_font_size)
    badge_text = "Les Histoires de LIA"
    bx, by = int(width * 0.035), int(height * 0.028)
    b_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    b_w = b_bbox[2] - b_bbox[0] + int(width * 0.03)
    b_h = b_bbox[3] - b_bbox[1] + int(height * 0.012)
    pad_x, pad_y = int(width * 0.015), int(height * 0.006)

    badge_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge_layer)
    bd.rounded_rectangle(
        [bx, by, bx + b_w, by + b_h],
        radius=int(b_h * 0.45),
        fill=(20, 10, 60, 190),
    )
    bd.text((bx + pad_x, by + pad_y), badge_text, font=badge_font,
            fill=(255, 255, 255, 230))
    img = Image.alpha_composite(img, badge_layer)

    # --- Sauvegarde ---
    result = img.convert("RGB")
    result.save(output_path, "PNG", optimize=True)
    print(f"  Miniature générée : {output_path}")
    return output_path


def generate_thumbnails(images: dict, title: str, output_dir: str) -> dict:
    """Génère les miniatures 9:16 (Short) et 16:9 (Long) avec titre overlay."""
    out = Path(output_dir)
    return {
        "portrait":  create_thumbnail(images["portrait"],  title, str(out / "thumbnail_9x16.png")),
        "landscape": create_thumbnail(images["landscape"], title, str(out / "thumbnail_16x9.png")),
    }


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
        "FontName=Montserrat,"
        "Bold=1,"
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
