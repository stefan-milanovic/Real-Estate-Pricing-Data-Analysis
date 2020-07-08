import numpy as np

class PSZLinearRegression:
    def __init__(self, learning_rate=0.0000004, n_steps = 100000, l2 = False, scaling = False, lambda_ = 5):
        self.learning_rate = learning_rate,
        self.n_steps = n_steps
        self.scaling = scaling
        self.l2 = l2
        self.lambda_ = lambda_

    def mse(self, pred, true):
        return np.sum((true - pred) ** 2) / true.shape[0]

    def rmse(self, pred, true):
        return np.sqrt(self.mse(pred, true))

    def scale(self, X):
        # Performs normalisation.
        for i in range(X.shape[0]):
            X[i] = (X[i] - min(X[i])) / (max(X[i]) - min(X[i]))

    def calc_loss_function(self, X, Y):
        if (self.l2 == False):
            return 1/(2 * X.shape[0]) * np.dot(X.T, np.dot(X, self.W) - Y)
        else:
            return 1/(2 * X.shape[0]) * (np.dot(X.T, np.dot(X, self.W) - Y) + self.lambda_ * np.sum(self.W ** 2))

    def calc_gradient(self, X, Y):
        if (self.l2 == False):
            return 1/X.shape[0] * np.dot(X.T, (np.dot(X, self.W) - Y))
        else:
            return 1/X.shape[0] * (np.dot(X.T, (np.dot(X, self.W) - Y)) + self.lambda_ * self.W)

    def fit(self, X, Y):

        # Add the bias term.
        Xtrain = np.c_[np.ones(X.shape[0]), X]

        if (self.scaling):
            self.scale(Xtrain)

        # Randomly initialise weights.
        self.W = np.random.rand((Xtrain.shape[1]))

        # Iteratively update W for n_steps.
        for i in range(self.n_steps):
            self.W = self.W - self.learning_rate * self.calc_gradient(Xtrain, Y)

    def predict(self, X):
        Xpred = np.c_[np.ones(X.shape[0]), X]
        return np.dot(Xpred, self.W)