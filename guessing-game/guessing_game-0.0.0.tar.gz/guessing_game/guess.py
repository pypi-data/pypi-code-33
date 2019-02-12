class Guess:

    def __init__(self, guess_num):
        self.guess_num = int(guess_num)
    
    def eval_num(self, correct_num):
        if self.guess_num == correct_num:
            return 0
        elif self.guess_num < correct_num:
            return -1
        else:
            return 1

