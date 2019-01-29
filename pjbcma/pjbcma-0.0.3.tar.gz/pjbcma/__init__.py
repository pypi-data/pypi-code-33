#this package contains convenience functions for handling
#the business of using Python 3.7 Jupyter Notebooks and
#the Python package pyjags, along with JAGS, to
#perform the code exercises in the textbook 
#Bayesian cognitive modeling: A practical course,
#by Lee, M. D., & Wagenmakers, E. J. (2014)

import pyjags

from .ModelHandler import ModelHandler
from .SampleHandler import SampleHandler
from .SimpleSampler import SimpleSampler


def demo():
	mydemo = """ spec_string = \"\"\"
model: #model code or local .txt file
model{
  for (i in 1:observationCount){ 
    testScores[i] ~ dnorm(mu, lambda)
  }
  mu ~ dunif(0,100)
  lambda ~ dgamma(.001,.001)
}

settings:
chains = 3 #number of chains to run
samples = 1000 #number of samples per chain
thinning = 0 #number of samples to discard between recorded samples
burnin = 500 #number of burn-in samples per chain

data:
testScores = [1,2,3,4,5,6,7,8] # can be integer or list
observationCount = len(testScores) # variables can be assigned using Python expressions

sample: #model variables to record, one per line
mu
lambda
\"\"\"

sampler = pjbcma.SimpleSampler(spec_string)

## optionally set data from outside the spec string
# sampler.set_data("testScores", [10, 20, 30, 40, 50, 60, 70, 80])
# sampler.set_data("observationCount", 8)

#take samples
samples = sampler.sample()

#see documentation for all visualization options
samples.summarize()
samples.vizchains("mu")
samples.vizhist("mu")
"""
	print(mydemo)




	




