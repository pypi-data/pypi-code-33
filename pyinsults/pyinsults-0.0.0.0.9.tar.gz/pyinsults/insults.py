import random

adjectives = [
  "stinking",
  "whining",
  "pathetic",
  "ugly",
  "obnoxious",
  "low-life",
  "nasty-ass"
]

insults = [
  "asshole",
  "cumstain",
  "foolio",
  "dickwad",
  "Trump voter",
  "Justin Bieber fan",
  "retard",
  "fuckface",
  "cocksmoker",
  "shitgoblin",
  "jizztrumpet",
  "goatfucker",
  "motherfucker",
  "faglord",
]

def random_insult():
    return random.choice(insults)

def long_insult():
    return ' '.join([random.choice(adjectives), random.choice(insults)])