import logging
import time
from behave import step
from selenium import webdriver

@step("I open a browser")
def step_impl(context, maximized=True):
    context.driver = webdriver.Chrome()
    if maximized:
        context.driver.maximize_window()


@step("I navigate to the Wikipedia page")
def step_impl(context):
    context.wikipedia_page = WikipediaPage(context.driver)
    logging.info("Navigating to the Wikipedia page")
    context.wikipedia_page.navigate()

@step("I log {text}")
def step_impl(context, text):
    logging.info(text)
    for i in range(20):
        logging.info("simulating logs {}...".format(i))


@step("I see in the page '{search_text}'")
def step_impl(context, search_text):
    logging.info("Searching for the text '{}'".format(search_text))
    context.wikipedia_page.search_for(search_text)
    time.sleep(1)
    
    
@step("the test fails")
def step_impl(context):
    assert False
