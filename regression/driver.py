import mysql.connector
import numpy as np
from linear_regression import PSZLinearRegression
from mysql.connector import Error

from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression, Ridge
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

    # Contains the price of the real estate from real_estates[i].
    prices = []

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
                    price_per_m2 = row[3]
                    prices.append(real_estate_attributes.square_footage * price_per_m2)
        
    except Error as e:
        print("==> Error while connecting to MySQL: ", e)
    
    finally:
        if (db_connection.is_connected()):
            cursor.close()
            db_connection.close()
            print("==> Disconnected from MySQL.")
        return real_estates, prices

def shuffle_arrays(a, b):
    assert len(a)==len(b)
    c = np.arange(len(a))
    np.random.shuffle(c)

    return a[c],b[c]

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
    real_estates, prices = load_from_database()
    real_estates_train, real_estates_test, prices_train, prices_test = split_test_train(real_estates, prices)

    # Test the model.

    # 1) The model with default parameters. Has given the best results.
    # Example RMSE: 58967.353090078206
    model = PSZLinearRegression()
    model.fit(real_estates_train, prices_train)
    price_predictions = model.predict(real_estates_test)
    print("RMSE = ", model.rmse(true = prices_test, pred = price_predictions))

    # 2) The model while using scaling of all the features to range [0, 1]. Has given the worst results.
    # Example RMSE: 10872742.71033323
    model = PSZLinearRegression(scaling=True)
    model.fit(real_estates_train, prices_train)
    price_predictions = model.predict(real_estates_test)
    print("RMSE_scaling = ", model.rmse(true = prices_test, pred = price_predictions))

    # 3) The model while using L2 regularisation. Has given results similar to model 1.
    # Example RMSE: 58967.40003870255
    model = PSZLinearRegression(l2 = True)
    model.fit(real_estates_train, prices_train)
    price_predictions = model.predict(real_estates_test)
    print("RMSE_l2_regularised = ", model.rmse(true = prices_test, pred = price_predictions))

    # Compare the results with sklearn's LinearRegression model.
    # Example RMSE: 59834.90062872186
    test_model = LinearRegression()
    test_model.fit(real_estates_train, prices_train)
    test_price_pred = test_model.predict(real_estates_test)
    print("RMSE_sklearn = ", mean_squared_error(y_true = prices_test, y_pred = test_price_pred, squared = False))

    # Plot a graph to compare the real and predicted values.

    # plt.xlabel('Construction Year')
    # plt.ylabel('Price')

    # plt.title('Real vs Predicted values comparison')
    # plt.scatter(real_estates_test[:, 2], prices_test)
    # plt.scatter(real_estates_test[:, 2], price_predictions)