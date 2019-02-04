import random

adjectives = ["stinking", "whining", "pathetic"]

insults = ["asshole", "cumstain", "foolio", "dickwad", "Trump voter"]

def random_insult():
  return random.choice(insults)

def long_insult():
  return ''.join(random.choice(adjectives), random.choice(insults))


if __name__ == "__main__":
  random_insult()