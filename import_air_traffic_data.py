import csv
import os
from py2neo import Graph, Node, Relationship

def create_node_relationship(node_a, node_b, leg, graph_object):
    a = Node("Airport",lat=node_a["latitude"],
                        lon=node_a["longitude"],
                        name=node_a["name"],
                        location=node_a["location"],
                        state=node_a["state"],
                        country=node_a["country"],
                        start_date=node_a["start-date"],
                        code=node_a["code"])
    a.__primarylabel__ = "name"
    a.__primarykey__ = "name"
    b = Node("Airport",lat=node_b["latitude"],
                        lon=node_b["longitude"],
                        name=node_b["name"],
                        location=node_b["location"],
                        state=node_b["state"],
                        country=node_b["country"],
                        start_date=node_b["start-date"],
                        code=node_b["code"])
    b.__primarylabel__ = "name"
    b.__primarykey__ = "name"
    connection = Relationship.type("CONNECTION")
    graph_object.merge(connection(a,b, airline=leg))

def main():
    input_flights = './269269812_T_T100_SEGMENT_ALL_CARRIER.csv'
    input_airports = './454489447_T_MASTER_CORD.csv'

    airport_locations = {}
    nodes = {}
    legs = []

    g = Graph("bolt://localhost:7687", auth=("neo4j", "gis12345"))
    print("Successfully connected to Graph!")

    print("Building look-up dictionary of airport locations.")

    with open(input_airports, "r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        count=0
        for row in csvreader:  
            if count == 0:
                pass
            else:
                AIRPORT = row[0]
                DISPLAY_AIRPORT_NAME = row[1]
                DISPLAY_AIRPORT_CITY_NAME_FULL = row[2]
                AIRPORT_COUNTRY_CODE_ISO = row[3]
                AIRPORT_STATE_CODE = row[4]
                LATITUDE = row[5]
                LONGITUDE = row[6]
                AIRPORT_START_DATE = row[7]
                airport_locations[AIRPORT] = {"latitude":LATITUDE,
                                                "longitude":LONGITUDE,
                                                "name": DISPLAY_AIRPORT_NAME,
                                                "location": DISPLAY_AIRPORT_CITY_NAME_FULL,
                                                "state": AIRPORT_STATE_CODE,
                                                "country": AIRPORT_COUNTRY_CODE_ISO,
                                                "start-date": AIRPORT_START_DATE,
                                                "code": AIRPORT}

            count +=1

    print("Building flight tracks.")

    with open(input_flights, "r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        count = 0
        for row in csvreader:
            if count == 0:
                pass
            else:
                PAYLOAD = float(row[2])
                SEATS = float(row[3])
                PASSENGERS = float(row[4])
                FREIGHT = float(row[5])
                MAIL = float(row[6])
                DISTANCE = float(row[7])
                RAMP_TO_RAMP = float(row[8])
                AIR_TIME = float(row[9])
                UNIQUE_CARRIER = row[12]
                ORIGIN = row[22]
                DEST = row[33]

                if SEATS > 0 and PASSENGERS > 0:
                    percent_full = float((PASSENGERS / SEATS) * 100)
                else:
                    percent_full = 0
                leg = (ORIGIN, DEST, UNIQUE_CARRIER)
                if leg not in legs:
                    legs.append(leg)

                origin_coords = airport_locations[ORIGIN]
                dest_coords = airport_locations[DEST]

                if ORIGIN not in nodes.keys():
                    nodes[ORIGIN] = {
                        "latitude":origin_coords["latitude"],
                        "longitude":origin_coords["longitude"],
                        "name": origin_coords["name"],
                        "location": origin_coords["location"],
                        "state": origin_coords["state"],
                        "country": origin_coords["country"],
                        "start-date": origin_coords["start-date"],
                        "code": ORIGIN
                    }

                if DEST not in nodes.keys():
                    nodes[DEST] = {
                        "latitude":origin_coords["latitude"],
                        "longitude":origin_coords["longitude"],
                        "name": origin_coords["name"],
                        "location": origin_coords["location"],
                        "state": origin_coords["state"],
                        "country": origin_coords["country"],
                        "start-date": origin_coords["start-date"],
                        "code": DEST
                    }

            count +=1

    count = 0
    for leg in legs:
        create_node_relationship(airport_locations[leg[0]], airport_locations[leg[1]], leg[2], g)
        count +=1
        
        print(str((count / len(legs)) * 100) + '%' + " complete")

if __name__ == "__main__":
    main()