import logging as log
import os
from multiprocessing import Queue

from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync


def get_company_linkedin_url(page, company_name):
    """Perform a google search targeting resulst to linkedin.com
    Narowing this search to linkedin.com only can get results with less noise
    """
    company_name_encoded = company_name.replace(" ", "+")
    page.goto(
        f"https://www.google.com/search?q=site%3Alinkedin.com+lang%3Aen+{company_name_encoded}"
    )
    page.wait_for_load_state("load")

    links = page.locator("a[href]").all()
    for link in links:
        href = link.get_attribute("href")
        if "linkedin.com/company/" in href:
            return href


def search_service(companies: list, result_q: Queue):
    pid = os.getpid()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        stealth_sync(page)

        for company_name in companies:
            result = get_company_linkedin_url(page, company_name)
            result_q.put(result)
            log.info(f"[pid={pid}] CompanySearch company={company_name} url={result}")

        log.info(f"[pid={pid}] CompanySearch finish searching companies urls")
        browser.close()
