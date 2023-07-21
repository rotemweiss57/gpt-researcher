"""Selenium web scraping module."""
from __future__ import annotations
import os
import logging
import asyncio
from pathlib import Path
from sys import platform
from seleniumbase import BaseCase
from seleniumbase import config as sb_config
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from fastapi import WebSocket


import processing.text as summary

from config import Config
from processing.html import extract_hyperlinks, format_hyperlinks

from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

FILE_DIR = Path(__file__).parent.parent
CFG = Config()


async def async_browse(url: str, question: str, websocket: WebSocket) -> str:
    """Browse a website and return the answer and links to the user

    Args:
        url (str): The url of the website to browse
        question (str): The question asked by the user
        websocket (WebSocketManager): The websocket manager

    Returns:
        str: The answer and links to the user
    """
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=8)

    print(f"Scraping url {url} with question {question}")
    await websocket.send_json(
        {"type": "logs", "output": f"🔎 Browsing the {url} for relevant about: {question}..."})

    try:
        driver, text = await loop.run_in_executor(executor, scrape_text_with_selenium, url)
        await loop.run_in_executor(executor, add_header, driver)
        summary_text = await loop.run_in_executor(executor, summary.summarize_text, url, text, question, driver)

        await websocket.send_json(
            {"type": "logs", "output": f"📝 Information gathered from url {url}: {summary_text}"})

        return f"Information gathered from url {url}: {summary_text}"
    except Exception as e:
        print(f"An error occurred while processing the url {url}: {e}")
        return f"Error processing the url {url}: {e}"



def browse_website(url: str, question: str) -> tuple[str, WebDriver]:
    """Browse a website and return the answer and links to the user

    Args:
        url (str): The url of the website to browse
        question (str): The question asked by the user

    Returns:
        Tuple[str, WebDriver]: The answer and links to the user and the webdriver
    """

    if not url:
        return "A URL was not specified, cancelling request to browse website.", None

    driver, text = scrape_text_with_selenium(url)
    add_header(driver)
    summary_text = summary.summarize_text(url, text, question, driver)

    links = scrape_links_with_selenium(driver, url)

    # Limit links to 5
    if len(links) > 5:
        links = links[:5]

    # write_to_file('research-{0}.txt'.format(url), summary_text + "\nSource Links: {0}\n\n".format(links))

    close_browser(driver)
    return f"Answer gathered from website: {summary_text} \n \n Links: {links}", driver


def scrape_text_with_selenium(self, url: str) -> tuple:
    """Scrape text from a website using SeleniumBase

    Args:
        url (str): The URL of the website to scrape

    Returns:
        Tuple[WebDriver, str]: The WebDriver and the text scraped from the website
    """
    # Set the user agent for the test
    sb_config.update({"user_agent": "Your User Agent"})

    # Set the ChromeDriver executable path
    chromedriver_path = "/usr/bin/chromedriver"

    if not os.path.exists(chromedriver_path):
        # Download the ChromeDriver if it doesn't exist
        os.system(
            "wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/115.0.5790.98/linux64/chromedriver-linux64.zip -O /tmp/chromedriver-linux64.zip"
        )
        os.system("unzip -o /tmp/chromedriver-linux64.zip -d /tmp/")
        os.system(f"sudo mv -f /tmp/chromedriver /usr/bin/chromedriver")

    # Chrome options and service configuration
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={sb_config.user_agent}")
    options.add_experimental_option("prefs", {"download_restrictions": 3})
    service = Service(executable_path=chromedriver_path)

    # Create the WebDriver
    self.create_driver(options=options, service=service)
    self.driver.get(url)

    # Print Chrome version
    print("Chrome version:", self.driver.capabilities["version"])

    # Print ChromeDriver version
    with os.popen("chromedriver --version") as f:
        chromedriver_version = f.read().strip()
    print("ChromeDriver version:", chromedriver_version)

    WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Get the HTML content directly from the browser's DOM
    page_source = self.driver.execute_script("return document.body.outerHTML;")
    soup = BeautifulSoup(page_source, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = self.get_text(soup)

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)

    return self.driver, text

def get_text(soup):
    """Get the text from the soup

    Args:
        soup (BeautifulSoup): The soup to get the text from

    Returns:
        str: The text from the soup
    """
    text = ""
    tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'p']
    for element in soup.find_all(tags):  # Find all the <p> elements
        text += element.text + "\n\n"
    return text


def scrape_links_with_selenium(driver: WebDriver, url: str) -> list[str]:
    """Scrape links from a website using selenium

    Args:
        driver (WebDriver): The webdriver to use to scrape the links

    Returns:
        List[str]: The links scraped from the website
    """
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    hyperlinks = extract_hyperlinks(soup, url)

    return format_hyperlinks(hyperlinks)


def close_browser(driver: WebDriver) -> None:
    """Close the browser

    Args:
        driver (WebDriver): The webdriver to close

    Returns:
        None
    """
    driver.quit()


def add_header(driver: WebDriver) -> None:
    """Add a header to the website

    Args:
        driver (WebDriver): The webdriver to use to add the header

    Returns:
        None
    """
    driver.execute_script(open(f"{FILE_DIR}/js/overlay.js", "r").read())
