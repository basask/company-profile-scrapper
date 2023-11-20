import argparse
import configparser
import logging as log
import time
from multiprocessing import Process, Queue

from parsers.csv_parser import parse
from persistance.sqlite_database import database_service
from scrappers.company_scrapper import company_scrapper
from search.playwrigth_search_url import search_service

log.basicConfig(format=f"%(asctime)s %(message)s", level=log.DEBUG)

CONFIG_FILE = "config.ini"


def get_config(config_file=CONFIG_FILE):
    """Loads a config file in the INI format from root folder.

    Arguments:
    config_file: string -- Filepath to the config INI file

    Returns: A ConfigParser object
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def run(filename):
    """Main application contrlller. Spaws processes to search form
    Linkedin profiles, scrap the profiles and persist the scrapped data
    into a sqlite database. This function also set ups all the queuing routes
    between processes.

    Arguments:
    filename: String -- String point to a file with company names to scrapp

    """
    config = get_config()
    database_name = config["persistance"].get("database", "companies.db")
    workers = int(config["scrappers"].get("workers", 1))

    linkedin_username = config["linkedin"].get("username")
    linkedin_password = config["linkedin"].get("password")
    if not linkedin_password or not linkedin_username:
        raise ValueError(
            "Please fill in the linkedin username and password at config.ini"
        )

    scrapp_queue = Queue()
    data_queue = Queue()
    database = Process(target=database_service, args=(data_queue, database_name))
    database.start()

    # Start linkedin profile search process
    companies = list(parse(filename))
    search_process = Process(
        target=search_service,
        args=(
            companies,
            scrapp_queue,
        ),
    )
    search_process.start()

    # Starting scrapper workers
    scrapper_configs = {"username": linkedin_username, "password": linkedin_password}
    scrapper_workers = [
        Process(
            target=company_scrapper,
            args=(scrapp_queue, data_queue, scrapper_configs),
        )
        for _ in range(workers)
    ]

    for worker in scrapper_workers:
        worker.start()

    search_process.join()

    # Waiting to last search result to flush into a worker before joining it
    time.sleep(5)

    # Blocking main proccess waiting workers to finish scrapping
    for worker in scrapper_workers:
        worker.terminate()
        worker.join()

    database.terminate()
    database.join()

    log.info("All done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Company scrapper",
        description="""
        Searches company Linkedin urls from the company name and scraps the company Linkedin profile. 
        Results are stored into a Sqlite3 database""",
    )
    parser.add_argument("filename")
    args = parser.parse_args()
    run(args.filename)
