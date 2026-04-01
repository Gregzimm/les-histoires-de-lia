"""Étape 1 : Génération de l'histoire via Claude API (Anthropic)."""

import json
import anthropic
try:
    from config import ANTHROPIC_API_KEY, PROJECT_CONFIG
except ModuleNotFoundError:
    from scripts.config import ANTHROPIC_API_KEY, PROJECT_CONFIG

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = f"""Tu es LIA, une conteuse pour enfants de {PROJECT_CONFIG['tranche_age']}.

STYLE NARRATIF :
- Ton : {PROJECT_CONFIG['style_narratif']['ton']}
- Structure : {PROJECT_CONFIG['style_narratif']['structure']}
- Langage : {PROJECT_CONFIG['style_narratif']['langage']}
- Émotions à explorer : {', '.join(PROJECT_CONFIG['style_narratif']['emotions'])}

RÈGLES :
- Chaque histoire a un prénom d'enfant français comme personnage principal
- Un élément magique ou une créature fantaisiste intervient toujours
- La morale est subtile, jamais moralisatrice
- Le vocabulaire est simple mais les images sont poétiques
- Les dialogues sont naturels et drôles mais écrits en français correct (pas de langage SMS)
- Pas de violence, pas de méchants effrayants

Tu dois générer une histoire ORIGINALE et COMPLÈTE, différente de toutes les précédentes."""


def generate_story(theme_hint: str | None = None) -> dict:
    """Génère une histoire complète avec versions courte et longue."""

    user_prompt = """Génère une nouvelle histoire pour enfants originale.

Réponds UNIQUEMENT avec un JSON valide (sans bloc de code markdown), avec cette structure exacte :

{
    "titre": "Le titre de l'histoire",
    "description": "Résumé en 1-2 phrases pour la description vidéo",
    "theme": "les thèmes principaux séparés par des virgules",
    "morale": "la leçon subtile de l'histoire",
    "personnage_principal": "prénom et courte description",
    "element_magique": "description de l'élément fantaisiste",
    "version_courte": {
        "texte": "L'histoire complète en ~200 mots, avec des paragraphes séparés par des \\n\\n"
    },
    "version_longue": {
        "texte": "L'histoire complète en ~700 mots, plus détaillée, riche en dialogues et descriptions, avec des paragraphes séparés par des \\n\\n"
    },
    "illustration_prompt": "prompt détaillé en anglais pour générer l'illustration de couverture, style: detailed 2D digital illustration, children's book style, pastel saturated colors, magical warm lighting, no text, immersive composition, 9:16 format"
}"""

    if theme_hint:
        user_prompt += f"\n\nThème suggéré pour aujourd'hui : {theme_hint}"

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()
    # Retirer les blocs markdown si présents (```json ... ```)
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()
    story = json.loads(raw)
    return story


def save_story(story: dict, output_path: str) -> str:
    """Sauvegarde l'histoire en JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(story, f, ensure_ascii=False, indent=2)
    print(f"Histoire sauvegardée : {output_path}")
    return output_path


if __name__ == "__main__":
    story = generate_story()
    print(f"Titre : {story['titre']}")
    print(f"Version courte : {len(story['version_courte']['texte'].split())} mots")
    print(f"Version longue : {len(story['version_longue']['texte'].split())} mots")
    save_story(story, "output/story.json")
