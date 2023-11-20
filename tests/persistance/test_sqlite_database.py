import os
import sqlite3
import unittest
from queue import Queue
from unittest.mock import MagicMock

from models.company import Company
from persistance.sqlite_database import database_service
from utils.runtime_state import RuntimeState


class TestSqliteDatabaseService(unittest.TestCase):
    TEST_DB = "__test_db__.db"

    def setUp(self):
        RuntimeState.is_running = MagicMock(return_value=False)
        if os.path.exists(self.TEST_DB):
            os.remove(self.TEST_DB)

    def tearDown(self) -> None:
        os.remove(self.TEST_DB)

    def test_persist_workflow(self):
        persist_queue = Queue()
        company_1: Company = Company(
            name="Company name",
            linkedin="www.linkeding.com.br/Company name",
            segment="Digital Marketing",
            location="Remote",
            folowers="1000 folowers",
            employees="500+ employees",
        )
        company_2: Company = Company(
            name="Other Company name",
            linkedin="www.linkeding.com.br/other+Company+name",
            segment="Healthcare",
            location="Ney York",
            folowers="1,056,334 folowers",
            employees="1000+ employees",
        )
        persist_queue.put(company_1)
        persist_queue.put(company_2)

        database_service(persist_queue, self.TEST_DB)

        conn = sqlite3.connect(self.TEST_DB)
        cur = conn.cursor()
        stored_companies = cur.execute(
            """SELECT 
            name, 
            linkedin, 
            segment, 
            location,
            folowers,
            employees  
            FROM company
        """
        ).fetchall()

        self.assertEqual(len(stored_companies), 2)

        stored_company = stored_companies[0]
        self.assertEqual(stored_company[0], company_1.name)
        self.assertEqual(stored_company[1], company_1.linkedin)
        self.assertEqual(stored_company[2], company_1.segment)
        self.assertEqual(stored_company[3], company_1.location)
        self.assertEqual(stored_company[4], company_1.folowers)
        self.assertEqual(stored_company[5], company_1.employees)

        stored_company = stored_companies[1]
        self.assertEqual(stored_company[0], company_2.name)
        self.assertEqual(stored_company[1], company_2.linkedin)
        self.assertEqual(stored_company[2], company_2.segment)
        self.assertEqual(stored_company[3], company_2.location)
        self.assertEqual(stored_company[4], company_2.folowers)
        self.assertEqual(stored_company[5], company_2.employees)

    def test_schema_creation_and_empty_table(self):
        persist_queue = Queue()
        database_service(persist_queue, self.TEST_DB)

        conn = sqlite3.connect(self.TEST_DB)
        cur = conn.cursor()
        # This should success if the schema was created
        stored_companies = cur.execute(
            """SELECT 
            name, 
            linkedin, 
            segment, 
            location,
            folowers,
            employees  
            FROM company
        """
        ).fetchall()

        # Should have no entryes in the database
        self.assertEqual(len(stored_companies), 0)
