import mysql.connector
import json
from mysql.connector import Error

class RealEstate:

    real_estate_type = None
    offer_type = None
    price_per_m2 = None
    city = None
    city_area = None
    square_footage = None
    construction_year = None
    land_size = None
    floor = None
    floors_in_building = None
    registered = None
    heating = None
    rooms = None
    bathrooms = None

    def parse_json(self, data):
        self.parse_type_and_offer_type(data['offer_type'])
        self.parse_price(data['price_per_m2'])

        self.city = data['city']
        self.city_area = data['city_area']

        self.parse_square_footage(data['square_footage'])

        self.parse_construction_year(data['construction_year'])
        self.land_size = None

        self.parse_floors(data['floor'], data['floors_in_building'])
        self.parse_registered(data['registered'])

        self.heating = data['heating']
        self.parse_rooms(data['rooms'])

        self.parse_additional_info(data['additional_info'])

    def parse_type_and_offer_type(self, data):
        info = data.split()
        self.real_estate_type = 'flat' if info[1] == 'stanova' else 'house'
        self.offer_type = 'sale' if info[0] == 'Prodaja' else 'rent'

    def parse_price(self, data):
        priceRaw = data.split()[0]
        # Remove thousands separator from the raw number.
        self.price_per_m2 = int(priceRaw.replace('.',''))

    def parse_square_footage(self, data):
        self.square_footage = data.split()[0]

    def parse_construction_year(self, data):
        if (data != ''):
            self.construction_year = int(data)

    def parse_floors(self, data_floor, data_floors_in_building):
        if (data_floor != ''):
            if (data_floor.strip() == 'Potkrovlje'):
                if (data_floors_in_building.isnumeric()):
                    self.floor = int(data_floors_in_building)
                else:
                    self.floor = 0
            else:
                if (data_floor.strip() in ['Prizemlje', 'Nisko prizemlje', 'Podrum', 'Suteren']):
                    self.floor = 0
                else:
                    self.floor = int(data_floor.rstrip())

        if (data_floors_in_building != '' and data_floors_in_building.isnumeric()):
            self.floors_in_building = int(data_floors_in_building)

    def parse_registered(self, data):
        if (data == 'Uknji\u017eeno'):
            self.registed = True
        else:
            self.registered = False

    def parse_rooms(self, data):
        if (data != ''):
            self.rooms = float(data)

    def parse_additional_info(self, data):
        if (data != ''):
            info = data.split()
            if (info[0] == 'Kupatilo'):
                self.bathrooms = info[1]

    def insert_to_database(self, cursor):
        add_real_estate = ("INSERT INTO real_estate "
               "(type, offer_type, price_per_m2, city, city_area, square_footage, construction_year, land_size, floor, floors_in_building, registered, heating, rooms, bathrooms) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

        real_estate_data = (
            self.real_estate_type,
            self.offer_type,
            self.price_per_m2,
            self.city,
            self.city_area,
            self.square_footage,
            self.construction_year,
            self.land_size,
            self.floor,
            self.floors_in_building,
            self.registered,
            self.heating,
            self.rooms,
            self.bathrooms
        )

        cursor.execute(add_real_estate, real_estate_data)

if __name__ == "__main__":
    
    input_file_path  = 'output/4zida.json'
    try:
        db_connection = mysql.connector.connect(host='localhost', database='real_estate', user='root', password='root')
        if (db_connection.is_connected()):
            print("==> Connected to MySQL.")
            cursor = db_connection.cursor()

            with open(input_file_path, 'r') as input_file:
                print("==> Opened input file.")
                contents = json.load(input_file)
                for real_estate_info in contents:
                    real_estate_buffer = RealEstate()
                    real_estate_buffer.parse_json(real_estate_info)
                    real_estate_buffer.insert_to_database(cursor)
                db_connection.commit()

            print("==> Closed input file.")
    except Error as e:
        print("==> Error while connecting to MySQL: ", e)
    
    finally:
        if (db_connection.is_connected()):
            cursor.close()
            db_connection.close()
            print("==> Disconnected from MySQL.")