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
    "playlist_category": "Choisir UNE catégorie parmi ces 5 exactement : 'Émotions & Sentiments' (peur, jalousie, tristesse, colère, timidité) | 'Amitié & Famille' (amitié, famille, fratrie, grands-parents) | 'Courage & Dépassement' (courage, persévérance, effort, autonomie) | 'Magie & Aventure' (magie, aventure, mystère, découverte) | 'Grandir & Apprendre' (apprendre, partager, pardon, vérité, mensonge, patience)",
    "youtube": {{
        "title": "Titre YouTube naturel et varié (max 70 caractères). Appliquer la règle ci-dessus.",
        "description": "Description YouTube structurée ainsi (utiliser de vrais sauts de ligne \\n) :\\nLigne 1 : hook émotionnel fort sur l'histoire — une phrase qui donne envie de regarder, ton chaleureux et humain. Pas de description plate.\\nLigne 2 : résumé de l'histoire en 1-2 phrases naturelles avec mots-clés intégrés ('histoire du soir pour enfants', 'conte magique', '4 ans 5 ans 6 ans').\\n\\nChapitres (format exact, timestamps pour vidéo ~5 min) :\\n0:00 Il était une fois...\\n0:45 [Titre de la situation principale de l'histoire]\\n2:00 [Titre du moment magique]\\n3:30 [Titre de la résolution]\\n4:30 La fin 🌙\\n\\nUne nouvelle histoire chaque soir pour accompagner le rituel du coucher 🔔 Abonne-toi pour ne rien manquer.\\n\\n#HistoireDuSoir #ContePourEnfants #LesHistoiresDeLeone #Maternelle",
        "tags": ["histoire du soir pour enfants", "conte pour enfants", "histoire magique", "histoire pour s endormir", "histoires enfants", "maternelle", "4 ans", "5 ans", "6 ans", "7 ans", "8 ans", "les histoires de lia", "conte magique", "histoire courte enfant", "lecture enfant"]
    }},
    "youtube_short": {{
        "title": "Titre Short YouTube ultra-court et accrocheur (max 50 caractères). Appliquer la règle ci-dessus. Pas de #Shorts dans le titre — YouTube le détecte automatiquement.",
        "description": "Description Short : 1 phrase intrigante sur l'histoire + saut de ligne + 3 hashtags max : #HistoireDuSoir #LesHistoiresDeLeone + 1 hashtag thématique."
    }},
    "tiktok": {{
        "title": "Titre TikTok court et percutant (max 50 caractères). Appliquer la règle ci-dessus.",
        "description": "Caption TikTok (max 150 caractères) : phrase intrigante sur l'histoire + 4-5 hashtags essentiels. Varier la formulation."
    }},
    "instagram": {{
        "caption": "Caption Instagram : 2-3 lignes d'intro chaleureuses avec emojis, ton humain comme si un parent parlait à d'autres parents. Terminer par une question d'engagement simple et naturelle pour inviter un commentaire (ex: 'Quel est le personnage préféré de ton enfant en ce moment ? 👇' ou question liée au thème de l'histoire). Puis saut de ligne. Puis EXACTEMENT 5 hashtags ultra-ciblés seulement : #histoiredusoir #conteenfants + 1 hashtag thème spécifique + #leshistoiresdelia + #bedtimestory"
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
