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


class AlreadyExists(Exception):
    pass


class Users:

    @staticmethod
    @postgres_wrapper
    def get(cursor, phone: str) -> User or None:
        cursor.execute(f"SELECT pk_id, phone, username FROM users WHERE phone = '{phone}'")
        res = cursor.fetchall()
        if res:
            return User(*res[0])
        else:
            None

    @staticmethod
    @postgres_wrapper
    def create(cursor, phone: str, username: str) -> User:
        try:
            cursor.execute(f"INSERT INTO users VALUES (DEFAULT, '{phone}', '{username}') RETURNING id")
        except psycopg2.Error:
            raise AlreadyExists()
        id_ = cursor.fetchall()[0][0]
        return User(id_, phone, username)
