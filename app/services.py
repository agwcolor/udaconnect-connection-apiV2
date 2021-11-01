import logging
from datetime import datetime, timedelta
from typing import Dict, List
from app import db
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request, g, Response, current_app


from app.models import Connection, Location, Person
from app.schemas import ConnectionSchema, LocationSchema, PersonSchema
from geoalchemy2.functions import ST_AsText, ST_Point
from sqlalchemy.sql import text

logging.basicConfig(level=logging.DEBUG)


class ConnectionService:
    @staticmethod
    def find_contacts(person_id: int, start_date: datetime,
                      end_date: datetime, meters=5
                      ) -> List[Connection]:
        """
        Finds all Person who have been within a given distance of a given Person within a date range.

        This will run rather quickly locally, but this is an expensive method and will take a bit of time to run on
        large datasets. This is by design: what are some ways or techniques to help make this data integrate more
        smoothly for a better user experience for API consumers?
        """
        locations: List = db.session.query(Location).filter(
            Location.person_id == person_id
        ).filter(Location.creation_time < end_date).filter(
            Location.creation_time >= start_date
        ).all()

        print("Locations :", locations)
        print(locations[0].person_id,
              locations[0].coordinate,
              locations[0].creation_time)

        my_persons = {person.id: person for person in PersonService.
                      retrieve_all()}
        print(my_persons)
        print(my_persons[5].id, my_persons[5].first_name,
              my_persons[5].last_name, my_persons[5].company_name)
        print(*my_persons.keys())
        # Cache all users in memory for quick lookup
        person_map: Dict[str, Person] = {person.id: person for person in
                                         PersonService.retrieve_all()}

        print("person_map :", person_map)
        # Prepare arguments for queries
        data = []
        for location in locations:
            print("Data :",
                  "person_id", person_id,
                  "longitude", location.longitude,
                  "latitude", location.latitude,
                  "meters", meters,
                  "start_date", start_date.strftime("%Y-%m-%d"),
                  "end_date", (end_date + timedelta(days=1)).
                  strftime("%Y-%m-%d"),)

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
        print("Data : ", data)
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
            ) in db.engine.execute(query, **line):
                location = Location(
                    id=location_id,
                    person_id=exposed_person_id,
                    creation_time=exposed_time,
                )
                location.set_wkt_with_coords(exposed_lat, exposed_long)

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
        return db.session.query(Person).all()
