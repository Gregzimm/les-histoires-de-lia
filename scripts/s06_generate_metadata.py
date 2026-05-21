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

RÈGLE ABSOLUE SUR LES TITRES :
Les titres doivent sonner naturels et humains — jamais formulaïques ni répétitifs.
INTERDIT : toujours finir par "| Histoire pour Enfants", "| Conte Magique", "#Shorts" dans le titre, ou répéter le même schéma.
AUTORISÉ : varier librement le format. Choisir parmi ces styles selon ce qui colle le mieux à l'histoire :
  Style A — Narratif : "[personnage] [verbe d'action] [quelque chose d'insolite]" ex: "Léonie retrouve son courage cette nuit-là 🌙"
  Style B — Question : "Et si [situation magique inattendue] ?" ex: "Et si les fleurs pouvaient te parler ? 🌸"
  Style C — Accroche émotionnelle : "[personnage] avait peur de [X]... jusqu'au jour où" ex: "Il avait peur du noir. Jusqu'à cette nuit-là. 🌑"
  Style D — Mystère : "[phrase courte mystérieuse sur l'histoire]" ex: "Le carnet de Papi cachait un secret 📘"
  Style E — Interpellation parent : "[question ou suggestion au parent]" ex: "Une histoire pour aider ton enfant à s'endormir 🌙"
Mélange les styles d'une publication à l'autre. L'emoji peut être au début OU à la fin.
Intègre naturellement 1-2 mots SEO parmi : histoire du soir, conte, magie, enfants — mais sans les forcer.

Réponds UNIQUEMENT avec un JSON valide (sans bloc de code markdown) :

{{
    "youtube": {{
        "title": "Titre YouTube naturel et varié (max 70 caractères). Appliquer la règle ci-dessus.",
        "description": "Description YouTube (5-7 lignes). Ligne 1 : phrase accrocheuse sur l'histoire, ton chaleureux. Ligne 2-3 : résumé naturel avec mots-clés ('histoire du soir pour enfants', 'conte magique', 'histoire pour s\\'endormir', '4 ans 5 ans 6 ans 7 ans'). Ligne 4 : call-to-action abonnement chaleureux. Ligne 5-6 : 4-5 hashtags max (#HistoireDuSoir #ContePourEnfants #LesHistoiresDeLeone #Maternelle).",
        "tags": ["histoire du soir pour enfants", "conte pour enfants", "histoire magique", "histoire pour s endormir", "histoires enfants", "maternelle", "4 ans", "5 ans", "6 ans", "7 ans", "8 ans", "les histoires de lia", "conte magique", "histoire courte enfant", "lecture enfant"]
    }},
    "tiktok": {{
        "title": "Titre TikTok court et percutant (max 50 caractères). Appliquer la règle ci-dessus. Pas de #Shorts dans le titre.",
        "description": "Caption TikTok (max 150 caractères) : phrase intrigante sur l'histoire + 4-5 hashtags essentiels seulement. Varier la formulation."
    }},
    "instagram": {{
        "caption": "Caption Instagram : 2-3 lignes d'intro engageantes et chaleureuses avec emojis. Ton humain, comme si un parent parlait à d'autres parents. Puis saut de ligne. Puis 20-25 hashtags mélangés français/anglais pertinents : #histoiredusoir #conteenfants #histoirematernelle #storytime #kidsstories #histoirespourenfants #maternelle #parentalite #contedefees #leshistoiresdelia #bedtimestory #enfants #educationbienveillante #livresenfants #imaginaire #magie #bienveillance #parentalitepositive + 5-6 hashtags spécifiques au thème de l'histoire."
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
