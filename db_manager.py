import psycopg2
import dataclasses
import datetime as dt

pg_database = 'hakaton'
pg_username = 'postgres'
pg_password = 'postgres'
pg_host = '127.0.0.1'


def postgres_wrapper(func):
    def wrap(*args, **kwargs):
        with psycopg2.connect(dbname=pg_database,
                              user=pg_username,
                              password=pg_password,
                              host=pg_host) as conn:
            with conn.cursor() as cursor:
                return func(cursor, *args, **kwargs)

    return wrap


@dataclasses.dataclass
class User:
    id: int
    phone: str
    username: str


@dataclasses.dataclass
class Emotion:
    id: int
    user_id: int
    value: int
    title: str
    description: str
    timestamp: dt.datetime


@dataclasses.dataclass
class Group:
    id: int
    owner_id: int


@postgres_wrapper
def ping(cursor):
    try:
        cursor.execute("SELECT * FROM users")
        cursor.fetchall()
        return True
    except Exception as e:
        return False
