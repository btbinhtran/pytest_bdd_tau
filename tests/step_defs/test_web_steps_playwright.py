import inspect
from functools import wraps

import pytest, pytest_asyncio
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.async_api import async_playwright

DUCKDUCKGO_HOME = 'https://duckduckgo.com/'

scenarios('../features/web_playwright.feature')


def async_step(step):
    """Convert an async step function to a normal one."""

    signature = inspect.signature(step)
    parameters = list(signature.parameters.values())
    has_event_loop = any(parameter.name == "event_loop" for parameter in parameters)
    if not has_event_loop:
        parameters.append(
            inspect.Parameter("event_loop", inspect.Parameter.POSITIONAL_OR_KEYWORD)
        )
        step.__signature__ = signature.replace(parameters=parameters)

    @wraps(step)
    def run_step(*args, **kwargs):
        loop = kwargs["event_loop"] if has_event_loop else kwargs.pop("event_loop")
        return loop.run_until_complete(step(*args, **kwargs))

    return run_step


@pytest_asyncio.fixture()
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        yield browser
        await browser.close()


@pytest_asyncio.fixture()
async def context(browser):
    context = await browser.new_context()
    yield context
    await context.close()


@pytest_asyncio.fixture()
async def page(context):
    page = await context.new_page()
    yield page
    await page.close()


@given('the DuckDuckGo home page is displayed', target_fixture='ddg_home')
@async_step
async def ddg_home(page):
    await page.goto(DUCKDUCKGO_HOME)


@when(parsers.parse('the user searches for "{text}"'))
@when(parsers.parse('the user searches for the phrase:\n{text}'))
@async_step
async def search_phrase(page, text):
    await page.fill('input[name="q"]', text)
    await page.press('input[name="q"]', 'Enter')


@then(parsers.parse('one of the results contains "{phrase}"'))
@async_step
async def results_have_one(page, phrase):
    xpath = "//*[@data-testid='result']//*[contains(text(), '%s')]" % phrase
    await page.wait_for_selector(xpath)

    assert len(await page.query_selector_all(xpath)) > 1


@then(parsers.parse('results are shown for "{phrase}"'))
@async_step
async def search_results(page, phrase):
    # Check search result list
    # (A more comprehensive test would check results for matching phrases)
    # (Check the list before the search phrase for correct implicit waiting)
    results_css_selector = '[data-testid="result"]'

    await page.wait_for_selector(results_css_selector)

    assert len(await page.query_selector_all(results_css_selector)) > 0
    # Check search phrase
    search_input = await page.wait_for_selector('input[name="q"]')
    assert await search_input.get_attribute('value') == phrase
