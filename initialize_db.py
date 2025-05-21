from shared.models.ORM import UsersBase, RequestsBase
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, drop_database, create_database

DB_URI = "postgresql+psycopg2://myuser:mypassword@44.204.22.70:5432"
USERS_DB = DB_URI + "/users"
REQUESTS_DB = DB_URI + "/requests"


def deleteDbs() -> None:
    if database_exists(USERS_DB):
        drop_database(USERS_DB)
    if database_exists(REQUESTS_DB):
        drop_database(REQUESTS_DB)


def initializeUsersDb() -> None:
    create_database(USERS_DB)
    engine = create_engine(USERS_DB)
    UsersBase.metadata.create_all(engine)


def initializeRequestsDb() -> None:
    create_database(REQUESTS_DB)
    engine = create_engine(REQUESTS_DB)
    RequestsBase.metadata.create_all(engine)


def main() -> None:
    deleteDbs()
    initializeUsersDb()
    initializeRequestsDb()


main()
