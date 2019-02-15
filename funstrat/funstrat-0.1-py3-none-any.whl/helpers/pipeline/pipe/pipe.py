from funstrat.helpers.pipeline.blocks.others import IndicatorBlock
from funstrat.helpers.pipeline.blocks.base import BaseBlock

import dask
class Pipeline(object):
    def __init__(self):
        """
            The pipeline is a mega strategy. 
            It should be used in conjunction with machine learning and indicators 
            Ideal Example:

            # The session code will reorientate itself after each add to make sense
            sess = Session(live=False, training=True)
            # Figure out the portfolio thing at some point.
            sess.add(Portfolio()) # Use Ray to setup portfolio objects. Can use with many items
            sess.add(LSTM()) # USE Ray to setup LSTM Training
            sess.add(ReinforcementAgent()) # Use with ray to set reinforcement agent here
            sess.add(ParameterServer(_types=['bayesian', 'meta-estimator'])) # Use ray to set a parameter server on here as well. Can use with pipeline system
            sess.add(StorageSystem(**storage_information))
            sess.add(SampleSet(barframe_1, barframe_2, barframe_3)) # We can use a class like this session to 
            sess.add(GlobalLog(types=["SQL", "File"], database_params={dictionary of parameters goes here}))
            sess.add(GenerateSample(_type="stochastic"))
            sess.add(GenerateSample(_type="deepmarkov"))
            # This session would generate a graph for everything to run on using a prebuilt networkx graph (eventually)
            # The networkx graph would be copied
            
            # Use the session to appropiate machine learning and ordering to the various bars

            sample_set = sess.get_sample_bars() # returns an object to help iterate
            
            # This is basically a dream list. Lets start with building indicators after getting a target audience.
            for bars in sample_set:
                while is_bars():
                    # Use *args to add different dataframes based on different types in future?
                    strategy = Pipeline(barframe, train_session=sess)
                    # Use strategy to add other processing blocks as well (Sentiment, News Events)
                    strategy.add(RSIIndicator(window=16, top=60, bottom=35)) # maybe get parameters from session
                    strategy.add(ATRIndicator(window=16, top=60, bottom=35))
                    strategy.add(FIBIndicator(window=16, top=60, bottom=35))
                    strategy.add(SqueezeIndicator(window=16, top=60, bottom=35))
                    ...
                    ...
                    strategy.run() # Run gets the graph up to this point and processes everything. Start with a list
            
            The strategy will then run and deliver a result:
                - Because this is an event driven system we should pipe the decisions to something
                - The pipe will be the portflio we add in.
                - To train machine learning on event driven knowledge we can pipe information using session information
                - Inside of run, try setting everything necessary for the session to run in place.
        """ 
        self.pipeline = []
        self.index = 0
        # We can even store results by type to ensure each block processes them correctly.
        self.results = []
        # print("Starting pipeline")
    
    def add(self, strategy):
        # Each processor sends information into the next processor
        # Make sure the class here is an instance of a processing block.
        # print(strategy)
        if not isinstance(strategy, BaseBlock):
            return

        self.pipeline.append(strategy)

    
    def end(self):
        # NOTE: Returns a boolean explaining wether we're at the end of the processing blocks.
        return ((self.index + 1) > len(self.pipeline))

    def next(self):
        # How to feed it in to the next?
        # location = self.index
        if not self.end():
            if self.index == 0:
                r = self.pipeline[self.index]
                self.index = self.index+1
            
                return r
            r = self.pipeline[self.index]
                # next_index = location + 1
            self.index = self.index + 1
            return r
    
    def process_next(self):
        n = self.next()
        result = None
        # Here we determine how to process the next block.
        # TODO: The next version will sort the order of blocks before processing them
        result = dask.delayed(n.process)(self.barframe)
        self.results.append(result)
    def _process_all(self):
        """ 
            How to get the most recent result to process the next block? 
            # Also run checks to see if we're dealing with a simple indicator (using only OCHL data)
            # if so we only need the data added in the constructor
            
            if self.next().is_feedforward() == True:
                # Check to see if there's any results
                if len(self.results) == 0:
                    # Also check to see if we've added something into the constructor we haven't gone over.
                    raise ValueError("There's nothing fed into the block ...")
                # Get the last result
                # Self.results[-1]

        """
        while not self.end():


            self.process_next()
        res = dask.compute(*self.results)
        self.results = []
        return list(res)

    def step(self, barframe):
        """ Run through each block and train as you go"""
        self.index = 0
        self.barframe = barframe
        return self._process_all()