"""
This module contains step definitions for web_selenium.feature.
It uses Selenium WebDriver for browser interactions:
https://www.seleniumhq.org/projects/webdriver/
Setup and cleanup are handled using hooks.
For a real test automation project,
use Page Object Model or Screenplay Pattern to model web interactions.

Prerequisites:
 - Firefox must be installed.
 - geckodriver must be installed and accessible on the system path.
"""
import pytest
from pytest_bdd import scenarios, when, then, parsers, given
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


DUCKDUCKGO_HOME = 'https://duckduckgo.com/'

scenarios('../features/web_selenium.feature')


@pytest.fixture
def browser():
    # A better practice would be to get browser choice from a config file.
    b = webdriver.Firefox()
    b.implicitly_wait(10)
    yield b
    b.quit()

@given('the DuckDuckGo home page is displayed', target_fixture='ddg_home')
def ddg_home(browser):
    browser.get(DUCKDUCKGO_HOME)

@when(parsers.parse('the user searches for "{text}"'))
@when(parsers.parse('the user searches for the phrase:\n{text}'))
def search_phrase(browser, text):
    search_input = browser.find_element(By.NAME, 'q')
    search_input.send_keys(text + Keys.RETURN)


@then(parsers.parse('one of the results contains "{phrase}"'))
def results_have_one(browser, phrase):
    xpath = "//*[@data-testid='result']//*[contains(text(), '%s')]" % phrase
    results = browser.find_elements(By.XPATH, xpath)
    assert len(results) > 0


@then(parsers.parse('results are shown for "{phrase}"'))
def search_results(browser, phrase):
    # Check search result list
    # (A more comprehensive test would check results for matching phrases)
    # (Check the list before the search phrase for correct implicit waiting)
    assert len(browser.find_elements(By.CSS_SELECTOR, '[data-testid="result"]')) > 0
    # Check search phrase
    search_input = browser.find_element(By.NAME, 'q')
    assert search_input.get_attribute('value') == phrase
