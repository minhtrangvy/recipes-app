import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row


def get_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")
    return database_url


@contextmanager
def get_connection():
    with psycopg.connect(get_database_url(), row_factory=dict_row) as connection:
        yield connection
