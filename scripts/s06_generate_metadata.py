"""Étape 6 : Génération des métadonnées optimisées pour chaque plateforme."""

import json
import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def generate_metadata(story: dict) -> dict:
    """Génère les descriptions optimisées pour YouTube, TikTok et Instagram."""

    prompt = f"""À partir de cette histoire pour enfants, génère les métadonnées optimisées pour les réseaux sociaux.

HISTOIRE :
- Titre : {story['titre']}
- Description : {story['description']}
- Thème : {story['theme']}
- Morale : {story.get('morale', '')}

Réponds UNIQUEMENT avec un JSON valide (sans bloc de code markdown) :

{{
    "youtube": {{
        "title": "titre accrocheur pour YouTube (max 70 caractères), commençant par un emoji",
        "description": "description SEO optimisée pour YouTube (3-5 lignes), incluant des mots-clés pertinents, un appel à l'abonnement, et les hashtags. Mentionner 'Les Histoires de LIA' et le thème.",
        "tags": ["liste", "de", "tags", "pertinents", "max", "15"]
    }},
    "tiktok": {{
        "title": "titre court et percutant (max 50 caractères)",
        "description": "caption TikTok engageante avec emojis et hashtags populaires (max 150 caractères). Inclure #LesHistoiresdeLIA"
    }},
    "instagram": {{
        "caption": "caption Instagram complète avec emojis, storytelling, appel à l'action et 20-30 hashtags pertinents. Mentionner @leshistoiresdelia"
    }}
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()
    metadata = json.loads(raw)
    return metadata


def save_metadata(metadata: dict, output_path: str) -> str:
    """Sauvegarde les métadonnées en JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Métadonnées sauvegardées : {output_path}")
    return output_path


if __name__ == "__main__":
    test_story = {
        "titre": "Le Jour Où Jules Est Devenu Grand Frère",
        "description": "Jules vit mal l'arrivée de son petit frère.",
        "theme": "jalousie, famille, grandir",
        "morale": "Être grand frère, c'est un super-pouvoir",
    }
    metadata = generate_metadata(test_story)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
