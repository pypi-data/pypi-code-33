from Fortuna import FlexCat, CumulativeWeightedChoice


note = """
Example: FlexCat inside CumulativeWeightedChoice behind a lambda, flick and twist.

Typical treasure table from a massively popular roll playing game.
  1-15    Spell scroll (7th level)
  16-30   Spell scroll (8th level)
  31-55   Potion of storm giant strength
  56-70   Potion of supreme healing
  71-85   Spell scroll (9th level)
  86-93   Universal solvent
  94-98   Arrow of slaying
  99-100  Sovereign glue
  
"""


random_spell = FlexCat({
    # ToDo: add missing cantrips & spells level 1 to 6.
    'level_7': (
        "Conjure Celestial", "Delayed Blast", "Divine Word", "Etherealness", "Finger of Death", "Fire Storm",
        "Forcecage", "Mirage Arcane", "Mordenkainen's Magnificent Mansion", "Mordenkainen's Sword", "Plane Shift",
        "Prismatic Spray", "Project Image", "Regenerate", "Resurrection", "Reverse Gravity", "Sequester",
        "Simulacrum", "Symbol", "Teleport"
    ),
    'level_8': (
        "Antimagic Field", "Antipathy/Sympathy", "Clone", "Control Weather", "Demiplane", "Dominate Monster",
        "Earthquake", "Feeblemind", "Glibness", "Holy Aura", "Incendiary Cloud", "Maze", "Mind Blank",
        "Power Word Stun", "Sunburst", "Telepathy", "Trap the Soul"
    ),
    'level_9': (
        "Astral Projection", "Foresight", "Gate", "Imprisonment", "Mass Heal", "Meteor Swarm", "Power Word Heal",
        "Power Word Kill", "Prismatic Wall", "Shapechange", "Time Stop", "True Polymorph", "True Resurrection",
        "Weird", "Wish"
    )
})


treasure_table = CumulativeWeightedChoice((
    (15, lambda: f"Spell scroll (7th level) {random_spell('level_7')}"),
    (30, lambda: f"Spell scroll (8th level) {random_spell('level_8')}"),
    (55, "Potion of storm giant strength"),
    (70, "Potion of supreme healing"),
    (85, lambda: f"Spell scroll (9th level) {random_spell('level_9')}"),
    (93, "Universal solvent"),
    (98, "Arrow of slaying"),
    (100, "Sovereign glue")
))


if __name__ == "__main__":
    print(note)
    num_selections = 15
    print(f"{num_selections} random selections from the treasure table:")
    for _ in range(num_selections):
        print(treasure_table())
