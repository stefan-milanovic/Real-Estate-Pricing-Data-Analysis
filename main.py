import numpy as np

from k_nearest_neighbours import KNearestNeighbours
from linear_regression import PSZLinearRegression
from driver_regression import RealEstateAttributes
from driver_regression import load_from_database as load_db_regression
from driver_classification import load_from_database as load_db_classification
 
if __name__ == '__main__':
    print("Insert the following values to receive a price prediction for your real estate")

    # Ask the user for input.
    real_estate = []
    print("Location: ")
    real_estate.append(input())

    print("Square footage (m^2): ")
    real_estate.append(int(input()))

    print("Construction year: ")
    real_estate.append(int(input()))

    print("Floor: ")
    real_estate.append(int(input()))

    print("Rooms: ")
    real_estate.append(int(input()))

    attributes = RealEstateAttributes(real_estate[0], real_estate[1], real_estate[2], real_estate[3], real_estate[4])

    # Use regression to predict the expected price of the real estate.
    real_estates_train, prices_train = load_db_regression()

    regression_model = PSZLinearRegression()
    regression_model.fit(np.asarray(real_estates_train), np.asarray(prices_train))
    print("The predicted price for your real estate: ", np.round(regression_model.predict(np.asarray([attributes.toarray()]))[0], 2), "eur")

    # Use K Nearest Neighbours to classify the real estate into one of the price classes.
    classification_model = KNearestNeighbours()

    k_string = "(default = " + str(classification_model.k) + ")"
    print("Change the value of parameter k?", k_string)
    selection = input()
    
    if (selection.isnumeric()):
        classification_model.set_k(int(selection))
    
    real_estates_train, classes_train = load_db_classification()
    classification_model.fit(np.asarray(real_estates_train), np.asarray(classes_train))
    print("The predicted class for your real estate: ", classification_model.predict(np.asarray([attributes.toarray()]))[0])
