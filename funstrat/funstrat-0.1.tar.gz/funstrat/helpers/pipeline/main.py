"""
This is a test pipeline system to run a strategy. Uses the chain of responsibility system to run through various indicators and a training step.

This is a strategy combined with a chain of command pattern. Where we can define a

"""
import random
from funstrat.helpers import Pipeline



class RandomPipelineBlock(object):
    def __init__(self):
        pass

    @property
    def is_feedforward(self):
        return False
    
    def process(self):
        return random.randint(0, 100)

class FeedForwardIncrement(object):
    def __init__(self):
        """Increments a number."""
        pass

    @property
    def is_feedforward(self):
        return True
    
    def process(self, last):
        # print(last)
        return last+1


        
            
    

if __name__ == "__main__":
    pipe = Pipeline()
    pipe.add(RandomPipelineBlock())
    pipe.add(FeedForwardIncrement())
    pipe.add(RandomPipelineBlock())
    pipe.add(RandomPipelineBlock())
    pipe.add(RandomPipelineBlock())
    
    # Allow us to append information into the
    
    final = pipe.run()
    print(final)