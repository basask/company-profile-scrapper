import logging as log
from multiprocessing import Queue

from googlesearch import search as gsearch


def get_company_linkedin_url(company_name):
    """Perform a google search targeting resulst to linkedin.com
    Narowing this search to linkedin.com only can get results with less noise
    """
    search_string = f"site:linkedin.com {company_name}"
    search_results = gsearch(search_string, num_results=5, sleep_interval=2, lang="en")
    return search_results


def search_service(companies: list, result_q: Queue):
    for company_name in companies:
        result = get_company_linkedin_url(company_name)
        company = next(result)
        log.info(f"CompanySearch - {company_name}")
        result_q.put(company)
