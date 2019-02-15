import numpy as np
from scipy.stats import linregress

def best_fit(data):
    x = np.arange(0,len(data))
    y = np.array(data)
    slope, intercept, r_value, p_value, std_err = linregress(x,y)
    # z = np.polyfit(x,y,1)
    return slope, intercept, r_value, p_value, std_err

if __name__ == "__main__":    
    x = [12, 34, 29, 38, 34, 51, 29, 34, 47, 34, 55, 94, 68, 81]
    print(best_fit(x))