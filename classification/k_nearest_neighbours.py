import numpy as np
import operator

class KNearestNeighbours:

    available_distance_functions = ['euclid', 'manhattan', 'chebyshev']

    # Optimal k from testing so far is k = 7, so it has been placed as default.
    # Optimal distance function so far is manhattan, so it has been placed as default.
    def __init__(self, k = 7, distance_function = 'manhattan'):
        self.k = k
        if (distance_function not in self.available_distance_functions):
            self.distance_function = 'manhattan'
        else:
            self.distance_function = distance_function

    def set_k(self, k):
        self.k = k

    def accuracy_score(self, y_true, y_pred):
        correct = 0
        for i in range(len(y_pred)):
            if (y_true[i] == y_pred[i]):
                correct += 1
        return correct / float(len(y_true)) * 100

    def euclid(self, a, b):
        return np.sqrt(np.sum((a - b) ** 2))

    def manhattan(self, a, b):
        return np.sum(abs(a - b))

    def chebyshev(self, a, b):
        return max(abs(a - b))

    def fit(self, X, Y):
        # Fit is a matter of adding this data to a local collection.
        self.X = np.copy(X)
        self.Y = np.copy(Y)

    def get_k_closest_neighbours(self, Xpred):
        distances = [[0 for j in range(len(self.X))] for i in range(len(Xpred))] 
        for i in range(len(Xpred)):
            for j in range(len(self.X)):
                distances[i][j] = (j, getattr(self, self.distance_function)(Xpred[i], self.X[j]))

        for i in range(len(distances)):
            distances[i].sort(key=operator.itemgetter(1))
        
        neighbours = [[] for i in range(len(Xpred))]
        for i in range(len(Xpred)):
            for x in range(self.k):
                neighbours[i].append(distances[i][x][0])

        return neighbours

    def votes(self, neighbours):
        results = []
        for row in neighbours:
            class_votes = {}
            for i in range(len(row)):
                vote = self.Y[row[i]]
                if vote in class_votes:
                    class_votes[vote] += 1
                else:
                    class_votes[vote] = 1
            results.append(sorted(class_votes.items(), key=operator.itemgetter(1), reverse = True)[0][0])
        return results
                
    def predict(self, Xpred):
        # For each point of X, find the nearest K neighbours and predict the class.
        neighbour_indeces = self.get_k_closest_neighbours(Xpred)
        return self.votes(neighbour_indeces)