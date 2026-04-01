"""Test v3 : pipeline complet avec histoire propre et sous-titres corrigés."""
import sys, json, os
sys.path.insert(0, 'scripts')
from pathlib import Path

story = {
    "titre": "L'Étagère des Petites Peurs",
    "description": "Zoé range ses peurs chaque soir sur une étagère magique, jusqu'au jour où elles lui parlent.",
    "theme": "peur, émotions, confiance en soi",
    "morale": "Les peurs ne sont pas des ennemies, elles nous protègent.",
    "illustration_prompt": (
        "detailed 2D digital illustration, premium children book style, "
        "cozy bedroom at night, magical glowing shelf with small cute friendly creatures, "
        "child in star pajamas sitting in bed looking at shelf with curiosity, "
        "soft warm night light, pastel saturated colors, no text, immersive composition"
    ),
    "version_courte": {
        "texte": (
            "Chaque soir, Zoé avait un rituel.\n\n"
            "Elle rangeait ses petites peurs sur une étagère... qu'elle seule pouvait voir.\n\n"
            "Une pour le noir. Une pour les bruits bizarres. Une pour quand elle devait parler devant la classe.\n\n"
            "Bonne nuit les peurs, disait-elle en bâillant.\n\n"
            "Mais un soir, une voix murmura : Veux-tu bien nous écouter, pour une fois ?\n\n"
            "Ses peurs s'étaient réveillées. Et elles n'étaient pas si terribles : "
            "un nuage mou, une gomme timide, un tambour qui tremblait.\n\n"
            "Nous ne voulons pas t'embêter. Nous voulons juste te prévenir quand tu t'aventures.\n\n"
            "Zoé sourit. D'accord, mais maintenant, je vous garde dans une boîte à câlins.\n\n"
            "Depuis, ses peurs sont toujours là... mais elles sont devenues des compagnons. "
            "Et parfois, elles ronflent plus fort qu'elle !"
        )
    },
    "version_longue": {
        "texte": (
            "Zoé était une aventurière du jour... mais la nuit, elle avait quelques petites peurs.\n\n"
            "Pas des grosses. Des toutes petites, comme des billes qu'on oublie dans une poche.\n\n"
            "Alors elle les rangeait. Sur une étagère qu'elle s'était inventée, juste au pied de son lit.\n\n"
            "Il y avait la peur du noir, un petit nuage violet tout doux. "
            "La peur des bruits inconnus, un tambour timide. "
            "Et la peur de se tromper, une gomme minuscule qui se cachait.\n\n"
            "Chaque soir, elle disait : Chut les peurs. Vous êtes là, je le sais. Mais ce soir, je dors.\n\n"
            "Mais une nuit, une petite voix l'appela : Zoé, peux-tu nous écouter un peu ? Juste un moment.\n\n"
            "Elle ouvrit les yeux. Et là, sur l'étagère, ses peurs ! Debout, agitées, mais pas méchantes.\n\n"
            "Tu nous ranges sans jamais nous parler, dit le nuage violet.\n\n"
            "Nous sommes là pour te prévenir, pas pour te faire mal, ajouta le tambour.\n\n"
            "Quand tu nous écoutes, tu sais où faire attention. Tu sais que c'est normal de douter, chuchota la gomme.\n\n"
            "Zoé s'assit dans son lit et les regarda. Alors vous n'êtes pas là pour m'embêter ?\n\n"
            "Non. Juste pour que tu deviennes plus forte.\n\n"
            "Elle leur tendit sa boîte à câlins. D'accord. On fait un marché : "
            "vous me parlez doucement. Et moi, je vous emmène dans mes poches quand j'en ai besoin.\n\n"
            "Depuis ce soir-là, Zoé dort mieux. Ses peurs se sont transformées en idées, en chansons, "
            "parfois en dessins rigolos.\n\n"
            "Et quand une nouvelle peur arrive, elle l'accueille gentiment : "
            "Bienvenue. Je vais t'apprendre à ne plus faire peur du tout."
        )
    }
}

test_dir = Path("output/test_v3")
test_dir.mkdir(parents=True, exist_ok=True)
with open(test_dir / "story.json", "w", encoding="utf-8") as f:
    json.dump(story, f, ensure_ascii=False, indent=2)

print("[1/4] Images (Flux)...")
from scripts.s02_generate_image import generate_cover_image
img_p = generate_cover_image(story["illustration_prompt"] + ", portrait 9:16", str(test_dir / "cover_9x16.png"), aspect_ratio="9:16")
img_l = generate_cover_image(story["illustration_prompt"] + ", wide landscape 16:9", str(test_dir / "cover_16x9.png"), aspect_ratio="16:9")
images = {"portrait": img_p, "landscape": img_l}
print("  → OK\n")

print("[2/4] Audio (ElevenLabs)...")
from scripts.s03_generate_audio import generate_both_versions
audio_paths = generate_both_versions(story, str(test_dir))
print("  → OK\n")

print("[3/4] Sous-titres corrigés depuis texte...")
from scripts.s04_generate_subtitles import generate_both_subtitles
subtitle_paths = generate_both_subtitles(audio_paths, str(test_dir), story=story)
with open(subtitle_paths["court"]) as f:
    print(f.read()[:500])
print()

print("[4/4] Assemblage vidéo...")
from scripts.s05_assemble_video import assemble_both_versions
videos = assemble_both_versions(images, audio_paths, subtitle_paths, str(test_dir))
print(f"  → Courte 9:16 : {os.path.getsize(videos['court'])/1024/1024:.1f} MB")
print(f"  → Longue 16:9 : {os.path.getsize(videos['long'])/1024/1024:.1f} MB\n")

print("SUCCÈS → output/test_v3/")
import subprocess
subprocess.run(["open", str(test_dir)])
