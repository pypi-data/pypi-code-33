from Fortuna import *


note = """Example: FlexCat and CumulativeWeightedChoice


Typical treasure tables from a massively popular roll playing game.
      
Treasure Table E
  1-30    Spell scroll (8th level) - one of several level 8 spells
  31-55   Potion of storm giant strength
  56-70   Potion of supreme healing
  71-85   Spell scroll (9th level) - one of several level 9 spells
  86-93   Universal solvent
  94-98   Arrow of slaying
  99-100  Sovereign glue
  
"""


random_spell = FlexCat({
    0: ("Acid Splash", "Blade Ward", "Chill Touch", "Dancing Lights", "Fire Bolt", "Friends", "Guidance", "Light"),
    1: ("Alarm", "Animal Friendship", "Bane", "Bless", "Burning Hands", "Charm Person", "Chromatic Orb"),
    2: ("Aid", "Alter Self", "Animal Messenger", "Arcane Lock", "Augury", "Blindness/Deafness", "Blur"),
    3: ("Animate Dead", "Beacon of Hope", "Bestow Curse", "Blink", "Clairvoyance", "Counterspell"),
    4: ("Arcane Eye", "Banishment", "Blight", "Compulsion", "Confusion", "Conjure Minor Elementals"),
    5: ("Animate Objects", "Awaken", "Bigby's Hand", "Cloudkill", "Commune Contagion", "Cone of Cold"),
    6: ("Arcane Gate", "Blade Barrier", "Chain Lightning", "Circle of Death", "Contingency", "Create Undead"),
    7: ("Conjure Celestial", "Delayed Blast", "Divine Word", "Etherealness", "Finger of Death", "Fire Storm"),
    8: ("Antimagic Field", "Antipathy", "Clone", "Control Weather", "Demiplane", "Dominate Monster"),
    9: ("Astral Projection", "Foresight", "Gate", "Imprisonment", "Mass Heal", "Meteor Swarm", "Power Word Heal"),
})

treasure_table_e = CumulativeWeightedChoice((
    (30, lambda: f"Spell scroll (8th level) {random_spell(8)}"),
    (55, "Potion of storm giant strength"),
    (70, "Potion of supreme healing"),
    (85, lambda: f"Spell scroll (9th level) {random_spell(9)}"),
    (93, "Universal solvent"),
    (98, "Arrow of slaying"),
    (100, "Sovereign glue")
))

if __name__ == "__main__":
    print(note)
    num_selections = 10
    print(f"{num_selections} random selections:")
    for _ in range(num_selections):
        print(treasure_table_e())
