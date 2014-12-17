import numpy as np  
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.grid_search import GridSearchCV
from multiprocessing import cpu_count
from sklearn.metrics import f1_score


# Solution for trying to train with all instances having single label
class TrivialClassifier:

    def __init__(self, label):
        self.label = label

    def predict(self, X):
        return [ self.label for x in X ]



def train(X, Y, do_grid, default_label=0):

    # If there are no training examples, then you need a classifier that returns the default label
    if len(Y) == 0:
        return TrivialClassifier(default_label)

    # scikit-learn requires you train data with more than one label
    if len(Y) and all( [ (y==Y[0]) for y in Y ] ):
        return TrivialClassifier(Y[0])

    # Search space
    C_range     = 10.0 ** np.arange( -5, 9 )
    gamma_range = 10.0 ** np.arange( -5 , 9 )

    # Grid search?
    if do_grid:
        print '\t\tperforming grid search'

        estimates = LinearSVC() 
        parameters = [ {'C':C_range } ]
            
        # Find best classifier
        clf = GridSearchCV(estimates, parameters, score_func = f1_score, 
                           n_jobs = cpu_count()                        )
        clf.fit(X, Y)

    else:
        clf = LinearSVC()
        clf.fit(X, Y)

    # Return chosen classifier
    return clf



def predict(clf, X):
    # Predict
    retVal = list(clf.predict(X))
    return retVal
