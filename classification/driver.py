import mysql.connector
import numpy as np
from k_nearest_neighbours import KNearestNeighbours
from mysql.connector import Error

from sklearn.metrics import mean_squared_error
from collections import Counter
import matplotlib.pyplot as plt

city_area_distances = { 
        'Stari Grad' : 0.4,
        'Vračar' : 2.7,
        'Savski Venac' : 4.8,
        'Novi Beograd' : 9.0,
        'Rakovica' : 13.2,
        'Čukarica' : 21.1,
        'Voždovac' : 5.0,
        'Zvezdara' : 3.9,
        'Zemun' : 12.8,
        'Palilula' : 24.6,
        'Mladenovac' : 53.1,
        'Grocka' : 37.3,
        'Obrenovac' : 33.1,
        'Surčin' : 24.2,
        'Barajevo' : 33.9,
        'Lazarevac' : 61.3
    }

class RealEstateAttributes:
    
    def __init__(self, location, square_footage, construction_year, floor, rooms):
        self.location = location
        self.square_footage = square_footage
        self.construction_year = construction_year
        self.floor = floor
        self.rooms = rooms        
        self.distance = city_area_distances[location] if location in city_area_distances else -1

    def toarray(self):
        return [self.distance, self.square_footage, self.construction_year, self.floor, self.rooms]

def load_from_database():
    # Array of attributes.
    real_estates = []

    # Contains the class for each real_estate[i].
    classes = []

    class_boundaries = [49999, 99999, 149999, 199999]
    class_names = ["< 50 000eur", "50 000 - 99 999eur", "100 000 - 149 999 eur", "150 000 - 199 999 eur", "> 200 000 eur"]

    try:
        db_connection = mysql.connector.connect(host='localhost', database='real_estate', user='root', password='root')
        if (db_connection.is_connected()):
            print("==> Connected to MySQL.")
            cursor = db_connection.cursor()

            sql_select_query = '''
            SELECT * FROM real_estate.real_estate AS RE 
            WHERE RE.city = \'Beograd\' AND RE.offer_type = \'sale\' AND RE.type = \'flat\'
            AND RE.construction_year IS NOT NULL AND RE.floor IS NOT NULL AND RE.rooms IS NOT NULL
            '''

            cursor.execute(sql_select_query)
            data = cursor.fetchall()

            for row in data:
                real_estate_attributes = RealEstateAttributes(row[5], row[6], row[7], row[9], int(row[13]))
                if (real_estate_attributes.location in city_area_distances):
                    real_estates.append(real_estate_attributes.toarray())
                    
                    # Calculate class.
                    real_estate_price = real_estate_attributes.square_footage * row[3]
                    
                    for i in range(0, len(class_boundaries)):
                        if (real_estate_price <= class_boundaries[i]):
                            classes.append(class_names[i])
                            break

                    if (real_estate_price >= class_boundaries[len(class_boundaries) - 1]):
                        classes.append(class_names[len(class_boundaries)])
        
    except Error as e:
        print("==> Error while connecting to MySQL: ", e)
    
    finally:
        if (db_connection.is_connected()):
            cursor.close()
            db_connection.close()
            print("==> Disconnected from MySQL.")
        return real_estates, classes

def shuffle_arrays(a, b):
    assert len(a)==len(b)
    c = np.arange(len(a))
    np.random.shuffle(c)

    return a[c],b[c]

def stratified_split_test_train(X, Y, test_size = 0.2):

    # Shuffle.
    X_shuffled, Y_shuffled = shuffle_arrays(np.asarray(X), np.asarray(Y))

    # Count elements of each class.
    counter = Counter(Y_shuffled)

    count_in_test = {}
    
    for element in counter:
        count_in_test[element] = int(np.round(test_size * counter[element]))

    # Fill in the result arrays.
    X_train = []
    X_test = []
    Y_train = []
    Y_test = []

    for i in range(X_shuffled.shape[0]):
        if (count_in_test[Y_shuffled[i]] != 0):
            X_test.append(X_shuffled[i])
            Y_test.append(Y_shuffled[i])
            count_in_test[Y_shuffled[i]] -= 1
        else:
            X_train.append(X_shuffled[i])
            Y_train.append(Y_shuffled[i])

    return (np.asarray(X_train), np.asarray(X_test), np.asarray(Y_train), np.asarray(Y_test))

def split_test_train(X, Y, test_size = 0.2):
    
    # Shuffle.
    X_shuffled, Y_shuffled = shuffle_arrays(np.asarray(X), np.asarray(Y))

    # Split.
    train_count = len(X_shuffled) - round(test_size * len(X_shuffled))

    X_train = X_shuffled[:train_count]
    X_test = X_shuffled[train_count:]
    
    Y_train = Y_shuffled[:train_count]
    Y_test = Y_shuffled[train_count:]

    return (X_train, X_test, Y_train, Y_test)

if __name__ == '__main__':
    real_estates, classes = load_from_database()
    real_estates_train, real_estates_test, classes_train, classes_test = stratified_split_test_train(real_estates, classes, test_size=0.2)
    
    # Test the model.

    for distance_function in ['euclid', 'manhattan', 'chebyshev']:
        for k in range(1, int(np.round(np.sqrt(real_estates_train.shape[0]))), 2):
         model = KNearestNeighbours(k = k, distance_function = distance_function)
         model.fit(real_estates_train, classes_train)
         predictions = model.predict(real_estates_test)
         
         k_string = "(k = " + str(model.k) + ", "
         distance_string = "distance_function = " + model.distance_function + ") ="
         print("Accuracy", k_string, distance_string, model.accuracy_score(y_true = classes_test, y_pred = predictions))
    