import logging as log
import os
import queue
import signal
from multiprocessing import Queue

from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

from models.company import Company
from utils.runtime_state import RuntimeState


def sanitize(value):
    """Cleans the scrapped field strings"""
    return value.replace("/n", "").strip()


def scrapp_page(page):
    """Collect data from the loaded Linkedin page

    Arguments:
    page: playwright.Page -- Page to scrap

    returns: Company instance
    """
    company_name = page.locator(".org-top-card-summary__title").text_content()
    args = [company_name, page.url]
    summary_items = page.locator(".org-top-card-summary-info-list__info-item").all()
    for item in summary_items:
        args.append(sanitize(item.text_content()))
    return Company(*args)


def sign_in(page, username, password):
    """ Perforn the page login if the login modal is present in the page

    Arguments:
    username: string -- Linkedin username
    password: string -- Linkedin password
    page: playwright.Page -- Loaded page
    """
    sign_in_button = page.get_by_role("button", name="Sign in")
    if sign_in_button.count() > 0:
        pid = os.getpid()
        sign_in_button.click()
        sign_in_button = page.locator(
            'xpath=//*[@id="organization_guest_contextual-sign-in_sign-in-modal"]/div/section/div/div/form/div[2]/button'
        )
        page.locator(
            'xpath=//*[@id="organization_guest_contextual-sign-in_sign-in-modal_session_password"]'
        ).fill(password)
        page.locator(
            'xpath=//*[@id="organization_guest_contextual-sign-in_sign-in-modal_session_key"]'
        ).fill(username)
        sign_in_button.click()
        page.wait_for_load_state("load")
        log.info(f"[pid={pid}] Worker logged in")


def company_scrapper(input_q: Queue, out_q: Queue, creadentials: dict):
    """Execute the main scrapper loop navigating to companies pages 
    and pushing collected company data forward
    
    Arguments:
    input_q: Queue -- Queue of companies urls
    out_q: Queue -- Queue to put collected data to
    creadentials: dict -- Linkedin creadentials

    """
    pid = os.getpid()
    log.info(f"[pid={pid}] ScrapperService start")

    username = creadentials.get("username")
    password = creadentials.get("password")

    runtime = RuntimeState()
    signal.signal(signal.SIGTERM, runtime.handle_signal)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        stealth_sync(page)
        log.info(f"[pid={pid}] ScrapperService browser started")

        while True:
            try:
                target = input_q.get(timeout=1)
                log.info(f"[pid={pid}] ScrapperService scrapping page={target}")
            except queue.Empty:
                target = None

            if target is None:
                if not runtime.is_running():
                    break
                continue

            page.goto(target)
            page.wait_for_load_state("load")
            sign_in(page, username=username, password=password)
            company = scrapp_page(page)
            out_q.put(company)
            log.info(f"[pid={pid}] ScrapperService Finish scrapping page={target}")

        browser.close()
    log.info(f"[pid={pid}] ScrapperService No mode pages to scrapp")
    return 0
