"""Étape 6 : Génération des métadonnées optimisées pour chaque plateforme."""

import json
import anthropic
try:
    from config import ANTHROPIC_API_KEY
except ModuleNotFoundError:
    from scripts.config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def generate_metadata(story: dict) -> dict:
    """Génère les descriptions optimisées pour YouTube, TikTok et Instagram."""

    prompt = f"""À partir de cette histoire pour enfants, génère les métadonnées optimisées pour chaque plateforme.

HISTOIRE :
- Titre : {story['titre']}
- Description : {story['description']}
- Thème : {story['theme']}
- Morale : {story.get('morale', '')}

CONTEXTE PLATEFORME :
- La vidéo courte (Shorts/Reels/TikTok) dure ~35 secondes
- La vidéo longue (YouTube) dure ~5 minutes
- Public : parents qui cherchent des histoires du soir, enfants 4-8 ans

Réponds UNIQUEMENT avec un JSON valide (sans bloc de code markdown) :

{{
    "youtube": {{
        "title": "Titre YouTube optimisé SEO (max 70 caractères). Format : [emoji] [Titre histoire] | Histoire du soir pour enfants. Doit contenir des mots que les parents cherchent : 'histoire du soir', 'conte', 'histoire magique', 'enfants'. Commence par un emoji pertinent.",
        "description": "Description YouTube SEO (5-7 lignes). Ligne 1 : phrase accrocheuse sur l'histoire. Ligne 2-3 : résumé avec mots-clés ('histoire du soir pour enfants', 'conte magique', 'histoire pour s\\'endormir', 'histoires pour enfants 4 ans 5 ans 6 ans'). Ligne 4 : 'Abonne-toi pour une nouvelle histoire chaque jour 🔔'. Ligne 5-6 : hashtags (#HistoirePourEnfants #ContePourEnfants #HistoireDuSoir #LesHistoiresDeLeone #Maternelle #Parentalité).",
        "tags": ["histoire du soir pour enfants", "conte pour enfants", "histoire magique", "histoire pour s endormir", "histoires enfants", "maternelle", "4 ans", "5 ans", "6 ans", "7 ans", "8 ans", "les histoires de lia", "conte magique", "histoire courte enfant", "lecture enfant"]
    }},
    "tiktok": {{
        "title": "titre percutant (max 50 caractères), commence par emoji",
        "description": "caption TikTok (max 150 caractères) : emoji + phrase intrigante sur l'histoire + 5-6 hashtags essentiels : #histoiredusoir #conteenfants #histoirematernelle #storytime #enfants #LesHistoiresDeLeone"
    }},
    "instagram": {{
        "caption": "Caption Instagram : 2-3 lignes d'intro engageantes avec emojis sur l'histoire. Puis saut de ligne. Puis 25-30 hashtags mélangés français/anglais : #histoiredusoir #conteenfants #histoirematernelle #histoiremagiqueenfants #storytime #kidsstories #histoirespourenfants #maternelle #parentalite #contedefees #leshistoiresdelia #histoirecourte #bedtimestory #enfants #educationbienveillante #livresenfants #imaginaire #magie #bienveillance #parentalitepositive + hashtags spécifiques au thème de l'histoire"
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
