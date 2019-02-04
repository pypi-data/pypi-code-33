import random


insults = ["kaka", "oetlul", "foolio"]


def random_insult():
  return random.choice(insults)


if __name__ == "__main__":
  random_insult()