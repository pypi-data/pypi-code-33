def test(data):
    print(data)

class autoEncoder:
    # depth = number of hidden layers till middle, mid_width = nodes in middle,
    # lr = learning rate, initializing the class with default values, GD=numeric genotype
    def __init__(self):
        self.depth = 2;
        self.mid_width = 2;
        self.lr = 0.0003;
        self.GD = None;
        # null holder for network to be made
        self.netWork = None

    # load genotype
    def loadData(self, data):
        self.GD = data;

    # getters and setters
    def depth(self):
        x = self.depth
        return x

    def setD(self, D):
        self.depth = D

    def getMW(self):
        return self.mid_width

    def setMW(self, m):
        self.mid_width = m

    def getLR(self):
        return self.lr

    def setLR(self, L):
        self.lr = L

    def setPara(self, x, y, z):
        self.setD(x);
        self.setMW(y);
        self.setLR(z);

    # call all the dependencies I need
    def callDependencies(self):
        import pandas as pd
        import numpy as np
        from numpy import genfromtxt as gt
        import numpy as np
        import keras
        import math
        from keras.models import Sequential, Model
        from keras.layers import Dense
        from keras.optimizers import Adam
        from keras import regularizers
        from sklearn.model_selection import train_test_split
        from sklearn import preprocessing

        # prints all the parameters and returns them

    def printPara(self):
        x = self.depth
        y = self.mid_width
        z = self.lr
        tup = x, y, z
        print("depth =", x, ", mid_width =", y, ", learning rate =", z)
        return tup

    #############functions for networks####################
    #
    def createNetwork(self):
        # call dependencies to model
        self.callDependencies()
        from keras.models import Sequential, Model
        from keras.layers import Dense
        from keras.optimizers import Adam
        from keras import regularizers

        # fake list to put number of nodes for each layer in
        # treat it like a stack
        ls = []


        inShape = int(len(self.GD.columns))
        nD = self.mid_width

        # starting the model
        m = Sequential()
        # define first layer output
        if inShape > nD:
            out = int(round(inShape / 5))
        else:
            out = int(round(inShape * 2))

        # appending out into node stack
        ls.append(out)

        m.add(Dense(out, activation='elu', input_shape=(inShape,)))
        for i in range(0, self.depth-2):
            
            if inShape > nD:
                out = int(round((out) / 3))
            else:
                out = int(round((out) * 1.5))

            #making sure the layer dont get too small, but not doing if layer is expanding
            if inShape > nD:
                # dont let it get smaller then we want
                if out > nD:
                    node = out;
                        # if too small then go to smallest size use specified
                else:
                    node = nD;
            else:
                if out > nD:
                    node = out;
            # if too small then go to smallest size use specified
                else:
                    node = nD;
            
            # adding this layers nodes
            m.add(Dense(node, activation='elu'))
            # adding the number of nodes to pop off stack later
            ls.append(node);

        # make middle layer
        m.add(Dense(nD, activation='linear', name="bottleneck"))

        # use for loop to make decoder hidden layers
        for i in range(0, self.depth-2):
            # pops nodes needed from list
            node = ls.pop();
            # make layer with poped number of nodes from stack
            m.add(Dense(node, activation='elu'))

        # second to final layer
        m.add(Dense(ls.pop(), activation='elu'))

        # adding final layer
        m.add(Dense(inShape, activation='sigmoid'))
        # compile and print model
        m.compile(loss='mean_squared_error', optimizer=Adam(lr=self.lr))
        m.summary()
        # prints AE parameters
        self.printPara()

        return m;

    # making a function to train a network, what the user will call.
    def train(self, epochs=30, batch=32):
        import pandas as pd
        import numpy as np
        from numpy import genfromtxt as gt
        import numpy as np
        import keras
        import math
        from keras.models import Sequential, Model
        from keras.layers import Dense
        from keras.optimizers import Adam
        from keras import regularizers
        from sklearn.model_selection import train_test_split
        from sklearn import preprocessing

        # creates a network with the data
        m = self.createNetwork();
        # making training and testing data
        min_max_scaler = preprocessing.MinMaxScaler()
        x = min_max_scaler.fit_transform(self.GD)
        y = min_max_scaler.fit_transform(self.GD)

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.1)
        history = m.fit(x_train, y_train, batch_size=batch, epochs=epochs, verbose=1,
                        validation_data=(x_test, y_test))
        # extract encoder
        encoder = Model(m.input, m.get_layer('bottleneck').output)
        # making awesome prediction
        preds = encoder.predict(self.GD)

        return encoder, preds;


