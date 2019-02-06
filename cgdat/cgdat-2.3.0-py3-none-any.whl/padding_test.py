import numpy as np

#################################################
#### Add padding to bool array function        ###
#################################################
def padBoolArray(bool_array, n):


    ### Perform padding operation ###
    bool_array_padded = bool_array.copy()  # Make hardcopy so that we don't change the original object
    for index, item in enumerate(bool_array):  # Loop through the supplied bool array
        if item:  # If bool == True
            bool_array_padded[(index-n):(index+n+1)] = True  # Set n neighboors before and after also to true

    ### Return new padded list ###
    return bool_array_padded


bool_test = np.array([False, False, False, True, True, False, False, False, False, False, False, True, False, False, False])
test = padBoolArray(bool_test, 1)
print(test)