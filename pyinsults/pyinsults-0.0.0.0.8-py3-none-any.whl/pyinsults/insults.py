import random

adjectives = ["stinking", "whining", "pathetic", "ugly", "obnoxious", "low-life"]
insults = ["asshole", "cumstain", "foolio", "dickwad", "Trump voter", "Justin Bieber fan"]

def random_insult():
  return random.choice(insults)

def long_insult():
  return ' '.join([random.choice(adjectives), random.choice(insults)])

if __name__ == "__main__":
  random_insult()