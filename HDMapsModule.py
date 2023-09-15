import psycopg2
import os
# from HDMaps import lanes, signs, map_operators
import lanes
import signs


class HDMapsModule:
    def __init__(self):
        #Connect to database
        '''
            Example variables:
                DB_USERNAME - postgres
                DB_PASSWORD - psuavt
                DB_NAME - MCity Map
                DB_HOSTNAME - postgres
                DB_PORT - 5432
        '''
        # uname = os.environ['DB_USERNAME']
        # passw = os.environ['DB_PASSWORD']
        # db_name = os.environ['DB_NAME']
        # db_host = os.environ['DB_HOSTNAME']
        # db_port = os.environ['DB_PORT']

        uname = "psuavt"
        passw = "psuavt"
        db_name = "MCity"
        db_host = "127.0.0.1"
        db_port = "5432"

        #Check if environment variables are set
        if not uname:
            raise Exception('Database username not specified in environment variable DB_USERNAME')

        if not passw:
            raise Exception('Database password not specified in environment variable DB_PASSWORD')

        if not db_name:
            raise Exception('Database name not specified in environment variable DB_NAME')

        if not db_host:
            raise Exception('Database hostname not specified in environment variable DB_HOTNAME')

        if not db_port:
            raise Exception('Database port not specified in environment variable DB_PORT')

        #Connect to database
        self.conn = psycopg2.connect(database=db_name, user=uname, password=passw, host=db_host, port=db_port)
        self.cur = self.conn.cursor()

        self.__lanes = lanes.lanes_init(self.cur)
        self.__signs = signs.signs_init(self.cur)


    def disconnect(self):
        self.cur.close()
        self.conn.close()

    def get_lanes(self):
        return self.__lanes

    def get_signs(self):
        return self.__signs

def road_names(self):

    road_names = {
        1: "Pontiac Trail",
        2: "Depot Street",
        3: "Carrier & Gable Drive",
        4: "State Street",
        5: "Liberty Street",
        6: "Main Steet",
        7: "Wolverine Avenue"
    }
    
    ''' 
    Route starts on Liberty St. going West, turning left onto Pontiac Trail. After moving south on Pontiac Trail we make a left onto State Steet. 
    Following state Street NE, follow the round about to the left, continuing onto State Street. Continue north till making a right onto Carrier
    and Gable, going north east till finishing at the top of C&G
    to finish the track. 
    '''

    return road_names

