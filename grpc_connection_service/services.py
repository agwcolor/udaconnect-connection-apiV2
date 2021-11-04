import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Location, Person
import connection_pb2
import connection_pb2_grpc

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


class ConnectionService(connection_pb2_grpc.ConnectionServiceServicer):
    @staticmethod
    def find_contacts(person_id: int, start_date: datetime,
                      end_date: datetime, meters: int
                      ):
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
        # Cache all users in memory for quick lookup
        person_map: Dict[str, Person] = {person.id: person for person in
                                         PersonService.retrieve_all()}
        # Prepare arguments for queries
        data = []
        for location in locations:
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
        # result: List[Connection] = []
        result = connection_pb2.ConnectionMessageList()
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

                # map results to grpc protobuf types
                location_proto = connection_pb2.Location()
                location_proto.longitude = location.longitude
                location_proto.latitude = location.latitude
                location_proto.creation_time = (location.creation_time).strftime("%Y-%m-%d")
                location_proto.id = location.id

                exposed_person = person_map[exposed_person_id]
                person_proto = connection_pb2.Person()
                person_proto.id = exposed_person.id
                person_proto.first_name = exposed_person.first_name
                person_proto.last_name = exposed_person.last_name
                person_proto.company_name = exposed_person.company_name

                connection_proto = connection_pb2.Connection()

                connection_proto.location.CopyFrom(location_proto)
                connection_proto.person.CopyFrom(person_proto)
                result.connections.append(connection_proto)
        return result


class PersonService:

    @staticmethod
    def retrieve_all() -> List[Person]:
        return session.query(Person).all()
