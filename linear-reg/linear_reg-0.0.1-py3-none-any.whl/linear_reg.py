import numpy as np
from matplotlib import pyplot as plt


class Batch_gradient_descent:

    def cost_function(self,X, Y, B):
        m = len(Y)
        J = np.sum((X.dot(B) - Y) ** 2)/(2 * m)
        return (J)


    def fit(self,X, Y, alpha=0.005, iterations=400):

        B = np.zeros(X.shape[1])
        cost_history = [0] * iterations
        
        m = len(Y)

        print('training initialized.. \n\n')         
        
        for iteration in range(iterations):
            #print(iteration)
            # Hypothesis Values
            h = X.dot(B)
            # Difference b/w Hypothesis and Actual Y
            loss = h - Y
            # Gradient Calculation
            gradient = X.T.dot(loss) / m
            # Changing Values of B using Gradient
            B = B - alpha * gradient
            # New Cost Value
            cost = self.cost_function(X, Y, B)
            cost_history[iteration] = cost

        self.X = X
        self.y = Y
        self.iter = iterations
        self.theta = B
        self.cost_history = cost_history

        print("Report:\ntotal samples: {}\ntotal iterations: {}\nfinal loss/cost: {}\n\noptimum theta : {}".format(len(Y),iterations,cost,B))
        return self.theta, self.cost_history

    def r2_score(self):

        y_ = self.X.dot(self.theta)
    
        sst = np.sum((self.y-self.y.mean())**2)
        ssr = np.sum((y_-self.y)**2)
        r2 = 1-(ssr/sst)
        return(r2)

    def rmse(self):
        y_ = self.X.dot(self.theta)
        
        ssr = np.sum((y_-self.y)**2)
        mse = ssr/len(y_)
        
        return(np.sqrt(mse))

    def predict(self,X):
        y_ = X.dot(self.theta)
        return(y_)

    def plot_result(self):
        plt.scatter(np.arange(self.iter),self.cost_history,s=2)
        plt.show()

def normal_equation(X,y):
    
    theta_best = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)
    return(theta_best)

def ols_simple(x,y):
    y_ = y.mean()
    x_ = x.mean()

    b1 = np.sum((y-y_)*(x-x_))/np.sum((x-x_)**2)
    b0 = y_- b1*x_
    return(b0,b1)
    
