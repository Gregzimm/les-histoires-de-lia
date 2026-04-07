"""Étape 2 : Génération de l'image de couverture via Replicate API (Flux)."""

import time
import requests
from pathlib import Path
try:
    from config import REPLICATE_API_TOKEN
except ModuleNotFoundError:
    from scripts.config import REPLICATE_API_TOKEN


def generate_cover_image(
    illustration_prompt: str,
    output_path: str,
    aspect_ratio: str = "9:16",
) -> str:
    """Génère l'image de couverture avec Flux 1.1 Pro via Replicate REST API."""
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
        "Prefer": "wait",
    }

    payload = {
        "input": {
            "prompt": illustration_prompt,
            "aspect_ratio": aspect_ratio,
            "output_format": "png",
            "safety_tolerance": 5,
        }
    }

    for attempt in range(4):
        resp = requests.post(
            "https://api.replicate.com/v1/models/black-forest-labs/flux-1.1-pro/predictions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        if resp.status_code == 429:
            wait = 15 * (attempt + 1)
            print(f"  Rate limit Replicate, attente {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        break
    prediction = resp.json()

    while prediction.get("status") not in ("succeeded", "failed", "canceled"):
        time.sleep(2)
        poll = requests.get(
            prediction["urls"]["get"],
            headers={"Authorization": f"Bearer {REPLICATE_API_TOKEN}"},
            timeout=30,
        )
        prediction = poll.json()

    if prediction.get("status") != "succeeded":
        error = prediction.get("error", "")
        if "NSFW" in str(error):
            return None  # Signal pour retry avec prompt de secours
        raise RuntimeError(f"Replicate a échoué : {error}")

    output = prediction.get("output")
    image_url = output[0] if isinstance(output, list) else str(output)

    image_data = requests.get(image_url, timeout=120).content
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_data)

    print(f"Image sauvegardée : {output_path}")
    return output_path


FALLBACK_PROMPT = (
    "children book illustration, soft watercolor style, magical glowing forest at night, "
    "small cute animals, fireflies, pastel colors, warm golden light, dreamy atmosphere, "
    "no text, no people, G-rated, safe for children"
)


def _generate_with_fallback(prompt: str, output_path: str, aspect_ratio: str) -> str:
    """Essaie le prompt original, puis le prompt de secours si NSFW détecté."""
    result = generate_cover_image(prompt, output_path, aspect_ratio)
    if result is None:
        print(f"  NSFW détecté, retry avec prompt de secours...")
        time.sleep(5)
        result = generate_cover_image(FALLBACK_PROMPT, output_path, aspect_ratio)
        if result is None:
            raise RuntimeError("Impossible de générer l'image même avec le prompt de secours.")
    return result


def generate_both_formats(illustration_prompt: str, output_dir: str) -> dict:
    """Génère les deux formats d'image (9:16 et 16:9)."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    portrait = _generate_with_fallback(
        illustration_prompt,
        str(output_dir / "cover_9x16.png"),
        aspect_ratio="9:16",
    )

    time.sleep(5)
    landscape_prompt = illustration_prompt.replace("9:16 format", "16:9 format")
    landscape = _generate_with_fallback(
        landscape_prompt,
        str(output_dir / "cover_16x9.png"),
        aspect_ratio="16:9",
    )

    return {"portrait": portrait, "landscape": landscape}
