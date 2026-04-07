"""Étape 1 : Génération de l'histoire via Claude API (Anthropic)."""

import json
from datetime import datetime
import anthropic
try:
    from config import ANTHROPIC_API_KEY, PROJECT_CONFIG
except ModuleNotFoundError:
    from scripts.config import ANTHROPIC_API_KEY, PROJECT_CONFIG

# 60 thèmes variés — chaque jour de l'année pioche un thème différent
THEMES_POOL = [
    "la jalousie entre frères et sœurs",
    "la peur du premier jour d'école",
    "un animal de compagnie qui parle",
    "découvrir la mer pour la première fois",
    "un grand-père qui raconte des histoires inventées",
    "apprendre à faire du vélo",
    "un jardin secret dans la ville",
    "la magie des livres qui prennent vie",
    "un robot qui apprend à ressentir",
    "une graine qui refuse de pousser",
    "le monstre sous le lit qui est en fait gentil",
    "une fête d'anniversaire qui tourne mal puis bien",
    "la tristesse quand un ami déménage",
    "un tableau qui aspire les enfants à l'intérieur",
    "la fierté d'apprendre à nager",
    "une lettre envoyée à la lune",
    "la solitude d'être enfant unique",
    "un cerf-volant qui s'échappe",
    "la magie des bonbons qui changent de goût",
    "un enfant qui peut parler aux insectes",
    "la pluie qui cache des trésors",
    "un miroir qui montre le futur",
    "apprendre à perdre au jeu",
    "une bibliothèque qui change de livres chaque nuit",
    "la timidité au théâtre scolaire",
    "une chaussette qui disparaît toujours",
    "le courage de dire la vérité",
    "un pont entre deux mondes",
    "la magie des étoiles filantes",
    "un enfant qui collectionne les couleurs",
    "une île flottante dans le ciel",
    "apprendre à partager un jouet précieux",
    "la nuit où tous les jouets s'animent",
    "un grand voyage en train",
    "la découverte du mensonge",
    "un enfant qui peut ralentir le temps",
    "une forêt qui murmure des secrets",
    "le déménagement dans une nouvelle maison",
    "une recette de cuisine magique",
    "la peur du tonnerre",
    "un enfant qui garde un dragon miniature",
    "apprendre à demander pardon",
    "une écharpe qui voyage autour du monde",
    "la magie d'une chambre qui s'agrandit",
    "le premier mensonge et ses conséquences",
    "une rivière qui chante",
    "la fierté de cuisiner seul pour la première fois",
    "un enfant qui peut voir les émotions en couleurs",
    "la magie d'une boîte à musique",
    "apprendre à être patient",
    "une porte cachée derrière l'armoire",
    "la nuit de la pleine lune",
    "un ballon de baudruche qui ne veut pas redescendre",
    "la découverte d'une vieille photo",
    "un enfant qui parle aux pierres",
    "la magie des bulles de savon",
    "apprendre à nager dans la nuit",
    "une horloge qui remonte le temps",
    "le premier ami imaginaire",
    "la magie d'un dessin qui prend vie",
]

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

    # Thème du jour — tourne sur 60 jours
    day_of_year = datetime.now().timetuple().tm_yday
    daily_theme = THEMES_POOL[day_of_year % len(THEMES_POOL)]
    theme_to_use = theme_hint if theme_hint else daily_theme

    user_prompt = f"""Génère une nouvelle histoire pour enfants originale sur le thème : **{theme_to_use}**

Ce thème DOIT être le cœur de l'histoire. Évite les histoires sur les nuages, les rêves, ou les étoiles sauf si le thème le demande.

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

    print(f"  Thème du jour : {theme_to_use}")

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
