import random
from .guess import Guess

class Game:
    
    def __init__(self):
        self.correct_num = random.randint(1,21)
        self.play_game()
        
    def play_game(self):
        result = 0
        for i in range(1,10):
            if i == 1:
                guess_num = input("The computer has picked a number between 1 to 20. What's your guess: ")
                guess_obj = Guess(int(guess_num))
                result = guess_obj.eval_num(self.correct_num)
            else: 
                if result == 1:
                    guess_str = "The number you guessed is higher than the chosen number. What's your next guess: "
                elif result == -1:
                    guess_str = "The number you guessed is lower than the chosen number. What's your next guess: "
                else:
                    print("You win! You have guessed correct")
                    break
                guess_num = input(guess_str)
                guess_obj = Guess(int(guess_num))
                result = guess_obj.eval_num(self.correct_num)
                