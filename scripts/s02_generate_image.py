"""Étape 2 : Génération de l'image de couverture via DALL-E 3."""

import requests
from pathlib import Path
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_cover_image(
    illustration_prompt: str,
    output_path: str,
    size: str = "1024x1792",
) -> str:
    """Génère l'image de couverture avec DALL-E 3.

    Args:
        illustration_prompt: Le prompt d'illustration de l'histoire.
        output_path: Chemin de sauvegarde de l'image.
        size: Taille de l'image. "1024x1792" pour 9:16, "1792x1024" pour 16:9.
    """
    response = client.images.generate(
        model="dall-e-3",
        prompt=illustration_prompt,
        size=size,
        quality="hd",
        n=1,
    )

    image_url = response.data[0].url

    image_data = requests.get(image_url, timeout=60).content
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_data)

    print(f"Image sauvegardée : {output_path}")
    return output_path


def generate_both_formats(illustration_prompt: str, output_dir: str) -> dict:
    """Génère les deux formats d'image (9:16 et 16:9)."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    portrait = generate_cover_image(
        illustration_prompt,
        str(output_dir / "cover_9x16.png"),
        size="1024x1792",
    )

    landscape_prompt = illustration_prompt.replace("9:16 format", "16:9 format")
    landscape = generate_cover_image(
        landscape_prompt,
        str(output_dir / "cover_16x9.png"),
        size="1792x1024",
    )

    return {"portrait": portrait, "landscape": landscape}


if __name__ == "__main__":
    test_prompt = (
        "detailed 2D digital illustration, children's book style, "
        "a small boy with a red cape sitting under a rainbow tree, "
        "magical glowing snail beside him, pastel saturated colors, "
        "warm magical lighting, no text, immersive composition, 9:16 format"
    )
    generate_cover_image(test_prompt, "output/test_cover.png")
