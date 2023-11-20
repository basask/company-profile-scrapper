import logging as log
import os
import signal
import sqlite3
import time
from multiprocessing import Queue

from models.company import Company
from utils.runtime_state import RuntimeState

""" Using the clean Sqlite3 interfaces dealing directly with connection and cursor
object is not optimal for small and big systems. 
This wil works given this is small script not intendet to become a production system.
For I production systems a more robust solution would be needed.
Ideas on top of my head: Using SQLAlchemy for ORM + Alembic for schema management 
"""


def create_schema(conn: sqlite3.Connection):
    """Creates the company schema at sqlite3 database

    Arguments:
    conn: sqlite3.Connection -- Connection to a sqlite database
    """
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS company (name, linkedin, segment, location, folowers, employees)"
    )


def database_service(persist_queue: Queue, db_name: str):
    """Database service main function.
    This service will pull data out of the 'persist_queue' and stores at
    the database defined by 'db_name'

    Arguments:
    persist_queue: Queue -- Queue to fetch data from
    db_name: String -- Name of the database to connect to
    """
    pid = os.getpid()
    log.info(f"[pid={pid}] DatabaseService waiting data")

    runtime = RuntimeState()
    signal.signal(signal.SIGTERM, runtime.handle_signal)

    conn = sqlite3.connect(db_name)
    create_schema(conn)

    data = []
    while True:
        if persist_queue.empty():
            if not runtime.is_running():
                break
            # Sleeping for cases when this function is used as proccess body (current use case)
            # For other use cases not multiprocesses this might be removed
            time.sleep(1)
            continue

        # TODO(DB01) [High coupled] Abstract the model structure out of the database service
        company: Company = persist_queue.get()
        log.info(f"[pid={pid}] DatabaseService Receive data company={company.name}")
        data.append(
            (
                company.name,
                company.linkedin,
                company.segment,
                company.location,
                company.folowers,
                company.employees,
            )
        )

    log.info(f"[pid={pid}] DatabaseService commiting database changes")
    cursor = conn.cursor()
    cursor.executemany(
        """INSERT INTO company (name, linkedin, segment, location, folowers, employees) 
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
        data,
    )
    conn.commit()
    conn.close()

    log.info(f"[pid={pid}] DatabaseService finish persisting data")
