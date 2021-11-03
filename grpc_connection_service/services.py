import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import sql
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Connection, Location, Person
from schemas import ConnectionSchema, LocationSchema, PersonSchema
from geoalchemy2.functions import ST_AsText, ST_Point

# ====================#
# == Define db == #
# ====================#

DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]

SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

# ====================#
# == Connect to db == #
# ====================#

from sqlalchemy import create_engine
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()

logging.basicConfig(level=logging.DEBUG)


class ConnectionService:
    @staticmethod
    def find_contacts(person_id: int, start_date: datetime,
                      end_date: datetime, meters: int
                      ) -> List[Connection]:
        """
        Finds all Person who have been within a given distance of a \
            given Person within a date range.

        This will run rather quickly locally, but this is an expensive \
            method and will take a bit of time to run on
        large datasets. This is by design: what are some ways or techniques\
            to help make this data integrate more
        smoothly for a better user experience for API consumers?
        """
        locations: List = session.query(Location).filter(
            Location.person_id == person_id
        ).filter(Location.creation_time < end_date).filter(
            Location.creation_time >= start_date
        ).all()

        # print("Locations :", locations)
        # print(locations[0].person_id,
        #      locations[0].coordinate,
         #     locations[0].creation_time)
        # print("LONGITUDE: ==> ", locations[0].longitude)

        my_persons = {person.id: person for person in PersonService.
                      retrieve_all()}
        # print("my_persons: ", my_persons)
        # print("1 person's data: ", my_persons[5].id, my_persons[5].first_name,
              # my_persons[5].last_name, my_persons[5].company_name)
        # print("my_persons keys :", *my_persons.keys())
        # Cache all users in memory for quick lookup
        person_map: Dict[str, Person] = {person.id: person for person in
                                         PersonService.retrieve_all()}

        # print("person_map :", person_map)
        # Prepare arguments for queries
        data = []
        for location in locations:
            print("Data :",
                  "person_id", person_id,
                  "longitude", location.longitude,
                  "latitude", location.latitude,
                  "meters", meters,
                  "start_date", type(start_date.strftime("%Y-%m-%d")),
                  "end_date", type((end_date + timedelta(days=1)).
                  strftime("%Y-%m-%d")),)

            data.append(
                {
                    "person_id": person_id,
                    "longitude": location.longitude,
                    "latitude": location.latitude,
                    "meters": meters,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": (end_date + timedelta(days=1)).
                    strftime("%Y-%m-%d"),
                }
            )
        # print("Data : ", data)
        query = text(
            """
        SELECT  person_id, id, ST_X(coordinate), ST_Y(coordinate), creation_time
        FROM    location
        WHERE   ST_DWithin(coordinate::geography,ST_SetSRID(ST_MakePoint(:latitude,:longitude),4326)::geography, :meters)
        AND     person_id != :person_id
        AND     TO_DATE(:start_date, 'YYYY-MM-DD') <= creation_time
        AND     TO_DATE(:end_date, 'YYYY-MM-DD') > creation_time;
        """
        )
        result: List[Connection] = []
        for line in tuple(data):
            for (
                exposed_person_id,
                location_id,
                exposed_lat,
                exposed_long,
                exposed_time,
            ) in engine.execute(query, **line):
                location = Location(
                    id=location_id,
                    person_id=exposed_person_id,
                    creation_time=exposed_time,
                )
                location.set_wkt_with_coords(exposed_lat, exposed_long)
                # print(type(location.creation_time))

                result.append(
                    Connection(
                        person=person_map[exposed_person_id], location=location,
                    )
                )
        # print(result)
        return result


class PersonService:

    @staticmethod
    def retrieve_all() -> List[Person]:
        print("I'm in personservice")
        return session.query(Person).all()
